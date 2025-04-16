import os
import discord
import logging
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv, set_key
from typing import Optional, Dict
from datetime import datetime, timedelta
import asyncio

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

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration
MARK_EMOJI = os.getenv('MARK_EMOJI', '🟣')
ALLOWED_ROLE_IDS = [int(role_id) for role_id in os.getenv('ALLOWED_ROLE_IDS', '').split(',') if role_id]
ALLOWED_USER_IDS = [int(user_id) for user_id in os.getenv('ALLOWED_USER_IDS', '').split(',') if user_id]
ADMIN_ONLY = os.getenv('ADMIN_ONLY', 'false').lower() == 'true'
GITHUB_LINK = "https://github.com/glizzykingdreko/discord-to-do-tickets"

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

def update_env_emoji(new_emoji: str):
    """Update the MARK_EMOJI in .env file"""
    try:
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        set_key(dotenv_path, 'MARK_EMOJI', new_emoji)
        logger.info(f"Updated MARK_EMOJI in .env to {new_emoji}")
    except Exception as e:
        logger.error(f"Failed to update .env file: {e}")

async def safe_channel_edit(channel: discord.TextChannel, new_name: str) -> tuple[bool, str, Optional[float]]:
    """
    Safely edit a channel name with rate limit handling.
    Returns: (success, message, retry_after)
    """
    # Get or create lock for this channel
    lock = channel_locks.setdefault(channel.id, asyncio.Lock())
    
    # Check if name actually needs to change
    if new_name == channel.name:
        return True, "Channel name is already in desired state.", None
    
    async with lock:
        try:
            # Check cooldown under lock to prevent race conditions
            can_modify, cooldown = can_modify_channel(channel.id)
            if not can_modify:
                minutes = int(cooldown // 60)
                seconds = int(cooldown % 60)
                time_msg = f"{minutes} minutes and {seconds} seconds" if minutes > 0 else f"{seconds} seconds"
                return False, f"Channel was modified too recently. Please wait {time_msg}.", cooldown
            
            # Attempt the edit
            await channel.edit(name=new_name)
            update_channel_modified(channel.id)
            return True, "Successfully modified channel name.", None
            
        except discord.errors.HTTPException as e:
            if e.code == 429:  # Rate limit error
                return False, "Rate limit reached.", e.retry_after
            raise e

async def update_bot_avatar():
    """Update the bot's avatar if it hasn't been set"""
    try:
        profile_path = os.path.join(os.path.dirname(__file__), 'assets', 'profile_picture.png')
        if not os.path.exists(profile_path):
            logger.warning("Profile picture not found in assets folder")
            return
            
        # Read the image file
        with open(profile_path, 'rb') as image:
            avatar_data = image.read()
            
        # Check if we need to update the avatar
        current_avatar = str(bot.user.avatar) if bot.user.avatar else None
        if not current_avatar:
            await bot.user.edit(avatar=avatar_data)
            logger.info("Updated bot's profile picture")
    except Exception as e:
        logger.error(f"Failed to update bot's avatar: {e}")

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    try:
        # Update bot's avatar if needed
        await update_bot_avatar()
        
        # Set bot's presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="being opensource!"
        )
        await bot.change_presence(activity=activity, status=discord.Status.online)
        
        # Create default permissions for commands
        mark_command = bot.tree.get_command("mark")
        setemoji_command = bot.tree.get_command("setemoji")
        markinfo_command = bot.tree.get_command("markinfo")
        help_command = bot.tree.get_command("help")
        checkmark_command = bot.tree.get_command("checkmark")
        about_command = bot.tree.get_command("about")

        # Set default permissions for each command
        mark_perms = {}
        admin_perms = {}
        everyone_perms = {"send_messages": True}  # Basic permission that everyone typically has
        
        # If admin only mode is enabled, restrict to administrators
        if ADMIN_ONLY:
            mark_perms["administrator"] = True
        else:
            # Add allowed roles if any
            for role_id in ALLOWED_ROLE_IDS:
                mark_perms[f"role:{role_id}"] = True
            
            # Add allowed users if any
            for user_id in ALLOWED_USER_IDS:
                mark_perms[f"user:{user_id}"] = True
        
        # Admin commands always require administrator permission
        admin_perms["administrator"] = True
        
        # Update command permissions
        if mark_command:
            mark_command.default_permissions = discord.Permissions(**mark_perms)
        if setemoji_command:
            setemoji_command.default_permissions = discord.Permissions(**admin_perms)
        if markinfo_command:
            markinfo_command.default_permissions = discord.Permissions(**admin_perms)
        if help_command:
            help_command.default_permissions = discord.Permissions(**everyone_perms)
        if checkmark_command:
            checkmark_command.default_permissions = discord.Permissions(**everyone_perms)
        if about_command:
            about_command.default_permissions = discord.Permissions(**everyone_perms)
        
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@bot.tree.command(name="about", description="Show information about the bot and its source code")
@app_commands.guilds()  # Make it available in servers
async def about(interaction: discord.Interaction):
    """Show information about the bot and its source code"""
    embed = discord.Embed(
        title="About Discord To-Do Bot",
        description=(
            "I'm a bot that helps manage channel markers with emojis.\n\n"
            "📖 **Source Code**\n"
            f"This bot is open source! Check out the [GitHub Repository]({GITHUB_LINK})\n\n"
            "🌟 **Features**\n"
            "• Mark channels with custom emojis\n"
            "• Role-based permissions\n"
            "• Admin controls\n"
            "• Rate limit handling"
        ),
        color=discord.Color.blue(),
        url=GITHUB_LINK  # Makes the title clickable too
    )
    embed.set_footer(text="Created by GlizzyKingDreko")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show help information for all commands")
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
    
    # Only show commands the user has access to
    commands_info = {
        "help": "Show this help message",
        "checkmark": "Check when a channel can be marked again"
    }
    
    # Add mark command if user has permission
    if ADMIN_ONLY and interaction.user.guild_permissions.administrator:
        commands_info["mark"] = "Toggle emoji in the current channel's name"
    elif not ADMIN_ONLY and (
        any(role.id in ALLOWED_ROLE_IDS for role in interaction.user.roles) or
        interaction.user.id in ALLOWED_USER_IDS
    ):
        commands_info["mark"] = "Toggle emoji in the current channel's name"
    
    # Add admin commands if user is administrator
    if interaction.user.guild_permissions.administrator:
        commands_info.update({
            "setemoji": "Set a custom emoji for the mark command (Admin only)",
            "markinfo": "Show current mark command settings (Admin only)"
        })
    
    for cmd, desc in commands_info.items():
        embed.add_field(name=f"/{cmd}", value=desc, inline=False)
    
    embed.set_footer(text="Bot is open source! Check out the GitHub repository for more info.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="mark", description="Toggle emoji in channel name")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.channel.id))  # Basic cooldown to prevent spam
async def mark(interaction: discord.Interaction):
    try:
        # Check if the command is used in a channel
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("This command can only be used in text channels!", ephemeral=True)
            return

        channel = interaction.channel
        current_name = channel.name

        # Determine new name
        if current_name.startswith(f"{MARK_EMOJI}-"):  # Check for emoji with hyphen
            new_name = current_name[len(MARK_EMOJI) + 1:]  # +1 for the hyphen
            action = "removed"
        else:
            new_name = f"{MARK_EMOJI}-{current_name}"
            action = "added"

        # Defer response since we might need to wait
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Attempt the edit
            await channel.edit(name=new_name)
            update_channel_modified(channel.id)
            logger.info(f"Emoji {action} in channel {channel.name} by {interaction.user.name}")
            await interaction.followup.send(f"Successfully {action} the emoji!", ephemeral=True)
        except discord.errors.HTTPException as e:
            if e.code == 429:  # Rate limit error
                retry_after = e.retry_after
                minutes = int(retry_after // 60)
                seconds = int(retry_after % 60)
                time_msg = f"{minutes} minutes and {seconds} seconds" if minutes > 0 else f"{seconds} seconds"
                await interaction.followup.send(
                    f"⚠️ This channel was edited too recently. Please wait {time_msg} before trying again.\n"
                    "Use `/checkmark` to check when you can modify this channel.",
                    ephemeral=True
                )
            else:
                raise e
                
    except discord.Forbidden:
        if not interaction.response.is_done():
            await interaction.response.send_message("I don't have permission to edit this channel!", ephemeral=True)
        else:
            await interaction.followup.send("I don't have permission to edit this channel!", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in mark command: {str(e)}")
        if not interaction.response.is_done():
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

@bot.tree.command(name="setemoji", description="Set a custom emoji for the mark command")
async def setemoji(interaction: discord.Interaction, emoji: str):
    """Set a custom emoji for the mark command (Admin only)"""
    try:
        global MARK_EMOJI
        old_emoji = MARK_EMOJI
        MARK_EMOJI = emoji
        
        # Update the .env file
        update_env_emoji(emoji)
        
        logger.info(f"Emoji changed from {old_emoji} to {emoji} by {interaction.user.name}")
        await interaction.response.send_message(
            f"Successfully set the mark emoji to: {emoji}\n"
            "Note: This will only affect new marks, existing marked channels will keep the old emoji.\n"
            "The new emoji has been saved and will persist after bot restart.",
            ephemeral=True
        )
    except Exception as e:
        logger.error(f"Error in setemoji command: {str(e)}")
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@bot.tree.command(name="markinfo", description="Show current mark command settings")
async def markinfo(interaction: discord.Interaction):
    """Show current mark command settings (Admin only)"""
    embed = discord.Embed(title="Mark Command Settings", color=discord.Color.blue())
    embed.add_field(name="Current Emoji", value=MARK_EMOJI, inline=False)
    embed.add_field(name="Admin Only Mode", value="Enabled" if ADMIN_ONLY else "Disabled", inline=False)
    
    if ALLOWED_ROLE_IDS:
        roles = [f"<@&{role_id}>" for role_id in ALLOWED_ROLE_IDS]
        embed.add_field(name="Allowed Roles", value=", ".join(roles) if roles else "None", inline=False)
    
    if ALLOWED_USER_IDS:
        users = [f"<@{user_id}>" for user_id in ALLOWED_USER_IDS]
        embed.add_field(name="Allowed Users", value=", ".join(users) if users else "None", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="checkmark", description="Check when a channel can be marked again")
async def checkmark(interaction: discord.Interaction):
    """Check when the current channel can be modified again"""
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("This command can only be used in text channels!", ephemeral=True)
        return

    can_modify, cooldown = can_modify_channel(interaction.channel.id)
    
    if can_modify:
        await interaction.response.send_message("✅ This channel can be marked now!", ephemeral=True)
    else:
        minutes = int(cooldown // 60)
        seconds = int(cooldown % 60)
        time_msg = f"{minutes} minutes and {seconds} seconds" if minutes > 0 else f"{seconds} seconds"
        await interaction.response.send_message(
            f"⏳ This channel can be marked again in {time_msg}",
            ephemeral=True
        )

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"This command is on cooldown. Please try again in {error.retry_after:.1f} seconds.",
            ephemeral=True
        )
    else:
        logger.error(f"Command error: {str(error)}")
        await interaction.response.send_message(
            "An error occurred while processing the command.",
            ephemeral=True
        )

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 