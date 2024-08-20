import asyncio
import logging
import re
import aiofiles
import aiofiles.os
import os
from aiogram.enums.parse_mode import ParseMode
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
from asgiref.sync import sync_to_async
from mothers.models.mother import AnalysisType, LaboratoryFile, LaboratoryMessage
from aiogram.exceptions import TelegramAPIError
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def calculate_file_hash(file_content):
    """
    Calculate the SHA-256 hash of the file content.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_content)
    return sha256_hash.hexdigest()


async def delete_laboratory_group_message(laboratory_id, group_id, bot, message_id=None, is_posted=None):
    # Check if there is an existing message for this laboratory and delete it
    filter_kwargs = {
        'laboratory_id': laboratory_id,
        'chat_id': group_id,
    }

    if message_id is not None:
        filter_kwargs['message_id'] = message_id
    if is_posted is not None:
        filter_kwargs['is_posted'] = is_posted

    laboratory_message = await LaboratoryMessage.objects.filter(**filter_kwargs).afirst()

    if laboratory_message is not None:
        message_id = await sync_to_async(lambda: laboratory_message.message_id)()

        try:
            await bot.delete_message(chat_id=group_id, message_id=message_id)
        except TelegramAPIError:
            pass
        finally:
            # Delete the record from the database after attempting to delete the message from Telegram
            await laboratory_message.adelete()


async def delete_all_messages_from_bot(laboratory_id, group_id, user_id, bot, is_posted=None):
    # Delay execution by 1 minute
    await asyncio.sleep(60)  # 60 seconds = 1 minute
    async for laboratory_message in LaboratoryMessage.objects.filter(
            laboratory_id=laboratory_id,
            chat_id=group_id,
            is_posted=is_posted
    ).aiterator():

        if laboratory_message is not None:
            message_id = laboratory_message.message_id

            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
            except TelegramAPIError as e:
                pass
            finally:
                # Delete the record from the database after attempting to delete the message from Telegram
                await laboratory_message.adelete()


async def save_new_message_for_laboratory(laboratory_id, group_id, message_id, is_posted=None):
    data_kwargs = {
        'laboratory_id': laboratory_id,
        'chat_id': group_id,
        'message_id': message_id
    }

    if is_posted is not None:
        data_kwargs['is_posted'] = is_posted

    await LaboratoryMessage.objects.acreate(**data_kwargs)


async def save_uploaded_unique_file(laboratory_id, analysis_type_id, downloaded_file, filename, message, chat_id):
    """
    Save the file from a BytesIO object to a LaboratoryFile model instance asynchronously.
    """
    # Calculate the hash of the file content
    files_value = downloaded_file.getvalue()
    file_hash = await calculate_file_hash(files_value)

    # Check if a file with the same hash already exists
    existing_file = await sync_to_async(LaboratoryFile.objects.filter)(
        hash=file_hash,
        laboratory_id=laboratory_id,
    )
    existing_file = await sync_to_async(existing_file.exists)()

    if existing_file:
        message_answer = await message.answer(
            "🔴 *This file already exists and cannot be uploaded again.*",
            parse_mode=ParseMode.MARKDOWN
        )
        await save_new_message_for_laboratory(laboratory_id, chat_id, message_answer.message_id, is_posted=False)
        return

    # Create a temporary file to save the content asynchronously
    async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        await temp_file.write(files_value)

    # Read the temporary file and save it to the model
    async with aiofiles.open(temp_file_path, 'rb') as temp_file:
        file_content = await temp_file.read()

        # Create a valid and safe filename
        safe_filename = get_valid_filename(filename)

        # Construct the new filename
        analysis_type = await sync_to_async(AnalysisType.objects.get)(id=analysis_type_id)
        new_filename = await construct_filename(laboratory_id, analysis_type, safe_filename)

        # Use sync_to_async to save the file content into the Django model
        await sync_to_async(LaboratoryFile.objects.create)(
            laboratory_id=laboratory_id,
            analysis_type_id=analysis_type_id,
            file=ContentFile(file_content, name=new_filename),
            hash=file_hash
        )

        message_answer = await message.answer("<i>File has been successfully uploaded and saved</i> 😂😂",
                                              parse_mode=ParseMode.HTML)
        await save_new_message_for_laboratory(laboratory_id, chat_id, message_answer.message_id, is_posted=False)

    # Clean up the temporary file
    await aiofiles.os.remove(temp_file_path)



async def save_uploaded_unique_video(laboratory_id, analysis_type_id, downloaded_file, filename, message, chat_id):
    """
    Save the video from a BytesIO object to a LaboratoryVideo model instance asynchronously.
    """
    # Calculate the hash of the file content
    files_value = downloaded_file.getvalue()
    file_hash = await calculate_file_hash(files_value)

    # Check if a file with the same hash already exists
    existing_file = await sync_to_async(LaboratoryFile.objects.filter)(
        hash=file_hash,
        laboratory_id=laboratory_id,
    )
    existing_file = await sync_to_async(existing_file.exists)()

    if existing_file:
        message_answer = await message.answer(
            "🔴 *This video already exists and cannot be uploaded again.*",
            parse_mode=ParseMode.MARKDOWN
        )
        await save_new_message_for_laboratory(laboratory_id, chat_id, message_answer.message_id, is_posted=False)
        return

    # Create a temporary file to save the content asynchronously
    async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        await temp_file.write(downloaded_file.getvalue())

    # Read the temporary file and save it to the model
    async with aiofiles.open(temp_file_path, 'rb') as temp_file:
        file_content = await temp_file.read()

        # Create a valid and safe filename
        safe_filename = get_valid_filename(filename)
        # Construct the new filename
        analysis_type = await sync_to_async(AnalysisType.objects.get)(id=analysis_type_id)

        file_name = await construct_ultrasound_video_name(laboratory_id, analysis_type, safe_filename)
        # Use sync_to_async to create and save the LaboratoryVideo instance
        await sync_to_async(LaboratoryFile.objects.create)(
            laboratory_id=laboratory_id,
            analysis_type_id=analysis_type_id,
            video=ContentFile(file_content, name=file_name),
            hash=file_hash
        )

        message_answer = await message.answer("<i>Video has been successfully uploaded and saved</i> 😂😂",
                                              parse_mode=ParseMode.HTML)
        await save_new_message_for_laboratory(laboratory_id, chat_id, message_answer.message_id, is_posted=False)

    # Clean up the temporary file
    await aiofiles.os.remove(temp_file_path)


def clean_filepath(filename):
    prohibited_characters = r'[\\/*?:"<>|\'`]'
    cleaned_filename = re.sub(prohibited_characters, '', filename)
    return cleaned_filename


async def construct_filename(laboratory_id, analysis_type, original_filename):
    extension = os.path.splitext(original_filename)[1]

    count_files = await sync_to_async(LaboratoryFile.objects.filter(
        laboratory_id=laboratory_id,
        analysis_type=analysis_type,
        file__isnull=False,
        video__exact=''
    ).count)() + 1

    new_filename = f'{analysis_type.name.title()}_{count_files}{extension}'
    return new_filename


async def construct_ultrasound_video_name(laboratory_id, analysis_type, original_filename):
    extension = os.path.splitext(original_filename)[1]

    count_ultrasound_videos = await sync_to_async(LaboratoryFile.objects.filter(
        laboratory_id=laboratory_id,
        analysis_type=analysis_type,
        video__isnull=False,
        file__exact='',
    ).count)() + 1
    new_filename = f'ultrasound_{count_ultrasound_videos}{extension}'
    return new_filename
