# personal channel management bot. Able to manage multiple channels at one time.
import json
import asyncio
import os
from telethon.sync import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsSearch
from telethon.errors.rpcerrorlist import UserNotParticipantError, ChannelPrivateError
from telethon import Button, utils
from telethon.tl.functions.messages import ExportChatInviteRequest
from dotenv import load_dotenv


load_dotenv()
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
bot_token = os.getenv('bot_token')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

with open('config.json', 'r') as f:
    channel_groups = json.load(f)

@bot.on(events.NewMessage(pattern='/list'))
async def list_groups(event):
    group_names = "\n".join([f"`{group}`" for group in channel_groups.keys()])
    await event.reply(f"Available Groups:\n\n{group_names}")

@bot.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    help_text = """
**BanBot Commands:**

`/ban [user_id|username] [group_name] [delay_in_minutes]`
   - Bans the specified user from all channels in the given group after the specified delay (in minutes).

`/unban [user_id|username] [group_name]`
   - Unbans the specified user from all channels in the given group.

`/stats [group_name]`
   - Shows member details (name, username, joined date) for each channel in the specified group.

**Additional Features:**
- Send a username to the bot in a private message to get a list of buttons for banning them from specific groups.

**Available Group Names:**
{}
    """.format("\n".join(f"- {group}" for group in channel_groups.keys()))
    await event.reply(help_text)

@bot.on(events.NewMessage(pattern='/ban'))
async def ban_user(event):
    try:
        parts = event.raw_text.split()
        if len(parts) < 3:
            raise ValueError
        user_id_or_username = parts[1]
        group_name = parts[2].lower()
        delay = int(parts[3]) if len(parts) > 3 else 0
    except (IndexError, ValueError):
        await event.reply('Invalid command format. Usage: /ban [user_id|username] [group_name] [delay_in_minutes]')
        return
    if group_name not in channel_groups:
        await event.reply(f'Invalid group name. Available groups: {", ".join(channel_groups.keys())}')
        return
    await ban_user_in_group(event, group_name, user_id_or_username, delay)

@bot.on(events.NewMessage(pattern='/unban'))
async def unban_user(event):
    args = event.raw_text.split()
    if len(args) != 3:
        await event.reply('Invalid usage. Please provide a user ID/username and a group name. Usage: /unban [user_id|username] [group_name]')
        return
    user_to_unban = args[1]
    group_name = args[2].lower()
    if group_name not in channel_groups:
        await event.reply(f'Invalid group name. Available groups: {", ".join(channel_groups.keys())}')
        return
    try:
        user = await bot.get_entity(user_to_unban)
        # Unban by setting all rights to False
        rights = ChatBannedRights(
            until_date=None,
            view_messages=False,
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_games=False,
            send_inline=False,
            embed_links=False
        )
        for channel_id in channel_groups[group_name]:
            channel = await bot.get_entity(channel_id)
            await bot(EditBannedRequest(channel, user, rights))
        await event.reply(f'User unbanned successfully from all channels in the "{group_name}" group.')
    except Exception as e:
        await event.reply(f'An error occurred: {str(e)}')

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

@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def handle_private_message(event):
    message_text = event.raw_text.strip()
    # If it's a command, let the command handlers process it
    if message_text in ["/stats", "/help", "/ban", "/unban"]:
        return
    # Otherwise, treat as username or user ID
    try:
        user = await bot.get_entity(message_text)
        buttons = []
        for group in channel_groups:
            button = [Button.inline(group, data=f'ban_{group}_{user.id}')]
            buttons.append(button)
        await event.reply(f"Select a group to ban {message_text} from:", buttons=buttons)
    except ValueError:
        await event.reply(f"Invalid user ID/username: {message_text}")
    except Exception as e:
        await event.reply(f'An unexpected error occurred: {str(e)}')

@bot.on(events.CallbackQuery(pattern=r'ban_'))
async def ban_button_handler(event):
    _, group_name, user_id_str = event.data.decode().split("_")
    user_id = int(user_id_str)
    await ban_user_in_group(event, group_name, user_id)

async def ban_user_in_group(event, group_name, user_id_or_username, delay=0, reason=None):
    try:
        user = await bot.get_entity(user_id_or_username)
        delay_message = f" in {delay} minutes" if delay > 0 else ""
        response_message = f"User {getattr(user, 'username', user.id)} will be banned from the {group_name} group{delay_message}."
        initial_message = await event.respond(response_message)
        if delay > 0:
            await asyncio.sleep(delay * 60)
        for channel_id in channel_groups[group_name]:
            try:
                rights = ChatBannedRights(until_date=None, view_messages=True)
                await bot(EditBannedRequest(channel_id, user, rights))
            except UserNotParticipantError:
                pass
        # Edit the original message to confirm the ban
        if hasattr(initial_message, 'edit'):
            await initial_message.edit(f"User {getattr(user, 'username', user.id)} has been banned from the {group_name} group.")
    except ValueError as ve:
        error_message = "Invalid user ID/username. Please double-check."
        if isinstance(event, events.CallbackQuery):
            await event.answer(error_message, alert=True)
        else:
            await event.reply(error_message)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        if isinstance(event, events.CallbackQuery):
            await event.answer(error_message, alert=True)
        else:
            await event.reply(error_message)

if __name__ == '__main__':
    with bot:
        print("Bot is running. Press Ctrl+C to stop.")
        bot.run_until_disconnected()
