import aiofiles
import json
import os

MESSAGE_FILE_PATH = "mothers/management/commands/message_data.json"


async def read_message_data():
    """Read message data from the JSON file asynchronously."""
    if os.path.exists(MESSAGE_FILE_PATH):
        async with aiofiles.open(MESSAGE_FILE_PATH, "r") as file:
            contents = await file.read()
            return json.loads(contents)
    return {}


async def write_message_data(data):
    """Write message data to the JSON file asynchronously."""
    async with aiofiles.open(MESSAGE_FILE_PATH, "w") as file:
        await file.write(json.dumps(data, indent=4))


async def get_existing_message_id(laboratory_id):
    """Get the existing message ID for a given laboratory_id asynchronously."""
    message_data = await read_message_data()
    return message_data.get(str(laboratory_id))


async def update_message_data(laboratory_id, message_id):
    """Update the message data with a new message ID for a given laboratory_id asynchronously."""
    message_data = await read_message_data()
    message_data[str(laboratory_id)] = message_id
    await write_message_data(message_data)


async def save_file_async(file_path, downloaded_file):
    """Save the file asynchronously."""
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(downloaded_file.getvalue())
