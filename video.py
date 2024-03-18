import os, shutil, cv2
from moviepy.editor import *
from PIL import Image
import decoding as d

# to clean the tmp folder
def clean_tmp(path="./tmp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] tmp files are cleaned up")

# Count the number of frames in the video
def countFrames(f_name):
    clip = VideoFileClip(f_name)
    num_frames = int(clip.reader.nframes)
    clip.close()
    return num_frames

# Extract all frames from the video
def get_frames(f_name):
    """Returns all frames in the video object"""
    video_object = VideoFileClip(f_name)
    if not os.path.exists("./tmp"):
        os.makedirs("tmp")
    temp_folder = "./tmp/"
    for index, frame in enumerate(video_object.iter_frames()):
        img = Image.fromarray(frame, 'RGB')
        img.save(f'{temp_folder}{index}.png')
    print("[INFO] All frames are extracted from video")
    video_object.close()

# Function to embed the hidden file into the video
def new_video(f_name):
    
    audio_path="tmp\\audio.aac"
    file_ext=f_name.split(".")[-1]
    # Extract audio from the input video
    os.system(f"ffmpeg -i {f_name} -vn -acodec copy {audio_path} -y")
    print("Audio is extracted from video")
    
    capture = cv2.VideoCapture(f_name) # Stores OG Video into a Capture Window
    fps = capture.get(cv2.CAP_PROP_FPS) # Extracts FPS of OG Video

    video_path_real = "tmp\\%d.png" # To Get All Frames in Folder
    os.system(f"ffmpeg -framerate {fps} -i {video_path_real} -codec copy tmp\\only_video.{file_ext}") # Combining the Frames into a Video
    print("Video frames are copied without compression")
    
    os.system(f"ffmpeg -i tmp\\only_video.{file_ext} -i {audio_path} -codec copy Output\\video.{file_ext}") # Combining the Frames and Audio into a Video
    print('Video is successfully encoded with encrypted text Document')

    # Debugging: Check if the hidden file is present in the output directory
    if os.path.exists(f"video.{file_ext}"):
        print("Hidden file is embedded in the video without compression.")
    else:
        print("Hidden file is not embedded in the video.")
    clean_tmp()

# Function to get the number of frames in the video
def get_video_info(f_name,frame_count):
    print(frame_count)
    print(type(frame_count))
    count=countFrames(f_name)
    print()
    print(f"the number of frames in the video is {count}")
    print(f"the number of files that can be embedded into the video is : {((count-10)//(frame_count+2))}")
    return count,frame_count

def get_count(folder_path):
    # List all files and directories in the specified folder
    files = os.listdir(folder_path)
    # Filter out directories from the list
    files = [file for file in files if os.path.isfile(os.path.join(folder_path, file))]
    # Return the number of files
    return len(files)

# Function to check if the frame is hidden
def is_hidden(n):
    frame_file_name = os.path.join('./tmp', f"{n}.png")
    clear = d.decode_frame(frame_file_name).encode('latin-1')
    return clear.startswith(b'___') or clear.startswith(b'__')