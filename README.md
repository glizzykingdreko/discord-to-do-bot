# Discord To Do Bot

![Banner](./assets/banner.png)

A flexible Discord bot that adds/removes custom emojis to channel names using the `/mark` command.

📖 Read the full article: [How I Track Support Tickets With a Simple Channel Marker Bot](https://medium.com/@glizzykingdreko/how-i-track-support-tickets-with-a-simple-channel-marker-bot-8a92b41f54c1)

## Table of Contents
- [Use Cases](#use-cases)
  - [Support Ticket Management](#support-ticket-management-)
  - [Other Use Cases](#other-use-cases)
    - [Project Management](#project-management-)
    - [Event Organization](#event-organization-)
    - [Community Management](#community-management-)
    - [Server Organization](#server-organization-)
- [Features](#features)
- [Inviting the Bot](#inviting-the-bot)
- [Setup](#setup)
- [Commands](#commands)
- [Rate Limits](#rate-limits)
- [Permission System](#permission-system)
- [Requirements](#requirements)
- [Contact](#contact)

## Use Cases

### Support Ticket Management 🎫
Originally developed to improve support ticket management in Discord servers. The bot helps track:
- Unanswered tickets that need attention
- Tickets requiring follow-up
- Tickets pending customer response
- High-priority issues

Example workflow:
1. New ticket created: `ticket-123456`
2. Need to follow up later: `/mark` → `🟣-ticket-123456`
3. Issue resolved: `/mark` → `ticket-123456`

This makes it easy to:
- Quickly identify which tickets need attention
- Keep track of pending follow-ups
- Maintain a clear overview of ticket status

### Other Use Cases

#### Project Management 📊
- Mark channels that need updates
- Highlight channels with pending tasks
- Track channels requiring review
- Flag important announcements

#### Event Organization 📅
- Mark channels for ongoing events
- Highlight channels needing preparation
- Track post-event cleanup channels
- Flag channels for important updates

#### Community Management 👥
- Mark channels needing moderation
- Highlight channels with active discussions
- Track channels requiring content updates
- Flag channels for rule reviews

#### Server Organization 🗂
- Mark channels under construction
- Highlight temporary channels
- Track archived/inactive channels
- Flag channels for reorganization

## Features

- `/mark` command to toggle emoji in channel names
- `/checkmark` command to check when a channel can be marked again
- Smart rate limit handling with cooldown tracking
- Customizable emoji through environment variables or `/setemoji` command
- Role and user-based permission system
- Admin-only mode option
- `/markinfo` command to view current settings
- Works in any text channel

## Rate Limits

Due to Discord's API limitations, channel names can only be modified twice every 10 minutes. The bot handles this by:
- Tracking modification times for each channel
- Providing clear feedback on when channels can be modified again
- Offering the `/checkmark` command to check cooldown status

## Inviting the Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications/)
2. Select your application
3. Go to the "OAuth2" section in the left sidebar
4. Select "URL Generator" under "OAuth2"
5. In "Scopes", select:
   - `bot`
   - `applications.commands`
6. In "Bot Permissions", select:
   - `Manage Channels` (Required for editing channel names)
   - `Send Messages`
   - `Use Slash Commands`
7. Copy the generated URL at the bottom
8. Open the URL in a browser to invite the bot to your server
   - You need "Manage Server" permission in the Discord server to add bots

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Enable Privileged Intents:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications/)
   - Select your application
   - Go to the "Bot" section
   - Enable "Message Content Intent" under "Privileged Gateway Intents"
   - Save changes

5. Edit `.env` with your configuration:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `MARK_EMOJI`: The emoji to use (default: 🟣)
   - `ALLOWED_ROLE_IDS`: Comma-separated list of role IDs that can use the command
   - `ALLOWED_USER_IDS`: Comma-separated list of user IDs that can use the command
   - `ADMIN_ONLY`: Set to "true" to allow only server administrators to use the command

6. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

- `/mark` - Toggle the emoji in the current channel's name
- `/setemoji <emoji>` - Set a custom emoji for the mark command (Admin only)
- `/markinfo` - Show current mark command settings (Admin only)
- `/help` - Display help information for all commands

## Permission System

The bot supports multiple ways to control who can use the `/mark` command:

1. **Admin Only Mode**: When enabled, only server administrators can use the command
2. **Role-based**: Users with specific roles can use the command
3. **User-based**: Specific users can use the command

You can configure these in the `.env` file or use the `/markinfo` command to view current settings.

## Requirements

- Python 3.8 or higher
- discord.py
- python-dotenv 

## Contact

For any inquiries or further information, please reach out:

- Project Maintainer: [glizzykingdreko](mailto:glizzykingdreko@protonmail.com)
- Twitter: [@glizzykingdreko](https://twitter.com/glizzykingdreko)
- You like my projects? [Buy me a coffee](https://www.buymeacoffee.com/glizzykingdreko) 