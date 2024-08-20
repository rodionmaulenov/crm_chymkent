import logging
from aiogram import Bot, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from mothers.management.commands.another_functions import get_analysis_button_pairs, send_upload_prompt, \
    handle_file_upload, update_video_uploaded_button, get_uploaded_files_count, update_file_uploaded_button, \
    has_finalize_upload_button, convert_utc_to_local, check_all_uploaded_files
from mothers.management.commands.record_to_the_file import save_uploaded_unique_file, save_uploaded_unique_video, \
    save_new_message_for_laboratory, delete_all_messages_from_bot
from mothers.models.mother import AnalysisType, Laboratory, LaboratoryFile
from decouple import config
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile

User = get_user_model()

bot = Bot(token=config("TELEGRAM_BOT_TOKEN_FOR_UZB"))

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to store user data
user_data = {}

# Global dictionary to store keyboards
keyboards_store = {}

# Global dictionary to store keyboards
keyboards_store_for_not_come = {}


@router.callback_query(lambda c: c.data.startswith('not_come_'))
async def mother_not_comes_to_laboratory(callback_query: CallbackQuery):
    laboratory_obj_id = int(''.join(callback_query.data.split('_')[2:]))

    keyboards_store_for_not_come[callback_query.message.chat.id] = {
        "not_sure": callback_query.message.reply_markup.inline_keyboard,
    }

    # Display a pop-up confirmation dialog
    await bot.answer_callback_query(
        callback_query.id,
        text="Did the client really not come?",
        show_alert=True,
    )

    # After the pop-up, show Yes/No buttons to confirm the action
    confirm_buttons = [
        [
            InlineKeyboardButton(
                text="✅ Yes, not come",
                callback_data=f"really_not_{laboratory_obj_id}"
            ),
            InlineKeyboardButton(
                text="❌ I'm not sure",
                callback_data="not_confident"
            )
        ]
    ]
    confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=confirm_buttons)

    # Edit the message's inline keyboard with the new buttons
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=confirmation_keyboard
    )


@router.callback_query(lambda c: c.data.startswith('really_not_'))
async def sure_mother_not_comes(callback_query: CallbackQuery):
    laboratory_obj_id = int(''.join(callback_query.data.split('_')[2:]))

    # The altered state in which the mothers came to the Laboratory
    laboratory_obj = await Laboratory.objects.aget(id=laboratory_obj_id)
    laboratory_obj.is_coming = False
    await laboratory_obj.asave()

    # Display a pop-up confirmation dialog
    await bot.answer_callback_query(
        callback_query.id,
        text="It's a pity, please accept my condolences",
        show_alert=False,
        cache_time=10
    )

    confirm_buttons = [
        [
            InlineKeyboardButton(
                text="🤬 she didn't come ...",
                callback_data="disable"
            ),
        ]
    ]
    confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=confirm_buttons)

    # Edit the message's inline keyboard with the new buttons
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=confirmation_keyboard
    )


@router.callback_query(lambda c: c.data.startswith('not_confident'))
async def when_not_sure(callback_query: CallbackQuery):
    initial_keyboard = keyboards_store_for_not_come[callback_query.message.chat.id]['not_sure']
    initial_keyboard = InlineKeyboardMarkup(inline_keyboard=initial_keyboard)

    # Display a pop-up confirmation dialog
    await bot.answer_callback_query(
        callback_query.id,
        text="When you will be confident, indicates the user status",
        show_alert=False,
        cache_time=15
    )

    # Edit the message's inline keyboard with the new buttons
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=initial_keyboard
    )


@router.callback_query(lambda c: c.data.startswith('come_'))
async def verify_mother_came_or_not(callback_query: CallbackQuery):
    laboratory_obj_id, analysis_type_ids_str, user_id = callback_query.data.split('_')[1:]

    keyboards_store[callback_query.message.chat.id] = {
        "not_sure": callback_query.message.reply_markup.inline_keyboard,
    }

    user_data['django_user_id'] = user_id

    # Display a pop-up confirmation dialog
    await bot.answer_callback_query(
        callback_query.id,
        text="Did the client really come?",
        show_alert=True,
    )

    # After the pop-up, show Yes/No buttons to confirm the action
    confirm_buttons = [
        [
            InlineKeyboardButton(
                text="✅ Yes, I'm sure",
                callback_data=f"yes_come_{laboratory_obj_id}_{analysis_type_ids_str}"
            ),
            InlineKeyboardButton(
                text="❌ I'm not sure",
                callback_data="not_sure"
            )
        ]
    ]
    confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=confirm_buttons)

    # Edit the message's inline keyboard with the new buttons
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=confirmation_keyboard
    )


@router.callback_query(lambda c: c.data.startswith('not_sure'))
async def when_not_sure(callback_query: CallbackQuery):
    initial_keyboard = keyboards_store[callback_query.message.chat.id]['not_sure']
    initial_keyboard = InlineKeyboardMarkup(inline_keyboard=initial_keyboard)

    # Display a pop-up confirmation dialog
    await bot.answer_callback_query(
        callback_query.id,
        text="When you will be confident, indicates the user status",
        show_alert=False,
        cache_time=15
    )

    # Edit the message's inline keyboard with the new buttons
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=initial_keyboard
    )


@router.callback_query(lambda c: c.data.startswith('yes_come_'))
async def mother_come_to_laboratory(callback_query: CallbackQuery):
    laboratory_obj_id, analysis_type_ids_str = callback_query.data.split('_')[2:]
    analysis_type_ids = list(map(int, analysis_type_ids_str.strip('[]').split(',')))

    # Show a pop-up asking for confirmation
    await bot.answer_callback_query(
        callback_query.id,
        text="Now you can add files to this client",
        show_alert=False,
        cache_time=7,
    )

    # The altered state in which the mothers came to the Laboratory
    laboratory_obj = await Laboratory.objects.aget(id=laboratory_obj_id)
    laboratory_obj.is_coming = True
    await laboratory_obj.asave()

    # Fetch analysis types asynchronously
    analysis_type_objs = await sync_to_async(AnalysisType.objects.filter)(id__in=analysis_type_ids)

    button_pairs = await get_analysis_button_pairs(analysis_type_objs, laboratory_obj_id)

    # Add a "Go to Bot" button at the bottom
    button_pairs.append([
        InlineKeyboardButton(
            text="🚀 Go to Bot",
            url="https://t.me/Kairatikbot"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=button_pairs)

    # Send the photo along with the constructed message and keyboard
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard
    )


@router.callback_query(
    lambda c: c.data.startswith('upload_file_') or c.data.startswith('ultrasound_video_') or c.data.startswith(
        'ultrasound_file_'))
async def process_upload_button(callback_query: CallbackQuery):
    analysis_type_id, laboratory_id = map(int, callback_query.data.split('_')[2:])

    analysis_type = await AnalysisType.objects.select_related().aget(id=analysis_type_id)

    # Save the context
    user_data[callback_query.from_user.id] = {
        'analysis_type_id': analysis_type_id,
        'laboratory_id': laboratory_id,
        'message_id': callback_query.message.message_id,
        'chat_id': callback_query.message.chat.id,
        'inline_keyboard': callback_query.message.reply_markup.inline_keyboard,
        'callback_query': callback_query,
    }
    await send_upload_prompt(laboratory_id, bot, callback_query, analysis_type, user_data)


@router.message(lambda message: message.document is not None or message.video is not None or message.photo is not None)
async def handle_docs_photo_and_video(message: Message):
    new_keyboard = None
    # Retrieve the analysis type and laboratory ID from the user's context
    context = user_data.get(message.from_user.id)

    analysis_type_id = context['analysis_type_id']
    laboratory_id = context['laboratory_id']
    message_id = context['message_id']
    chat_id = context['chat_id']
    original_keyboard = context['inline_keyboard']
    callback_query = context['callback_query']
    expected_file_type = context['expected_file_type']

    laboratory_obj = await Laboratory.objects.aget(id=laboratory_id)

    if message.video:
        await save_new_message_for_laboratory(laboratory_id, chat_id, message.message_id, is_posted=False)
        if expected_file_type != 'video':
            message_answer = await message.answer("Please upload a document file, not a video.")
            await save_new_message_for_laboratory(laboratory_id, chat_id, message_answer.message_id, is_posted=False)
            return

        downloaded_file, original_filename = await handle_file_upload(message, bot, file_type='video')

        await save_uploaded_unique_video(
            laboratory_id,
            analysis_type_id,
            downloaded_file,
            original_filename,
            message,
            chat_id
        )

        # Fetch the count of uploaded files for this analysis type and laboratory
        count_video_uploaded = await sync_to_async(LaboratoryFile.objects.filter(
            laboratory_id=laboratory_id,
            analysis_type_id=analysis_type_id,
            video__isnull=False,
            file__exact='',
        ).count)()

        # Update only the clicked button's text to "✅ Video Uploaded"
        new_keyboard = await update_video_uploaded_button(
            bot=bot,
            chat_id=chat_id,
            message_id=message_id,
            original_keyboard=original_keyboard,
            callback_query=callback_query,
            count_video_uploaded=count_video_uploaded
        )

    if message.document or message.photo:
        await save_new_message_for_laboratory(laboratory_id, chat_id, message.message_id, is_posted=False)
        if expected_file_type != ['document', 'photo']:
            message_answer = await message.answer("Please upload a video file, not a document.")
            await save_new_message_for_laboratory(laboratory_id, chat_id, message_answer.message_id, is_posted=False)
            return

        try:
            photo = message.photo[-1]
            if photo:
                file_type = 'photo'
            else:
                file_type = 'document'
        except Exception:  # when upload file without "Compress image"
            file_type = 'photo'

        downloaded_file, original_filename = await handle_file_upload(message, bot, file_type=file_type)

        await save_uploaded_unique_file(
            laboratory_id,
            analysis_type_id,
            downloaded_file,
            original_filename,
            message,
            chat_id
        )

        count_files = await get_uploaded_files_count(laboratory_id, analysis_type_id)

        # Update only the clicked button's text to "✅ File Uploaded"
        new_keyboard = await update_file_uploaded_button(
            bot=bot,
            chat_id=chat_id,
            message_id=message_id,
            original_keyboard=original_keyboard,
            callback_query=callback_query,
            count_files=count_files
        )

    # Add a "Return" button to the current message with the correct link
    return_link = f"https://t.me/uzb_analysis/{message_id}"

    return_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Return", url=return_link)],
    ])

    message_answer = await message.answer(
        "You can return to <u>post</u> or <u>upload next media</u> right here.",
        reply_markup=return_keyboard,
        parse_mode=ParseMode.HTML
    )
    await save_new_message_for_laboratory(laboratory_id, chat_id, message_answer.message_id, is_posted=False)

    all_uploaded = await check_all_uploaded_files(laboratory_obj)

    if not all_uploaded:
        # Add the button to show uploaded files
        uploaded_files_list = InlineKeyboardButton(text="📂 Show Uploaded Files", callback_data="show_uploaded_files")

        # Check if the 'finalize_upload' button already exists
        if not has_finalize_upload_button(new_keyboard, 'show_uploaded_files'):
            # Add the new button as a new row in the keyboard
            new_keyboard = InlineKeyboardMarkup(
                inline_keyboard=new_keyboard.inline_keyboard + [[uploaded_files_list]]
            )
        else:
            new_keyboard = new_keyboard

        try:
            # Attempt to edit the message's inline keyboard
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=new_keyboard
            )
        except TelegramBadRequest:
            return

    else:
        # Ensure the new button is properly instantiated
        finalize_upload_button = InlineKeyboardButton(text="🔒 Finalize Upload", callback_data='finalize_upload')

        # Check if the 'finalize_upload' button already exists
        if not has_finalize_upload_button(new_keyboard, 'finalize_upload'):
            # Add the new button as a new row in the keyboard
            new_keyboard = InlineKeyboardMarkup(
                inline_keyboard=new_keyboard.inline_keyboard + [[finalize_upload_button]]
            )
        else:
            new_keyboard = new_keyboard
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=new_keyboard
            )
        except TelegramBadRequest:
            return

    # Store the original keyboard using a unique key (e.g., message_id)
    keyboards_store[message_id] = new_keyboard

    await delete_all_messages_from_bot(laboratory_id, chat_id, message.from_user.id, bot, is_posted=False)


@router.callback_query(lambda c: c.data.startswith('show_uploaded_files'))
async def show_uploaded_files(callback_query: CallbackQuery):
    # Get the laboratory_id from the callback data or user context
    laboratory_id = user_data.get(callback_query.from_user.id)['laboratory_id']
    chat_id = user_data.get(callback_query.from_user.id)['chat_id']
    django_user_id = user_data.get('django_user_id')

    # Fetch the files
    files = await sync_to_async(
        lambda: list(LaboratoryFile.objects.filter(laboratory_id=laboratory_id).order_by('-created')))()

    message = None
    for file in files:
        # Open the file using aiofiles and read its path
        if file.file:
            input_file = FSInputFile(file.file.path)
            local_scheduled_time = await convert_utc_to_local(django_user_id, file.created)
            formatted_time = local_scheduled_time.strftime("🗓️ %A, %d %B - ⏰ %H:%M")
            message = await bot.send_document(
                chat_id=callback_query.from_user.id,
                document=input_file,
                caption=f"{file.file.name.split('/')[-1]}\n{formatted_time}"
            )
        if file.video:
            input_file = FSInputFile(file.video.path)
            local_scheduled_time = await convert_utc_to_local(django_user_id, file.created)
            formatted_time = local_scheduled_time.strftime("🗓️ %A, %d %B - ⏰ %H:%M")
            message = await bot.send_document(
                chat_id=callback_query.from_user.id,
                document=input_file,
                caption=f"{file.video.name.split('/')[-1]}\n{formatted_time}"
            )

        await save_new_message_for_laboratory(laboratory_id, chat_id, message.message_id, is_posted=False)

    await delete_all_messages_from_bot(laboratory_id, chat_id, message.from_user.id, bot, is_posted=False)


@router.callback_query(lambda c: c.data.startswith('finalize_upload'))
async def handle_finalize_button(callback_query: CallbackQuery):
    # Display a pop-up confirmation dialog
    await bot.answer_callback_query(
        callback_query.id,
        text="Are you sure you want to complete the upload?",
        show_alert=True,
        cache_time=5,
    )

    confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, complete upload", callback_data='yes_finalize_upload'),
            InlineKeyboardButton(text="❌ No, cancel", callback_data='no_finalize_upload')
        ],
    ])

    # Edit the message to display the new keyboard
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=confirmation_keyboard
    )


@router.callback_query(lambda c: c.data.startswith('yes_finalize_upload'))
async def handle_yes_finalize_upload_button(callback_query: CallbackQuery):
    # Display a pop-up confirmation dialog
    await bot.answer_callback_query(
        callback_query.id,
        text="Great, now you can not add new files. Move to another client",
        show_alert=False,
        cache_time=5,
    )

    original_keyboard = keyboards_store.get(callback_query.message.message_id)

    # Remove the "🚀 Go to Bot" button and disable the remaining buttons
    disabled_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=button.text,
                callback_data="disabled"
            )
            for button in row
        ]
        for row in original_keyboard.inline_keyboard
    ])

    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=disabled_keyboard
    )


@router.callback_query(lambda c: c.data.startswith('no_finalize_upload'))
async def handle_no_finalize_upload_button(callback_query: CallbackQuery):
    await bot.answer_callback_query(
        callback_query.id,
        text="Great, You still can add new files",
        show_alert=False,
        cache_time=7,
    )

    original_keyboard = keyboards_store.get(callback_query.message.message_id)
    # Edit the message to display the new keyboard
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=original_keyboard
    )
