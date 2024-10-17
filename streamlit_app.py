import streamlit as st
import zipfile
import subprocess
import pandas as pd
import tempfile
import ffmpeg
import io
import os

fade_in = 1
fade_out = 1

def create_zip_from_folder(folder_path):
    zip_file_path = f"{folder_path}.zip"
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    return zip_file_path


def generate_thumbnail(video_bytes, thumbnail_path, time="00:01:05"):
    input_stream = io.BytesIO(video_bytes)
    ffmpeg.input("pipe:0", ss=time).output(thumbnail_path, vframes=1).run(input=input_stream.read(), overwrite_output=True)


def time_to_seconds(time_str):
    parts = time_str.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    else:
        return float(parts[0])


def cut_video_segment(input_bytes, output_file, start_time, end_time):
    start_time_sec = time_to_seconds(start_time)
    end_time_sec = time_to_seconds(end_time)
    duration = end_time_sec - start_time_sec
    command = [
        "ffmpeg",
        "-ss", start_time,
        "-to", end_time,
        "-i", "pipe:0",
        '-vf', f'fade=t=in:st=0:d={fade_in}, fade=t=out:st={duration-fade_out}:d={fade_out}',
        '-af', f'afade=t=in:st=0:d={fade_in}, afade=t=out:st={duration-fade_out}:d={fade_out}',
        output_file, "-y"
    ]
    try:
        process = subprocess.run(command, input=input_bytes,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        st.error(f"Error during FFmpeg processing: {e.stderr.decode()}")


def process_segments(csv_file, input_bytes):
    df = pd.read_csv(csv_file)
    temp_dir = tempfile.mkdtemp("segments")
    for index, row in df.iterrows():
        start_time = row["start_time"]
        end_time = row["end_time"]
        file_path = os.path.join(temp_dir, f"segment{index+1}.mp4")
        print(f"Processing segment {index + 1}: {start_time} to {end_time}")
        cut_video_segment(input_bytes, file_path, start_time, end_time)
    return temp_dir


temp_image_file = False

st.write(
    """
# Welcome to VideoRonin
Easily cut segments of a video via web
"""
)

selected_video = st.sidebar.file_uploader(
    label="Select Video to cut segment from",
    type=["mp4"]
)
if selected_video:
    # thumbnail = generate_thumbnail(selected_video.read(), "thumbnail.png")
    # st.sidebar.image("thumbnail.png")

    fade_in = st.sidebar.slider(
        "Select a fade in duration",
        min_value=0,
        max_value=10,
        value=1,
        step=1
    )
    st.sidebar.write(f"Selected Fade in time: {fade_in}s")
    fade_out = st.sidebar.slider(
        "Select a fade out duration",
        min_value=0,
        max_value=10,
        value=1,
        step=1
    )
    st.sidebar.write(f"Selected Fade out time: {fade_out}s")

    uploaded_csv = st.sidebar.file_uploader(
        "Choose CSV file that contains the timestamp", type="csv")
    if uploaded_csv is not None:
        if st.sidebar.button('Cut Videos', type="primary"):
            temp_dir = process_segments(io.BytesIO(
                uploaded_csv.read()), selected_video.read())
            if os.path.exists(temp_dir):
                zip_file_path = create_zip_from_folder(temp_dir)
                with open(zip_file_path, "rb") as f:
                    st.download_button(label="Download videos", data=f, file_name=os.path.basename(
                        zip_file_path), mime="application/zip")
            else:
                st.error(f"The folder '{temp_dir}' does not exist.")
