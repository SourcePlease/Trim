import subprocess
import os
import shutil

def remove_audio_subtitles(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-an', '-sn',  # Disable audio and subtitles
        '-c:v', 'copy',  # Copy video codec (no re-encoding)
        output_file
    ]
    subprocess.run(command)

def extract_audio_subtitles(input_file, output_audio, output_subtitle):
    command_audio = [
        'ffmpeg',
        '-i', input_file,
        '-vn',  # Disable video
        '-acodec', 'copy',
        output_audio
    ]
    command_subtitle = [
        'ffmpeg',
        '-i', input_file,
        '-map', '0:s:0',  # Select first subtitle track
        output_subtitle
    ]
    subprocess.run(command_audio)
    subprocess.run(command_subtitle)

def trim_video(input_file, output_file, start_time, end_time):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start_time,  # Start time
        '-to', end_time,  # End time
        '-c', 'copy',
        output_file
    ]
    subprocess.run(command)

def merge_videos(video_list, output_file):
    with open('videos.txt', 'w') as f:
        for video in video_list:
            f.write(f"file '{video}'\n")
    
    command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'videos.txt',
        '-c', 'copy',
        output_file
    ]
    subprocess.run(command)
    os.remove('videos.txt')

def mute_audio(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-an',  # Disable audio
        '-c:v', 'copy',
        output_file
    ]
    subprocess.run(command)

def merge_video_audio(video_file, audio_file, output_file):
    command = [
        'ffmpeg',
        '-i', video_file,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_file
    ]
    subprocess.run(command)

def merge_video_subtitle(video_file, subtitle_file, output_file):
    command = [
        'ffmpeg',
        '-i', video_file,
        '-vf', f"subtitles={subtitle_file}",
        output_file
    ]
    subprocess.run(command)

def video_to_gif(input_file, output_file, start_time, duration):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start_time,  # Start time
        '-t', duration,  # Duration of GIF
        '-vf', 'fps=10,scale=320:-1:flags=lanczos',
        '-c:v', 'gif',
        output_file
    ]
    subprocess.run(command)

def split_video(input_file, output_file, segment_time):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c', 'copy',
        '-map', '0',
        '-segment_time', segment_time,
        '-f', 'segment',
        output_file
    ]
    subprocess.run(command)

def generate_screenshot(input_file, output_image, time='00:00:10'):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', time,  # Time to take the screenshot
        '-vframes', '1',  # Capture only one frame
        output_image
    ]
    subprocess.run(command)

def generate_manual_screenshots(input_file, times, output_image_template):
    for i, time in enumerate(times):
        command = [
            'ffmpeg',
            '-i', input_file,
            '-ss', time,
            '-vframes', '1',
            output_image_template.format(i+1)
        ]
        subprocess.run(command)

def generate_sample(input_file, output_file, start_time, duration):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start_time,
        '-t', duration,  # Duration of sample
        '-c', 'copy',
        output_file
    ]
    subprocess.run(command)

def video_to_audio(input_file, output_file, audio_format='mp3', quality='high'):
    audio_bitrate = {
        'low': '64k',
        'medium': '128k',
        'high': '192k'
    }
    
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vn',  # Disable video
        '-c:a', audio_format,
        '-b:a', audio_bitrate[quality],
        output_file
    ]
    subprocess.run(command)

def optimize_video(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-crf', '28',  # Constant Rate Factor, lower means better quality
        '-preset', 'fast',  # Speed/quality tradeoff
        output_file
    ]
    subprocess.run(command)

def convert_video(input_file, output_file, output_format):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_file + '.' + output_format
    ]
    subprocess.run(command)

def rename_video(old_name, new_name):
    os.rename(old_name, new_name)

def get_media_info(input_file):
    command = [
        'ffmpeg',
        '-i', input_file
    ]
    subprocess.run(command)

def make_archive(input_files, output_archive, format='zip', password=None):
    if password:
        import pyminizip
        pyminizip.compress_multiple(input_files, [], output_archive, password, 5)
    else:
        shutil.make_archive(output_archive, format, root_dir=input_files[0])
