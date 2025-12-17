# Discord Economy & Management Bot

A comprehensive Discord bot featuring an economy system, private rooms, role management, and marriage functionality. Built with Python and discord.py.

## Features

### Economy System
- Dual currency system: Coins and Stars
- Currency transfer between users with configurable commission
- Currency conversion (Stars to Coins)
- Coin flip gambling game
- Duel system for competitive currency battles

### Role Management
- Create custom personal roles
- Manage role colors and names
- Assign roles to other users
- Toggle roles on/off
- Complete logging of all role actions

### Private Rooms
- Create personal voice channels
- Co-owner system for room management
- Access control and member management
- Customize room names and role colors
- Track member activity and time spent
- Comprehensive logging system

### Marriage System
- Propose and marry other users
- Automatic creation of love rooms for married couples
- Special role assignment for married users
- Divorce functionality
- Full activity logging

### User Statistics
- Track voice channel activity time
- Count messages sent
- View user balance and statistics

## Requirements

- Python 3.8 or higher
- discord.py 2.6.0 or higher
- aiohttp 3.8.5 or higher
- SQLite3 (included with Python)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Main-bot-discord-server-main
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the bot:
   - Copy `config.py.example` to `config.py`
   - Edit `config.py` and fill in all required values:
     - `BOT_TOKEN`: Your bot token from [Discord Developer Portal](https://discord.com/developers/applications)
     - `GUILD_ID`: Your Discord server ID
     - Configure all channel IDs, category IDs, and prices according to your needs

4. Run the bot:
```bash
python bot.py
```

## Configuration

All bot settings are located in `config.py`:

### Essential Settings
- `BOT_TOKEN`: Your bot's authentication token
- `GUILD_ID`: Target Discord server ID

### Currency Settings
- `CURRENCY_COINS`: Name for coins currency
- `CURRENCY_DIAMONDS`: Name for stars currency
- `CONVERSION_RATE`: Coins per star conversion rate
- `TRANSFER_FEE`: Percentage fee for transfers

### Pricing
- `ROLE_CREATE_PRICE`: Cost to create a role
- `ROLE_COLOR_PRICE`: Cost to change role color
- `ROLE_NAME_PRICE`: Cost to change role name
- `ROOM_RENAME_PRICE`: Cost to rename a room
- `ROOM_COLOR_PRICE`: Cost to change room role color
- `MARRY_PRICE`: Cost to get married

### Channel & Category IDs
- `PRIVATE_CATEGORY_ID`: Category for private rooms
- `LOVE_CATEGORY_ID`: Category for love rooms
- `LOVE_VOICE_TRANSFER_ID`: Voice channel for love room creation
- `LOVE_ROLE_ID`: Role ID for married users
- `TRANSFER_LOG_CHANNEL_ID`: Channel for transfer logs
- `ROOM_LOG_CHANNEL_ID`: Channel for room logs
- `LOVE_LOG_CHANNEL_ID`: Channel for marriage logs

## Commands

### Economy Commands
- `/balance [user]` - View user balance
- `/give <user> <currency_type> <amount>` - Transfer currency to another user
- `/convert <amount>` - Convert Stars to Coins
- `/coinflip <amount>` - Play coin flip game (bet 50-50000 coins)
- `/duel <user> <amount>` - Challenge a user to a duel

### Role Commands
- `/role create` - Create a personal role
- `/role manage` - Manage your existing roles
- `/inventory` - View your inventory (roles, rooms, items)

### Room Commands
- `/room` - Manage your private rooms
- `/addroom <name> <owner_id>` - Create a private room (Admin only)

### Relationship Commands
- `/marry <user>` - Propose marriage to another user
- `/divorce` - Divorce your current partner

### Utility Commands
- `/avatar <user>` - Display user avatar
- `/banner <user>` - Display user banner
- `/online [user]` - Show user activity statistics

### Admin Commands
- `/addm <user> <currency_type> <amount>` - Add currency to user (Admin only)

## Bot Permissions

The bot requires the following permissions:
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Manage Roles
- Manage Channels
- Move Members
- Connect (Voice)
- Speak (Voice)

## Database

The bot uses SQLite3 database (`bot.db`) to store:
- User balances
- Role ownership and assignments
- Private room data
- Marriage records
- Voice activity statistics
- Message counts

The database is automatically created on first run.

## Logging

The bot logs all important actions to designated channels:
- Currency transfers
- Room creation and management
- Marriage and divorce events
- Role management actions

Configure log channels in `config.py`.

## Troubleshooting

### Commands not appearing
- Ensure the bot has proper permissions
- Wait a few seconds after bot startup for command sync
- Restart Discord client (Ctrl+R)
- Check console for sync errors

### Bot not responding
- Verify bot token is correct
- Check bot is online on the server
- Ensure bot has required permissions
- Review console output for errors

### Permission errors
- Verify bot role is above target roles
- Check channel permissions
- Ensure bot has administrator permissions if needed

## Development

### Project Structure
```
.
├── bot.py              # Main bot file
├── config.py           # Configuration (create from config.py.example)
├── config.py.example   # Configuration template
├── database.py         # Database operations
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

### Adding New Features

1. Define commands using `@bot.tree.command()` decorator
2. Add configuration options to `config.py` if needed
3. Update database schema in `database.py` if required
4. Add logging calls using `send_log()` function

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.

## Author

[kompromizz]
