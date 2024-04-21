from moviepy.editor import VideoFileClip, VideoClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
import moviepy.video.fx.all as vfx
from fastapi import UploadFile
from typing import List, Optional, Union
import os
import uuid


async def convert_to_tik_tok(
    files: List[UploadFile],
    audio: Optional[UploadFile],
    effect: Optional[str]
):
    clips = await crop_clips(files, [9, 16])

    combined_clips = concatenate_videoclips(clips)

    if effect:
        combined_clips = add_effects(combined_clips, effect)

    no_audio_path = f"static/{uuid.uuid4()}.mp4"
    combined_clips.write_videofile(no_audio_path, codec='libx264')

    final_video_path = no_audio_path

    if audio:
        final_video_path = await add_audio_to_video(no_audio_path, audio)
        os.remove(no_audio_path)

    for clip in clips:
        clip.close()
        if os.path.exists(clip.filename):
            os.remove(clip.filename)

    return f"http://localhost:8000/{final_video_path}"


async def add_audio_to_video(video_filename: str, audio: UploadFile):
    video_clip = VideoFileClip(video_filename)
    audio_file_path = f"temp_audio_{uuid.uuid4()}.mp3"
    with open(audio_file_path, 'wb') as f:
        contents = await audio.read()
        f.write(contents)

    # Create an audio clip and set its duration to match the video
    audio_clip = AudioFileClip(audio_file_path)
    final_clip = video_clip.set_audio(
        audio_clip.set_duration(video_clip.duration))

    # Save the final video with audio to a new path
    final_video_path = f"static/{uuid.uuid4()}.mp4"
    final_clip.write_videofile(final_video_path, codec='libx264')

    # Clean up
    video_clip.close()
    audio_clip.close()
    os.remove(audio_file_path)  # Remove temporary audio file

    return final_video_path


async def crop_clips(files: List[UploadFile], size: list):
    clips = []
    for file in files:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
        clip = VideoFileClip(temp_file_path)
        # Calculate dimensions to maintain a 9:16 aspect ratio
        target_height = clip.size[1]  # Use original height or a target height
        target_width = target_height * size[0] // size[1]

        # Ensure the target width does not exceed the video's original width
        if target_width > clip.size[0]:
            target_width = clip.size[0]
            # Adjust height according to the actual width
            target_height = target_width * size[1] // size[0]

        # Calculate the cropping area
        x_center = clip.size[0] / 2
        y_center = clip.size[1] / 2
        x1 = max(x_center - target_width / 2, 0)
        y1 = max(y_center - target_height / 2, 0)

        # Crop the video
        cropped_clip = clip.crop(  # type: ignore
            x1=x1, y1=y1, width=target_width, height=target_height)  # type: ignore
        clips.append(cropped_clip)
        file.file.close()
    return clips


def add_effects(video: Union[VideoClip, CompositeVideoClip], effect: str):
    if effect == "black_and_white":
        new_video = video.fx(vfx.blackwhite)  # type: ignore
    elif effect == "time_mirror":
        new_video = video.fx(vfx.time_mirror)  # type: ignore
    elif effect == "slow_motion":
        new_video = video.fx(vfx.speedx, 0.5)  # type: ignore
    elif effect == "painting":
        new_video = video.fx(vfx.painting)  # type: ignore
    elif effect == "inverted":
        new_video = video.fx(vfx.invert_colors)  # type: ignore

    return new_video


def generate_filename(extension):
    return f"static/{uuid.uuid4()}.{extension}"
