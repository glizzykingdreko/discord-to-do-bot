# Discord To-Do Bot

A Discord bot that helps manage channel markers with emojis. Perfect for tracking support tickets, project tasks, or any other channel-based organization needs.

📖 Read the full article: [How I Track Support Tickets With a Simple Channel Marker Bot](https://medium.com/@glizzykingdreko/how-i-track-support-tickets-with-a-simple-channel-marker-bot-8a92b41f54c1)

## Table of Contents
- [Use Cases](#use-cases)
  - [Support Ticket Management](#support-ticket-management)
  - [Other Use Cases](#other-use-cases)
    - [Project Management](#project-management)
    - [Event Organization](#event-organization)
    - [Community Management](#community-management)
    - [Server Organization](#server-organization)
- [Features](#features)
- [Inviting the Bot](#inviting-the-bot)
- [Setup](#setup)
- [Commands](#commands)
- [Rate Limits](#rate-limits)
- [Permission System](#permission-system)
- [Requirements](#requirements)
- [2.0 Update](#20-update)
- [Contact](#contact)

## Use Cases

### Support Ticket Management
This bot was originally developed to improve support ticket management in Discord servers. It helps track:
- Unanswered tickets
- Tickets waiting for follow-up
- High-priority issues
- Completed tickets

Example workflow:
1. User creates a support ticket channel
2. Support team marks it with 🟣 (to-do)
3. When waiting for user response, mark with ⌛
4. For urgent issues, mark with 🔴
5. Once resolved, mark with ✅

### Additional Use Cases

#### Project Management
- Track task progress
- Mark priority levels
- Indicate review needed
- Show completion status

#### Event Organization
- Track event planning stages
- Mark deadlines
- Show preparation status
- Indicate follow-up needed

#### Community Management
- Track moderation actions
- Mark channels for review
- Show maintenance status
- Indicate special handling

#### Server Organization
- Categorize channels
- Show update status
- Mark temporary channels
- Indicate special purposes

## Features

- Mark channels with custom emojis
- Role-based permissions
- Admin controls
- Rate limit handling
- Automatic cooldown management
- Ephemeral responses
- Open source code

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
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.example.env` to `.env` and fill in your values:
   ```bash
   cp .example.env .env
   ```
4. Configure your bot token and permissions in `.env`
5. Run the bot:
   ```bash
   python bot.py
   ```

## Default Commands

- `/mark` - Toggle emoji in channel name
- `/waiting` - Mark channel as waiting for response
- `/urgent` - Mark channel as urgent
- `/checkmark` - Check when a channel can be marked again
- `/help` - Show help information
- `/setemoji` - Change emoji for a command (Admin only)
- `/sync` - Force sync commands (Admin only)

## Rate Limits

Discord has strict rate limits for channel modifications:
- 2 channel edits per 10 minutes per channel
- Global rate limits may apply

The bot handles these limits by:
- Tracking channel modification times
- Enforcing cooldowns
- Providing clear error messages
- Showing remaining cooldown time

## Permission System

The bot uses a flexible permission system:
- Role-based access control
- User-specific permissions
- Admin-only mode option
- Configurable through `.env`

## Requirements

- Python 3.8+
- discord.py
- python-dotenv
- PyYAML

## 2.0 Update

The bot now features a powerful configuration system through `config.yaml`, allowing you to customize and extend its functionality to match your specific needs.

### Custom Command Configuration

The `config.yaml` file lets you define your own commands with:
- Custom emojis
- Specific descriptions
- Unique command names

Example configuration:
```yaml
commands:
  mark:
    emoji: "🟣"
    description: "Mark a channel as to-do"
    command_name: "mark"
  waiting:
    emoji: "⌛"
    description: "Mark a channel as waiting for response"
    command_name: "waiting"
  urgent:
    emoji: "🔴"
    description: "Mark a channel as urgent"
    command_name: "urgent"
```

### Key Features

1. **Dynamic Command Creation**
   - Commands are automatically created on bot startup
   - No code changes needed to add new commands
   - Each command gets its own emoji and description

2. **Flexible Marking System**
   - Multiple markers can coexist
   - Easy transition between different states
   - Clear visual hierarchy with emojis

3. **Easy Customization**
   - Change emojis without restarting the bot
   - Add new commands by editing the config file
   - Modify descriptions to match your workflow

4. **Admin Controls**
   - Change emojis on the fly with `/setemoji`
   - Force command sync with `/sync`
   - Maintain security with permission system

### How to Add New Commands

1. Open `config.yaml`
2. Add a new command section:
   ```yaml
   newcommand:
     emoji: "🆕"
     description: "Your command description"
     command_name: "newcommand"
   ```
3. Restart the bot or use `/sync`

The bot will automatically:
- Create the new command
- Add it to the help menu
- Handle all permissions and rate limits
- Support emoji customization

### Best Practices

1. **Emoji Selection**
   - Use distinct emojis for different states
   - Consider color coding for visual hierarchy
   - Choose emojis that are widely supported

2. **Command Naming**
   - Use clear, descriptive names
   - Keep names short but meaningful
   - Avoid special characters

3. **Description Writing**
   - Be clear and concise
   - Explain the purpose
   - Use consistent formatting

## Contact

📧 Email: [glizzykingdreko@gmail.com](mailto:glizzykingdreko@gmail.com)
🐦 Twitter: [@glizzykingdreko](https://twitter.com/glizzykingdreko)
💻 GitHub: [glizzykingdreko](https://github.com/glizzykingdreko)
- Project Maintainer: [glizzykingdreko](mailto:glizzykingdreko@protonmail.com)
- You like my projects? [Buy me a coffee](https://www.buymeacoffee.com/glizzykingdreko) 