from pytube import YouTube
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os
import threading
from pydub import AudioSegment
import subprocess
import re

def get_streams(url):
    yt = YouTube(url)
    video_streams = yt.streams.filter(file_extension='mp4', adaptive=True, only_video=True).order_by('resolution').desc()
    audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
    return video_streams, audio_streams, yt.title

def download_stream(stream, output_path, filename):
    try:
        stream.download(output_path, filename=filename)
        return os.path.join(output_path, filename)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def convert_to_mp3(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        mp3_path = file_path.rsplit('.', 1)[0] + '.mp3'
        audio.export(mp3_path, format='mp3')
        os.remove(file_path)  # Hapus file asli setelah konversi
        return mp3_path
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion: {e}")
        return None

def merge_video_audio(video_path, audio_path, output_path, video_title):
    try:
        # Membersihkan judul video dari karakter yang tidak valid
        clean_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
        output_file = os.path.join(output_path, f"{clean_title}.mp4")
        command = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{output_file}"'
        subprocess.run(command, shell=True, check=True)
        os.remove(video_path)
        os.remove(audio_path)
        return output_file
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred during merging: {e}")
        return None

def download():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a URL.")
        return
    
    output_path = os.path.expanduser("~/Downloads")
    video_streams, audio_streams, video_title = get_streams(url)

    # Membersihkan judul video dari karakter yang tidak valid
    clean_title = re.sub(r'[\\/*?:"<>|]', "", video_title)

    selected_video = video_combo.get()
    selected_audio = audio_combo.get()

    if selected_video != "None":
        video_stream = next(stream for stream in video_streams if stream.resolution == selected_video)
        audio_stream = next(stream for stream in audio_streams if stream.abr == selected_audio)
        
        def video_audio_download_and_merge():
            video_path = download_stream(video_stream, output_path, "video.mp4")
            audio_path = download_stream(audio_stream, output_path, "audio.mp4")
            if video_path and audio_path:
                merged_file = merge_video_audio(video_path, audio_path, output_path, clean_title)
                if merged_file:
                    messagebox.showinfo("Success", "Download and merging completed!")
        
        download_thread = threading.Thread(target=video_audio_download_and_merge)
        download_thread.start()
    elif selected_audio != "None":
        audio_stream = next(stream for stream in audio_streams if stream.abr == selected_audio)
        
        def audio_download_and_convert():
            downloaded_file = download_stream(audio_stream, output_path, f"{clean_title}.mp4")
            if downloaded_file:
                mp3_file = convert_to_mp3(downloaded_file)
                if mp3_file:
                    messagebox.showinfo("Success", "Download and conversion to MP3 completed!")
        
        download_thread = threading.Thread(target=audio_download_and_convert)
        download_thread.start()
    else:
        messagebox.showerror("Error", "Please select a video or audio quality.")

def update_streams(*args):
    url = url_entry.get()
    if url:
        video_streams, audio_streams, _ = get_streams(url)
        video_combo['values'] = ["None"] + [stream.resolution for stream in video_streams]
        audio_combo['values'] = ["None"] + [stream.abr for stream in audio_streams]
        video_combo.current(0)
        audio_combo.current(0)

def refresh():
    update_streams()

root = Tk()
root.title("YouTube Downloader")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

ttk.Label(mainframe, text="YouTube URL:").grid(column=1, row=1, sticky=W)
url_entry = ttk.Entry(mainframe, width=40)
url_entry.grid(column=2, row=1, sticky=(W, E))

ttk.Label(mainframe, text="Video Quality:").grid(column=1, row=2, sticky=W)
video_combo = ttk.Combobox(mainframe)
video_combo.grid(column=2, row=2, sticky=(W, E))
video_combo['values'] = ["None"]
video_combo.current(0)

ttk.Label(mainframe, text="Audio Quality:").grid(column=1, row=3, sticky=W)
audio_combo = ttk.Combobox(mainframe)
audio_combo.grid(column=2, row=3, sticky=(W, E))
audio_combo['values'] = ["None"]
audio_combo.current(0)

url_entry.bind("<FocusOut>", update_streams)

download_button = ttk.Button(mainframe, text="Download", command=download)
download_button.grid(column=2, row=4, sticky=W)

refresh_button = ttk.Button(mainframe, text="Refresh", command=refresh)
refresh_button.grid(column=1, row=4, sticky=E)

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

root.mainloop()
