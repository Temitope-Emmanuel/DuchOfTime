import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mpy

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

global img, bg_img, submit_btn
fps = 15
video_file_path = ''
width = 0
height = 0

def get_position():
    return{
    'Top': height - 16,
    'Center': height / 2,
    'Bottom': height/ 3
}

st.write(
    """
# Welcome to DuchOfTime
Create Countdown Timer for any of your events
"""
)

bg_img = st.sidebar.file_uploader(
    label="Select Image for Background of countdown video",
    type=["png", "jpg"]
)
if bg_img:
    st.sidebar.image(bg_img, width=256)
    st.sidebar.write('This is the background Image to use', bg_img.name)
countdown_color = st.sidebar.color_picker(
    'Select the color of the countdown text')
choose_font = st.sidebar.selectbox(label='Select the font to use', options=[
                                   'Impacted', 'Lato-Regular', 'SilomBol', 'Trajan Bold'])
choose_font_size = st.sidebar.number_input(label='Choose the font size',
                                            min_value=10, placeholder=10, step=4)
position = st.sidebar.selectbox(label='Select Position', options=get_position().keys())
duration = st.sidebar.number_input('Choose how long the countdown will be',
                                    min_value=1, placeholder=10, step=1)

if bg_img is not None:
    img = Image.open(bg_img)
    width, height = img.size
    video_file_path = bg_img.name.split('.')[0]+'.mp4'


def make_frame(t):
    global last_image
    font = ImageFont.truetype(choose_font+'.ttf', choose_font_size)
    print('this is the text', position, get_position()[position])

    image = img.copy()
    draw = ImageDraw.Draw(image)
    space_length = draw.textlength(" ", font)
    word = format_duration(int(duration)-int(t))
    word_length = draw.textlength(word + " ", font) - space_length
    draw.text(((width/2)-(word_length/2), get_position()[position]),
              word, fill=countdown_color, font=font)
    last_image = np.array(image)
    return last_image


def predict():
    print('we are here and now', duration)
    clip = mpy.VideoClip(make_frame, duration=int(duration))
    clip.write_videofile(video_file_path, fps=fps,
                         codec="libx264", audio_codec="aac")
    return video_file_path


if bg_img:
    submit_btn = st.button('Generate Countdown Video',
                           type="primary", on_click=predict)

if video_file_path is not "" and submit_btn:
    video_file = open(video_file_path, 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
    st.download_button(label="Download video",
                       file_name=video_file_path,
                       mime="video/mp4",
                       data=video_bytes)
    # os.remove(video_file_path)
