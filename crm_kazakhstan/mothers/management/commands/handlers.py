import logging
from asgiref.sync import sync_to_async
from aiogram import Bot, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import os

from mothers.management.commands.record_to_the_file import save_file_async
from mothers.models.mother import LaboratoryFile, AnalysisType
from decouple import config

bot = Bot(token=config("TELEGRAM_BOT_TOKEN_FOR_UZB"))

router = Router()

CHAT_ID = '-1002171039112'
DOWNLOAD_DIR = 'uploads/'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to store user data
user_data = {}


@router.callback_query(lambda c: c.data.startswith('upload_file_'))
async def process_upload_button(callback_query: CallbackQuery):
    analysis_type_id, laboratory_id = map(int, callback_query.data.split('_')[2:])

    analysis_type = await AnalysisType.objects.select_related().aget(id=analysis_type_id)
    await bot.send_message(callback_query.from_user.id,
                           f"Please upload your file for analysis type {analysis_type.get_name_display()} now.")

    # Save the context (analysis type, laboratory ID, message ID, chat ID, keyboard) for the user
    user_data[callback_query.from_user.id] = {
        'analysis_type_id': analysis_type_id,
        'laboratory_id': laboratory_id,
        'message_id': callback_query.message.message_id,
        'chat_id': callback_query.message.chat.id,
        'inline_keyboard': callback_query.message.reply_markup.inline_keyboard,
        'callback_query': callback_query
    }


@router.message(lambda message: message.document is not None)
async def handle_docs_photo(message: Message):
    # Retrieve the analysis type and laboratory ID from the user's context
    context = user_data.get(message.from_user.id)
    if not context:
        await message.answer("Error: No context found for your file upload. Please press the button first.")
        return

    analysis_type_id = context['analysis_type_id']
    laboratory_id = context['laboratory_id']
    message_id = context['message_id']
    chat_id = context['chat_id']
    original_keyboard = context['inline_keyboard']
    callback_query = context['callback_query']

    document_id = message.document.file_id
    file_info = await bot.get_file(document_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    # Ensure the download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, message.document.file_name)

    # # Save the file locally
    # with open(file_path, 'wb') as f:
    #     f.write(downloaded_file.getvalue())
    # Save the file asynchronously
    await save_file_async(file_path, downloaded_file)

    # Save file information to the database using sync_to_async
    laboratory_file = await sync_to_async(LaboratoryFile.objects.filter)(
        laboratory_id=laboratory_id,
        analysis_type_id=analysis_type_id
    )
    laboratory_file = await sync_to_async(laboratory_file.first)()

    if laboratory_file:
        laboratory_file.file = file_path
        await sync_to_async(laboratory_file.save)()
        await message.answer("File has been successfully uploaded and saved.")

        # Update only the clicked button's text to "✅ File Uploaded"
        new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ File Uploaded" if button.callback_data == callback_query.data else button.text,
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

        # Ensure that you are editing the correct message
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=new_keyboard
        )

        # Add a "Return" button to the current message with the correct link
        return_link = f"https://t.me/uzb_analysis/{message_id}"

        return_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Return", url=return_link)],
        ])

        await message.answer(
            "You can return to the previous message or join the group if you are not a member.",
            reply_markup=return_keyboard
        )
