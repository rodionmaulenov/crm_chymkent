import logging
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from mothers.management.commands.record_to_the_file import save_new_message_for_laboratory
from mothers.models.mother import LaboratoryFile
from asgiref.sync import sync_to_async
import pytz
from datetime import datetime
from django.contrib.auth import get_user_model
from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramBadRequest

User = get_user_model()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_all_uploaded_files(laboratory):
    # Get the analysis types related to the laboratory
    analysis_type_objs = await sync_to_async(lambda: list(laboratory.analysis_types.all()))()

    # Total count of analysis types
    count_analysis = len(analysis_type_objs)

    # List to keep track of whether each analysis type has an uploaded file or video
    uploaded = []

    # Iterate over each analysis type
    for analysis_type_obj in analysis_type_objs:
        # Check if there is any file or video corresponding to the analysis type
        has_file_or_video = await sync_to_async(
            lambda: LaboratoryFile.objects.filter(
                analysis_type=analysis_type_obj,
                laboratory=laboratory
            ).exclude(file__exact='', video__exact='').exists()
        )()

        uploaded.append(has_file_or_video)
        logger.info(f"uploaded: {uploaded}")

    # Verify that all analysis types have corresponding files or videos and that counts match
    all_uploaded = all(uploaded) and (len(uploaded) >= count_analysis)

    return all_uploaded


def has_finalize_upload_button(keyboard, callback_data):
    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == callback_data:
                return True
    return False


def increment_button_text(button_text, callback_data, current_callback_data, count_files_uploaded):
    # Check if the current button is the one clicked
    if callback_data == current_callback_data:
        match = re.match(r"(\d+) ✅", button_text)
        if match:
            # Increment the existing count
            count = count_files_uploaded
            new_text = f"{count} ✅{button_text[match.end():]}"  # Keep the rest of the text after incrementing the count
        else:
            # Start with a count of 1 if no existing count is found
            new_text = f"{count_files_uploaded} ✅{button_text}"
        return new_text
    return button_text


async def get_uploaded_files_count(laboratory_id, analysis_type_id):
    count_files = await sync_to_async(LaboratoryFile.objects.filter(
        laboratory_id=laboratory_id,
        analysis_type=analysis_type_id,
        file__isnull=False,
        video__exact=''
    ).count)()
    return count_files


async def send_upload_prompt(laboratory_id, bot, callback_query, analysis_type, user_data):
    """
    Send a prompt to the user to upload a file or video based on the analysis type.
    """

    if callback_query.data.startswith('ultrasound_video_'):
        message = await bot.send_message(callback_query.from_user.id,
                                         f"😄👋 Let's go to upload the <b>{analysis_type.get_name_display()}</b> video file.",
                                         parse_mode=ParseMode.HTML)
        # Save expected file type in context
        user_data[callback_query.from_user.id]['expected_file_type'] = 'video'
    else:
        message = await bot.send_message(callback_query.from_user.id,
                                         f"Let's go to upload your <b>{analysis_type.get_name_display()}</b> file. 😃👍",
                                         parse_mode=ParseMode.HTML)
        # Save expected file type in context
        user_data[callback_query.from_user.id]['expected_file_type'] = ['document', 'photo']

    await save_new_message_for_laboratory(laboratory_id, callback_query.message.chat.id, message.message_id,
                                          is_posted=False)


async def handle_file_upload(message, bot, file_type='document'):
    """
    Handle the upload of a file (video, document, or photo) and return the downloaded file and original filename.

    :param message: The Message object containing the file.
    :param bot: The bot instance used to interact with Telegram.
    :param file_type: The type of file to handle ('video', 'document', or 'photo').
    :return: A tuple containing the downloaded file and the original filename.
    """
    if file_type == 'video':
        file_id = message.video.file_id
        original_filename = message.video.file_name
    elif file_type == 'document':
        file_id = message.document.file_id
        original_filename = message.document.file_name
    elif file_type == 'document' or (file_type == 'photo' and message.document):
        file_id = message.document.file_id
        original_filename = message.document.file_name
    else:  # Assume it's a photo if not video or document
        file_id = message.photo[-1].file_id  # Use the highest resolution photo
        original_filename = "photo.jpg"  # Default name for the photo since Telegram doesn't provide one

    # Download the file from Telegram
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    return downloaded_file, original_filename


async def update_video_uploaded_button(bot, chat_id, message_id, original_keyboard, callback_query,
                                       count_video_uploaded):
    """
    Update the clicked button's text to "✅ Video Uploaded" and update the message.

    :param bot: The bot instance.
    :param chat_id: The chat ID where the message is located.
    :param message_id: The message ID that needs to be edited.
    :param original_keyboard: The original inline keyboard markup.
    :param callback_query: The callback query containing the data.
    :param count_video_uploaded: The count of videos uploaded.
    """
    new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=increment_button_text(button.text, button.callback_data, callback_query.data, count_video_uploaded)
                if count_video_uploaded != 0 else button.text,
                callback_data=button.callback_data
            )
            if button.callback_data else InlineKeyboardButton(
                text=button.text,
                url=button.url
            )
            for button in row
        ]
        for row in original_keyboard
    ])
    try:
        # if upload the same file several times this error is raised
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=new_keyboard
        )
    except TelegramBadRequest:
        return

    return new_keyboard


async def update_file_uploaded_button(bot, chat_id, message_id, original_keyboard, callback_query, count_files):
    """
    Update the clicked button's text to "✅ File Uploaded" and update the message.

    :param bot: The bot instance.
    :param chat_id: The chat ID where the message is located.
    :param message_id: The message ID that needs to be edited.
    :param original_keyboard: The original inline keyboard markup.
    :param callback_query: The callback query containing the data.
    :param count_files: The count of files uploaded.
    """

    new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=increment_button_text(button.text, button.callback_data, callback_query.data, count_files)
                if count_files != 0 else button.text,
                callback_data=button.callback_data
            )
            if button.callback_data else InlineKeyboardButton(
                text=button.text,
                url=button.url
            )
            for button in row
        ]
        for row in original_keyboard
    ])
    # if upload the same file several times this error is raised
    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=new_keyboard
        )
    except TelegramBadRequest:
        return

    return new_keyboard


async def get_analysis_button_pairs(selected_analysis_types, instance_id):
    # Prefetch display names to avoid any synchronous operations during button creation
    button_pairs = []

    # Fetch display names if they involve any database interaction
    analysis_type_display_names = await sync_to_async(
        lambda: [(atype.id, atype.get_name_display()) for atype in selected_analysis_types]
    )()

    # Temporary list to store buttons in pairs
    temp_buttons_row = []

    # Create button pairs asynchronously
    for atype_id, display_name in analysis_type_display_names:
        if display_name == 'Ultrasound':
            # Add the "Upload video" button
            temp_buttons_row.append(
                InlineKeyboardButton(
                    text=f"🎥 {display_name}",
                    callback_data=f"ultrasound_video_{atype_id}_{instance_id}"
                )
            )

            # Check if the temp_buttons_row has 2 buttons and add to button_pairs
            if len(temp_buttons_row) == 2:
                button_pairs.append(temp_buttons_row)
                temp_buttons_row = []

            # Add the "Upload ultrasound file" button
            temp_buttons_row.append(
                InlineKeyboardButton(
                    text=f"📥 {display_name}",
                    callback_data=f"ultrasound_file_{atype_id}_{instance_id}"
                )
            )

        else:
            # Add the main button for non-ultrasound types
            temp_buttons_row.append(
                InlineKeyboardButton(
                    text=f"📥 {display_name}",
                    callback_data=f"upload_file_{atype_id}_{instance_id}",
                )
            )

        # If two buttons have been added, append them as a row and clear the temp list
        if len(temp_buttons_row) == 2:
            button_pairs.append(temp_buttons_row)
            temp_buttons_row = []

    # If any buttons are left over, add them as the last row
    if temp_buttons_row:
        button_pairs.append(temp_buttons_row)

    return button_pairs


async def construct_analysis_types_list(analysis_type_objs):
    """Constructs the analysis types list asynchronously."""
    return await sync_to_async("\n".join)(
        [atype.get_name_display() for atype in analysis_type_objs]
    )


async def construct_message(instance, analysis_types_list, user_id):
    """Constructs the message asynchronously."""
    instance_id = await sync_to_async(lambda: instance.id)()
    mother_name = await sync_to_async(lambda: instance.mother.name)()
    utc_scheduled_time = await sync_to_async(lambda: instance.scheduled_time)()
    local_scheduled_time = await convert_utc_to_local(user_id, utc_scheduled_time)
    description = await sync_to_async(lambda: instance.description)()

    # # Format the local scheduled time into a more readable format
    formatted_time = local_scheduled_time.strftime("🗓️ %A, %d %B \n⏰ %H:%M")

    return (
        f"*New Laboratory Created:*\n"
        f"*ID:* `{instance_id}`\n"
        f"*Mother:* `{mother_name}`\n"
        f"*Scheduled Time:* `{formatted_time}`\n"
        f"*Analysis Types:*\n`{analysis_types_list}`\n\n"
        f"*Description:* `{description}`\n\n"
        f"Please attach the result files for each analysis.📎\n"
        f"👇"
    )


async def convert_utc_to_local(user_id: int, utc_datetime: datetime) -> datetime:
    # Retrieve the user asynchronously
    user = await User.objects.aget(id=user_id)

    # Get the user's timezone, defaulting to 'UTC' if not set
    user_timezone = getattr(user, 'timezone', 'UTC')

    # Convert the string timezone to a timezone object
    user_timezone = pytz.timezone(str(user_timezone))

    # Make the datetime object timezone-aware in UTC if it isn't already
    if utc_datetime.tzinfo is None:
        utc_datetime = pytz.utc.localize(utc_datetime)
    else:
        utc_datetime = utc_datetime.astimezone(pytz.utc)

    # Convert the UTC timezone-aware datetime to the user's local timezone
    local_datetime = utc_datetime.astimezone(user_timezone)

    return local_datetime
