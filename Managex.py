
import asyncio
from telethon.sync import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsSearch
from telethon.errors.rpcerrorlist import UserNotParticipantError, ChannelPrivateError
from telethon import Button, utils

# Set API  (Use env file for better safety of data)
api_id = 'xyz'  #  API ID - your own (replace xyz )
api_hash = 'xyz'  #  Telegram API hash - your own (grt it on "auth.telegram.com")
bot_token = 'xyz'  # Replace with your bot token (obtained when creating a bot on BotFather)  

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Define channel groups for management
channel_groups = {
    "channel_name0": [-100 your_channel_id],  # like -100123456789  where 123456789 will be your channel id
    "channel_name1": [ ],
    "channel_name2": [-100 your_channel_id, -100 your_channel_id, -100 your_channel_id],
    "channel_name3": [-100 your_channel_id],

    "channel_name4": [-100 your_channel_id, -100 your_channel_id, -100 your_channel_id, -100 your_channel_id,-100 your_channel_id ,-100 your_channel_id ],   # can also manage FOLDERS

    
    # add others 
}

# Handle the '/list' command 
@bot.on(events.NewMessage(pattern='/list'))
async def list_groups(event):
    group_names = "\n".join([f"`{group}`" for group in channel_groups.keys()])
    await event.reply(f"Available Groups:\n\n{group_names}")

@bot.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    help_text = """
**BanBot Commands:**

`/ban [username] [group_name] [delay_in_minutes]`

   - Bans the specified user from all channels in the given group after the specified delay (in minutes).


`/unban [username] [group_name]`

   - Unbans the specified user from all channels in the given group.

`/stats [group_name]`

   - Shows member details (name, username, joined date) for each channel in the specified group.

**Additional Features:**

- Send a username to the bot in a private message to get a list of buttons for banning them from specific groups.

**Available Group Names:**

{}

    """.format("\n".join(f"- {group}" for group in channel_groups.keys()))

    await event.reply(help_text)

# Handle the '/ban' 
@bot.on(events.NewMessage(pattern='/ban'))
async def ban_user(event):
    try:
    
        parts = event.raw_text.split()
        user_id = int(parts[1])  # Extract user ID of the users
        group_name = parts[2].lower()
        delay = int(parts[3]) if len(parts) > 3 else 0  # Optional delay if you want to ban afteer some time
    except (IndexError, ValueError):
        await event.reply('Invalid command format. Usage: /ban [user_id] [group_name] [delay_in_minutes]')
        return

    if group_name not in channel_groups:
        await event.reply(f'Invalid group name. Available groups: {", ".join(channel_groups.keys())}')
        return

    await ban_user_in_group(event, group_name, user_id, delay)

# Handle the '/unban' (capable to remove the users from removed users list on telegram)
@bot.on(events.NewMessage(pattern='/unban'))
async def unban_user(event):
    args = event.raw_text.split()
    if len(args) != 3:
        await event.reply('Invalid usage. Please provide a user ID/username and a group name.')
        return

    user_to_unban = args[1]
    group_name = args[2].lower()

    if group_name not in channel_groups:
        await event.reply(f'Invalid group name. Available groups: {", ".join(channel_groups.keys())}')
        return

    try:
        user = await bot.get_entity(user_to_unban)
        for channel_id in channel_groups[group_name]:
            channel = await bot.get_entity(channel_id)
            await bot(EditBannedRequest(channel, user, ChatBannedRights(until_date=None, view_messages=None)))
        await event.reply(f'User unbanned successfully from all channels in the "{group_name}" group.')
    except Exception as e:
        await event.reply(f'An error occurred: {str(e)}')

# Handle the '/stats' 
@bot.on(events.NewMessage(pattern='/stats'))
async def channel_stats(event):
    try:
        _, group_name = event.raw_text.split()
    except ValueError:
        await event.reply('Invalid command format. Usage: /stats [group_name]')
        return

    if group_name not in channel_groups:
        await event.reply(f'Invalid group name. Available groups: {", ".join(channel_groups.keys())}')
        return

    MAX_MESSAGE_LENGTH = 3800

    # Processing each channel in the specified group
    for channel_id in channel_groups.get(group_name, []):
        try:
            channel = await bot.get_entity(channel_id)
            participants = await bot(GetParticipantsRequest(
                channel, ChannelParticipantsSearch(''), offset=0, limit=1000, hash=0
            ))

            total_members = participants.count
            await event.respond(f"📊 **Stats for Channel:** {channel.title}  (Total Members: {total_members})")

            message_parts = []
            current_part = ""
            for i, participant in enumerate(participants.participants, start=1):
                user = await bot.get_entity(participant.user_id)
                if user and not user.bot:
                    joined_date = participant.date.strftime("%Y-%m-%d") if hasattr(participant, 'date') else "Unknown"
                    user_info = f"{i}. > **{utils.get_display_name(user)}** \n"
                    user_info += f"    [{user.username or 'N/A'}](tg://user?id={user.id}) - Joined: {joined_date}\n"

                    if len(current_part) + len(user_info) > MAX_MESSAGE_LENGTH:
                        message_parts.append(current_part)
                        current_part = ""
                    current_part += user_info

            if current_part:
                message_parts.append(current_part)

            for part in message_parts:
                await event.respond(part, link_preview=False)
        except ChannelPrivateError:
            await event.reply(f"🔒 Channel {channel_id}: Private")

# Handle private messages
@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def handle_private_message(event):
    message_text = event.raw_text.strip()
    print("Received private message" + message_text)

    if message_text in ["/stats", "/help", "/ban", "/unban"]:
        print("It was a command")
        return

    print("It looks like a username")
    try:
        user = await bot.get_entity(message_text)
        buttons = []
        for group in channel_groups:
            button = [Button.inline(group, data=f'ban_{group}_{user.id}')]
            buttons.append(button)
        await event.reply(f"Select a group to ban {message_text} from:", buttons=buttons)
    except ValueError:
        print(f"[handle_private_message] Invalid user ID/username: {message_text}")
    except Exception as e:
        print(f"[handle_private_message] Unexpected error: {e}")
        await event.reply(f'An unexpected error occurred: {str(e)}')

# Handle button clicks  , buttons signal ban function if clicked
@bot.on(events.CallbackQuery(pattern=r'ban_'))
async def ban_button_handler(event):
    _, group_name, user_id_str = event.data.decode().split("_")
    user_id = int(user_id_str)

    print(f"[ban_button_handler] Received ban request for user ID {user_id} in group {group_name}")

    await ban_user_in_group(event, group_name, user_id)

async def ban_user_in_group(event, group_name, user_id_or_username, delay=0, reason=None):
    try:
        user = await bot.get_entity(user_id_or_username)
        delay_message = f" in {delay} minutes" if delay > 0 else ""
        response_message = f"User {user.username} will be banned from the {group_name} group{delay_message}."

        initial_message = await event.respond(response_message)

        if delay > 0:
            await asyncio.sleep(delay * 60)

        for channel_id in channel_groups[group_name]:
            try:
                rights = ChatBannedRights(until_date=None, view_messages=True)
                if reason:
                    rights.comment = reason
                await bot(EditBannedRequest(channel_id, user, rights))
            except UserNotParticipantError:
                pass

        if isinstance(initial_message, events.Message):
            await initial_message.edit(f"User {user.username} has been banned from the {group_name} group.")

    except ValueError as ve:
        print(f"[ban_user_in_group] ValueError: {ve}")
        error_message = "Invalid user ID/username. Please double-check."
        if isinstance(event, events.CallbackQuery):
            await event.answer(error_message, alert=True)
        else:
            await event.reply(error_message)
    except Exception as e:
        print(f"[ban_user_in_group] Unexpected error: {e}")
        error_message = f"An error occurred: {str(e)}"
        if isinstance(event, events.CallbackQuery):
            await event.answer(error_message, alert=True)
        else:
            await event.reply(error_message)
          
if __name__ == '__main__':
    with bot:
        print("Bot is succesfully running. use ctrl+c to stop it manualy.")
        bot.run_until_disconnected()
