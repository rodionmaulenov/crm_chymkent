import asyncio
import logging
import aiofiles
from celery import shared_task
from django.utils import timezone
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from documents.models import MainDocument
from mothers.management.commands.handlers import bot
from .management.commands.another_functions import construct_message, construct_analysis_types_list
from .management.commands.record_to_the_file import delete_laboratory_group_message, save_new_message_for_laboratory
from .models import Mother
from django.db.models import Q
from asgiref.sync import sync_to_async
from .models.mother import Laboratory, AnalysisType
from django.contrib.auth import get_user_model
from aiogram.enums.parse_mode import ParseMode

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
def send_telegram_message(group_id, laboratory_id, analysis_type_ids, user_id):
    laboratory_obj = Laboratory.objects.get(id=laboratory_id)

    async def async_send_message():

        await delete_laboratory_group_message(laboratory_id, group_id, bot, is_posted=True)

        # Define the buttons
        two_buttons = [
            [
                InlineKeyboardButton(
                    text="✅ Come",
                    callback_data=f"come_{laboratory_id}_{analysis_type_ids}_{user_id}"
                ),
                InlineKeyboardButton(
                    text="🚫 Not Come",
                    callback_data=f"not_come_{laboratory_id}"
                ),
            ]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=two_buttons)

        passport_document = await sync_to_async(lambda: laboratory_obj.mother.main_document.filter(
            title=MainDocument.MainDocumentChoice.PASSPORT
        ).first())()

        if passport_document:
            passport_file_path = passport_document.file.path
            file_name = passport_document.file.name.split('/')[-1]

            # Open the image file and read its contents asynchronously
            async with aiofiles.open(passport_file_path, 'rb') as file:
                file_data = await file.read()

            input_file = BufferedInputFile(file_data, filename=file_name)

            # Fetch analysis types asynchronously
            analysis_type_objs_list = await sync_to_async(
                lambda: list(AnalysisType.objects.filter(id__in=analysis_type_ids))
            )()

            # Asynchronously construct the analysis types list
            analysis_types_list = await construct_analysis_types_list(analysis_type_objs_list)

            # Asynchronously construct the message
            message = await construct_message(laboratory_obj, analysis_types_list, user_id)

            # Send the photo along with the constructed message and keyboard
            sent_message = await bot.send_photo(
                chat_id=group_id,
                photo=input_file,
                caption=message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )

            # Update the file with the new message ID
            await save_new_message_for_laboratory(laboratory_id, group_id, sent_message.message_id, is_posted=True)

    # Use existing or create new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(async_send_message())
