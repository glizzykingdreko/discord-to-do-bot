import os
import discord
import logging
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv, set_key
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# Load environment variables
load_dotenv()

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration
GITHUB_LINK = "https://github.com/glizzykingdreko/discord-to-do-tickets"
COMMANDS_CONFIG = config['commands']
ADMIN_ONLY = os.getenv('ADMIN_ONLY', 'false').lower() == 'true'
ALLOWED_ROLE_IDS = [int(role_id) for role_id in os.getenv('ALLOWED_ROLE_IDS', '').split(',') if role_id]
ALLOWED_USER_IDS = [int(user_id) for user_id in os.getenv('ALLOWED_USER_IDS', '').split(',') if user_id]

# Channel modification tracking
channel_last_modified: Dict[int, datetime] = {}
channel_locks: Dict[int, asyncio.Lock] = {}
CHANNEL_COOLDOWN = 600  # 10 minutes in seconds

def can_modify_channel(channel_id: int) -> tuple[bool, float]:
    """Check if a channel can be modified and return remaining cooldown."""
    if channel_id not in channel_last_modified:
        return True, 0
    
    now = datetime.now()
    last_modified = channel_last_modified[channel_id]
    cooldown_end = last_modified + timedelta(seconds=CHANNEL_COOLDOWN)
    
    if now >= cooldown_end:
        return True, 0
    else:
        return False, (cooldown_end - now).total_seconds()

def update_channel_modified(channel_id: int):
    """Update the last modification time for a channel."""
    channel_last_modified[channel_id] = datetime.now()

def update_config_emoji(command_name: str, new_emoji: str):
    """Update the emoji in config.yaml file"""
    try:
        config['commands'][command_name]['emoji'] = new_emoji
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f)
        logger.info(f"Updated emoji for {command_name} in config.yaml to {new_emoji}")
    except Exception as e:
        logger.error(f"Failed to update config.yaml file: {e}")

async def create_mark_command(cmd_name: str, emoji: str, description: str):
    """Create a dynamic mark command"""
    
    @bot.tree.command(name=cmd_name, description=description)
    async def dynamic_mark(interaction: discord.Interaction):
        try:
            if not isinstance(interaction.channel, discord.TextChannel):
                await interaction.response.send_message(
                    "This command can only be used in text channels!", 
                    ephemeral=True,
                    delete_after=5
                )
                return

            channel = interaction.channel
            current_name = channel.name

            # Determine new name
            if current_name.startswith(f"{emoji}-"):
                new_name = current_name[len(emoji) + 1:]
                action = "removed"
            else:
                new_name = f"{emoji}-{current_name}"
                action = "added"

            await interaction.response.defer(ephemeral=True)
            
            try:
                await channel.edit(name=new_name)
                update_channel_modified(channel.id)
                logger.info(f"{cmd_name.capitalize()} emoji {action} in channel {channel.name} by {interaction.user.name}")
                await interaction.followup.send(
                    f"Successfully {action} the {cmd_name} marker!", 
                    ephemeral=True,
                    delete_after=3
                )
            except discord.errors.HTTPException as e:
                if e.code == 429:
                    retry_after = e.retry_after
                    minutes = int(retry_after // 60)
                    seconds = int(retry_after % 60)
                    time_msg = f"{minutes} minutes and {seconds} seconds" if minutes > 0 else f"{seconds} seconds"
                    await interaction.followup.send(
                        f"⚠️ This channel was edited too recently. Please wait {time_msg} before trying again.\n"
                        "Use `/checkmark` to check when you can modify this channel.",
                        ephemeral=True,
                        delete_after=10
                    )
                else:
                    raise e
        except discord.Forbidden:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "I don't have permission to edit this channel!", 
                    ephemeral=True,
                    delete_after=5
                )
            else:
                await interaction.followup.send(
                    "I don't have permission to edit this channel!", 
                    ephemeral=True,
                    delete_after=5
                )
        except Exception as e:
            logger.error(f"Error in {cmd_name} command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"An error occurred: {str(e)}", 
                    ephemeral=True,
                    delete_after=5
                )
            else:
                await interaction.followup.send(
                    f"An error occurred: {str(e)}", 
                    ephemeral=True,
                    delete_after=5
                )

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    try:
        # Set bot's presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="being opensource!"
        )
        await bot.change_presence(activity=activity, status=discord.Status.online)
        
        # Create dynamic commands from config
        for cmd_name, cmd_config in COMMANDS_CONFIG.items():
            await create_mark_command(
                cmd_config['command_name'],
                cmd_config['emoji'],
                cmd_config['description']
            )
        
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@bot.tree.command(name="help", description="Show information about available commands")
async def help(interaction: discord.Interaction):
    """Show help information for all commands"""
    embed = discord.Embed(
        title="Channel Marker Bot Help",
        description=(
            "A bot that helps manage channel markers with emojis\n\n"
            f"🔗 [View Source Code]({GITHUB_LINK})"
        ),
        color=discord.Color.blue()
    )
    
    # Add available mark commands
    embed.add_field(
        name="Available Markers",
        value="\n".join([
            f"• `/{cmd['command_name']}` - {cmd['emoji']} {cmd['description']}"
            for cmd in COMMANDS_CONFIG.values()
        ]),
        inline=False
    )
    
    # Add utility commands
    embed.add_field(
        name="Utility Commands",
        value=(
            "• `/checkmark` - Check when a channel can be marked again\n"
            "• `/help` - Show this help message"
        ),
        inline=False
    )
    
    # Add admin commands if user is administrator
    if interaction.user.guild_permissions.administrator:
        embed.add_field(
            name="Admin Commands",
            value="• `/setemoji <command> <emoji>` - Change the emoji for a specific command",
            inline=False
        )
    
    embed.set_footer(text="Created by GlizzyKingDreko")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setemoji", description="Set a custom emoji for a specific command")
async def setemoji(interaction: discord.Interaction, command: str, emoji: str):
    """Set a custom emoji for the specified command (Admin only)"""
    try:
        if command not in COMMANDS_CONFIG:
            await interaction.response.send_message(
                f"Unknown command: {command}. Available commands: {', '.join(COMMANDS_CONFIG.keys())}", 
                ephemeral=True,
                delete_after=5
            )
            return
            
        old_emoji = COMMANDS_CONFIG[command]['emoji']
        COMMANDS_CONFIG[command]['emoji'] = emoji
        
        # Update the config file
        update_config_emoji(command, emoji)
        
        logger.info(f"Emoji for {command} changed from {old_emoji} to {emoji} by {interaction.user.name}")
        await interaction.response.send_message(
            f"Successfully set the {command} emoji to: {emoji}\n"
            "Note: This will only affect new marks, existing marked channels will keep the old emoji.\n"
            "The new emoji has been saved and will persist after bot restart.",
            ephemeral=True,
            delete_after=5
        )
    except Exception as e:
        logger.error(f"Error in setemoji command: {str(e)}")
        await interaction.response.send_message(
            f"An error occurred: {str(e)}", 
            ephemeral=True,
            delete_after=5
        )

@bot.tree.command(name="checkmark", description="Check when a channel can be marked again")
async def checkmark(interaction: discord.Interaction):
    """Check when the current channel can be modified again"""
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "This command can only be used in text channels!", 
            ephemeral=True,
            delete_after=5
        )
        return

    can_modify, cooldown = can_modify_channel(interaction.channel.id)
    
    if can_modify:
        await interaction.response.send_message(
            "✅ This channel can be marked now!", 
            ephemeral=True,
            delete_after=3
        )
    else:
        minutes = int(cooldown // 60)
        seconds = int(cooldown % 60)
        time_msg = f"{minutes} minutes and {seconds} seconds" if minutes > 0 else f"{seconds} seconds"
        await interaction.response.send_message(
            f"⏳ This channel can be marked again in {time_msg}",
            ephemeral=True,
            delete_after=5
        )

@bot.tree.command(name="sync", description="Force sync commands (Admin only)")
async def sync(interaction: discord.Interaction):
    """Force sync commands (Admin only)"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You need administrator permissions to use this command!",
            ephemeral=True,
            delete_after=5
        )
        return

    try:
        # Create dynamic commands from config
        for cmd_name, cmd_config in COMMANDS_CONFIG.items():
            await create_mark_command(
                cmd_config['command_name'],
                cmd_config['emoji'],
                cmd_config['description']
            )
        
        synced = await bot.tree.sync()
        logger.info(f"Force synced {len(synced)} command(s)")
        await interaction.response.send_message(
            f"Successfully synced {len(synced)} commands!",
            ephemeral=True,
            delete_after=5
        )
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
        await interaction.response.send_message(
            f"Failed to sync commands: {str(e)}",
            ephemeral=True,
            delete_after=5
        )

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 