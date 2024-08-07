import asyncio
import logging
import aiofiles
import pytz
from datetime import datetime
from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramAPIError
from celery import shared_task
from django.utils import timezone
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from documents.models import MainDocument
from mothers.management.commands.handlers import bot
from .management.commands.record_to_the_file import get_existing_message_id, update_message_data
from .models import Mother
from django.db.models import Q
from asgiref.sync import sync_to_async
from .models.mother import Laboratory, AnalysisType
from django.contrib.auth import get_user_model

User = get_user_model()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@shared_task
def delete_weekday_objects():
    # Exclude instances where any of the specified fields are null
    has_null_fields = Mother.objects.filter(
        Q(age__isnull=True) | Q(residence__isnull=True) | Q(height__isnull=True) | Q(weight__isnull=True) |
        Q(caesarean__isnull=True) | Q(children__isnull=True)
    )

    # Get the current date and time
    date_now = timezone.now()

    mothers_to_delete_ids = []
    for mother in has_null_fields:
        if mother.created.weekday() in [0, 1, 2, 3, 4] and mother.created.date() < date_now.date():
            mothers_to_delete_ids.append(mother.id)

    # Delete the mothers
    deleted, _ = Mother.objects.filter(id__in=mothers_to_delete_ids).delete()

    return deleted


@shared_task
def delete_weekend_objects():
    # Exclude instances where any of the specified fields are null
    has_null_fields = Mother.objects.filter(
        Q(age__isnull=True) | Q(residence__isnull=True) | Q(height__isnull=True) | Q(weight__isnull=True) |
        Q(caesarean__isnull=True) | Q(children__isnull=True)
    )

    # Get the current date and time
    date_now = timezone.now()

    mothers_to_delete_ids = []
    for mother in has_null_fields:
        if mother.created.weekday() in [5, 6] and mother.created.date() < date_now.date():
            mothers_to_delete_ids.append(mother.id)

    # Delete the mothers
    deleted, _ = Mother.objects.filter(id__in=mothers_to_delete_ids).delete()

    return deleted


@shared_task
def send_telegram_message(chat_id, instance_id, analysis_type_ids, user_id):
    """Send a message to the specified chat with details about the laboratory."""

    async def async_send_message():
        """Define the asynchronous function to send a message."""

        # Fetch instance asynchronously
        instance = await sync_to_async(Laboratory.objects.get)(id=instance_id)
        # Fetch analysis types asynchronously
        selected_analysis_types = await sync_to_async(AnalysisType.objects.filter)(id__in=analysis_type_ids)

        try:
            # Check if there is an existing message for this laboratory and delete it
            existing_message_id = await get_existing_message_id(instance.id)

            if existing_message_id:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=existing_message_id)
                except TelegramAPIError as e:
                    if 'message to delete not found' in str(e):
                        logger.warning(f"Message with ID {existing_message_id} not found in chat {chat_id}.")
                    else:
                        logger.error(f"Telegram API error while deleting message: {e}")

            button_pairs = await get_button_pairs(selected_analysis_types, instance.id)

            # Add a "Go to Bot" button at the bottom
            button_pairs.append([
                InlineKeyboardButton(
                    text="🚀 Go to Bot",
                    url="https://t.me/Kairatikbot"
                )
            ])

            keyboard = InlineKeyboardMarkup(inline_keyboard=button_pairs)

            # Asynchronously construct the analysis types list
            analysis_types_list = await construct_analysis_types_list(selected_analysis_types)

            # Asynchronously construct the message
            message = await construct_message(instance, analysis_types_list, user_id)

            # Fetch passport file asynchronously =
            passport_document = await sync_to_async(lambda: instance.mother.main_document.filter(
                title=MainDocument.MainDocumentChoice.PASSPORT
            ).first())()

            # Read the file directly from the local file system
            passport_file_path = passport_document.file.path  # Get the local file path
            file_name = passport_document.file.name.split('/')[-1]

            # Open the image file and read its contents asynchronously
            async with aiofiles.open(passport_file_path, 'rb') as file:
                file_data = await file.read()

            # Create a BufferedInputFile object from the data
            input_file = BufferedInputFile(file_data, filename=file_name)

            # Send the photo along with the constructed message and keyboard
            sent_message = await bot.send_photo(
                chat_id=chat_id,
                photo=input_file,
                caption=message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )

            # Update the file with the new message ID
            await update_message_data(instance.id, sent_message.message_id)

        except TelegramAPIError as e:
            logger.error(f"Telegram API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    # Use existing or create new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        # If there is no running event loop, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(async_send_message())


async def get_button_pairs(selected_analysis_types, instance_id):
    # Prefetch display names to avoid any synchronous operations during button creation
    button_pairs = []

    # Fetch display names if they involve any database interaction
    analysis_type_display_names = await sync_to_async(
        lambda: [(atype.id, atype.get_name_display()) for atype in selected_analysis_types]
    )()

    # Create button pairs asynchronously
    for i in range(0, len(analysis_type_display_names), 2):
        pair = analysis_type_display_names[i:i + 2]
        buttons = [
            InlineKeyboardButton(
                text=f"📥 {display_name}",
                callback_data=f"upload_file_{atype_id}_{instance_id}",
            )
            for atype_id, display_name in pair
        ]
        button_pairs.append(buttons)

    return button_pairs


async def construct_analysis_types_list(selected_analysis_types):
    """Constructs the analysis types list asynchronously."""
    return await sync_to_async("\n".join)(
        [atype.get_name_display() for atype in selected_analysis_types]
    )


async def construct_message(instance, analysis_types_list, user_id):
    """Constructs the message asynchronously."""
    instance_id = await sync_to_async(lambda: instance.id)()
    mother_name = await sync_to_async(lambda: instance.mother.name)()
    utc_scheduled_time = await sync_to_async(lambda: instance.scheduled_time)()
    local_scheduled_time = await convert_utc_to_local(user_id, utc_scheduled_time)
    local_scheduled_time_str = local_scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
    description = await sync_to_async(lambda: instance.description)()

    return (
        f"*New Laboratory Created:*\n"
        f"*ID:* `{instance_id}`\n"
        f"*Mother:* `{mother_name}`\n"
        f"*Scheduled Time:* `{local_scheduled_time_str}`\n"
        f"*Analysis Types:*\n`{analysis_types_list}`\n\n"
        f"*Description:* `{description}`\n"
        f"Please attach the result files for each analysis."
    )


async def convert_utc_to_local(user_id: int, utc_datetime: datetime) -> datetime:
    # Retrieve the user asynchronously
    user = await User.objects.select_related().aget(id=user_id)

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
