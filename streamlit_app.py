import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mpy
import tempfile
import os

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

global img, bg_img, submit_btn

temp_file_path = "myfile.mp4"
print(temp_file_path)

@st.cache_data
def get_temp_file():
    if temp_file_path == "":
        return temp_file_path
    else:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            return temp_file.name


fps = 15
width = 0
height = 0
temp_file_path = get_temp_file()
print('this is the temp file',temp_file_path)


def get_position():
    return {
        'Top': height - 16,
        'Center': height / 2,
        'Bottom': height / 3
    }


def make_frame(t):
    global last_image, video_ready
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
    video_ready = True
    return last_image


def predict():
    global video_ready
    print('we are here and now', duration)
    try:
        clip = mpy.VideoClip(make_frame, duration=int(duration))
        clip.write_videofile(temp_file_path, fps=fps,
                            codec="libx264", audio_codec="aac")
        video_ready = True  # Set video_ready to True after successful video generation
    except Exception as e:
        print(e)

st.write(
    """
# Welcome to DuchOfTime
Create Countdown Timer for any of your events,
If it showing a blank screen try it again
"""
)

bg_img = st.sidebar.file_uploader(
    label="Select Image for Background of countdown video",
    type=["png", "jpg"]
)
if bg_img:
    img = Image.open(bg_img)
    width, height = img.size
    st.sidebar.image(bg_img, width=256)
    st.sidebar.write('This is the background Image to use', bg_img.name)
countdown_color = st.sidebar.color_picker(
    'Select the color of the countdown text')
choose_font = st.sidebar.selectbox(label='Select the font to use', options=[
                                   'Impacted', 'Lato-Regular', 'SilomBol', 'Trajan Bold'])
choose_font_size = st.sidebar.number_input(label='Choose the font size',
                                           min_value=10, step=4)
position = st.sidebar.selectbox(
    label='Select Position', options=get_position().keys())
duration = st.sidebar.number_input('Choose how long the countdown will be',
                                   min_value=1, step=1)


if bg_img:
    submit_btn = st.button('Generate Countdown Video', type="primary", on_click=predict)

    if temp_file_path != "" and submit_btn is True:
        print('this is how the temp_file_path looks', temp_file_path)
        file_exist = os.path.exists(temp_file_path)
        print('the file exist', file_exist, temp_file_path)
        if file_exist:
            video_file = open(temp_file_path, 'rb')
            video_clip = video_file.read()
            st.video(video_clip)
            st.download_button(label="Download video",
                            file_name=bg_img.name.split(".")[0] + '.mp4',
                            mime="video/mp4",
                            data=video_clip)
