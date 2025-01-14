# Telegram Channel Management Bot

A Telegram bot for managing multiple channels and groups efficiently, providing functionality to ban/unban users, retrieve member stats, and more.

## Features

- **Ban Users:** Ban users from all channels within a specified group, with optional delay.
- **Timer-Based Ban:** Schedule bans for specific users after a delay, ensuring precise control over banning operations.
- **Unban Users:** Unban users from all channels within a specified group.
- **View Stats:** Retrieve member details such as name, username, and joined date for each channel in a group.
- **Interactive Buttons:** Use inline buttons to perform actions directly in private chats.
- **Manage Folders:** Manage folders containing multiple Telegram channels efficiently.
- **Single Channel Support:** Easily manage individual Telegram channels.

This bot is highly effective for managing multiple Telegram channels or entire folders of channels, making it ideal for large-scale channel administrators.

## Commands

```
/list
    List all available group names.

/help
    Show the help menu with a list of commands and their usage.

/ban [username or user_id] [group_name] [delay_in_minutes]
    Ban a user from all channels in the specified group. Optionally, specify a delay.

/unban [username or user_id] [group_name]
    Unban a user from all channels in the specified group.

/stats [group_name]
    Display member statistics for each channel in the specified group.
```

## Setup

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install telethon
   ```
3. Create a bot on Telegram via the [BotFather](https://t.me/BotFather) to obtain the API token.
4. Replace the placeholders in the script with your Telegram `API_ID`, `API_HASH`, and `BOT_TOKEN`.
5. Run the script:
   ```bash
   python bot.py
   ```

## Running on a VPS

To keep the bot running on a VPS, you can use the `screen` utility:

1. Install screen:
   ```bash
   sudo apt-get install screen
   ```
2. Start a new screen session:
   ```bash
   screen -S bot_session
   ```
3. Run the bot script:
   ```bash
   python bot.py
   ```
4. Detach from the screen session while keeping it running:
   ```bash
   Ctrl+A, then D
   ```
5. To reattach to the session later:
   ```bash
   screen -r bot_session
   ```

## Configuration

Define your channel groups in the `channel_groups` dictionary. Each group should have a unique name as the key and a list of channel IDs as the value.

## Error Handling

The bot includes error handling for invalid commands, missing group names, and more. Detailed error messages are displayed to guide the user.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for enhancements and bug fixes.

## License

This project is licensed under the **MIT License**. See the LICENSE file for details.

## Disclaimer

Use this bot responsibly. Ensure you have the appropriate permissions to manage the channels you configure.
