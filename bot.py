import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import re

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize the Pyrogram Client
app = Client("my_bot", api_id=15830858, api_hash="2c015c994c57b312708fecc8a2a0f1a6", bot_token="6006802393:AAFeAWs0NhPDOc4_Bnd9RMEYjJniN05GELw")

def get_duration(filename):
    """Get the duration of the video in seconds."""
    logging.info("Getting duration of the video.")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
         "-of", "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

# Function to trim the video with progress
async def trim_video_with_progress(input_file, start_time, end_time, output_file, message):
    total_duration = get_duration(input_file)
    logging.info(f"Total duration of the video: {total_duration} seconds.")
    
    command = [
        'ffmpeg', '-y', '-i', input_file,
        '-ss', start_time, '-to', end_time,
        '-c', 'copy', output_file
    ]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            match = re.search(r"time=(\d+:\d+:\d+.\d+)", output)
            if match:
                current_time_str = match.group(1)
                current_time = sum(
                    x * float(t) for x, t in zip(
                        [3600, 60, 1], current_time_str.split(":")
                    )
                )
                progress = (current_time / total_duration) * 100
                logging.info(f"Progress: {progress:.2f}%")
                await message.edit_text(f"Trimming the video, please wait... {progress:.2f}%")
    return process.poll()

# Function to create a thumbnail
def create_thumbnail(input_file, thumbnail_file, time="00:00:30"):
    logging.info("Creating thumbnail.")
    command = [
        'ffmpeg', '-y', '-i', input_file,
        '-ss', time, '-vframes', '1',
        thumbnail_file
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.on_message(filters.command(["trim"]) & (filters.video | filters.document | filters.media))
async def trim(client: Client, message: Message):
    logging.info("Received trim command.")
    if not (message.reply_to_message.video or message.reply_to_message.document or message.reply_to_message.media):
        logging.warning("No video, document, or media found in the replied message.")
        await message.reply_text("Please reply to a video, document, or media message with /trim command.")
        return

    try:
        # Extract start time and end time from the message
        _, start_time, end_time = message.text.split()
    except ValueError:
        logging.warning("Invalid command format.")
        await message.reply_text("Usage: /trim <start_time> <end_time>\nExample: /trim 00:23:00 00:45:00")
        return

    if message.reply_to_message.video:
        media = message.reply_to_message.video
    elif message.reply_to_message.document:
        media = message.reply_to_message.document
    else:
        media = message.reply_to_message.media

    logging.info("Downloading video.")
    input_file = await message.reply_to_message.download()
    output_file = f"trimmed_{media.file_id}.mp4"
    thumbnail_file = f"thumbnail_{media.file_id}.jpg"

    # Notify the user about the start of the process
    progress_message = await message.reply_text("Trimming the video, please wait... 0%")

    # Trim the video with progress
    logging.info("Trimming video.")
    await trim_video_with_progress(input_file, start_time, end_time, output_file, progress_message)

    # Create a thumbnail from the video at the 30-second mark
    logging.info("Creating thumbnail.")
    create_thumbnail(input_file, thumbnail_file)

    # Send the trimmed video back to the user as a stream with a thumbnail
    logging.info("Sending trimmed video with thumbnail.")
    await message.reply_video(video=output_file, thumb=thumbnail_file, supports_streaming=True)

    # Delete the progress message and temporary files
    logging.info("Cleaning up temporary files.")
    await progress_message.delete()
    os.remove(input_file)
    os.remove(output_file)
    os.remove(thumbnail_file)

# Run the bot
app.run()
