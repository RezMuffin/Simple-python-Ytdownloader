from pytube import YouTube
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os
import threading

def get_streams(url):
    yt = YouTube(url)
    video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
    return video_streams, audio_streams

def download_stream(stream, output_path):
    try:
        stream.download(output_path)
        messagebox.showinfo("Success", "Download completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def download():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a URL.")
        return
    
    output_path = os.path.expanduser("~/Downloads")
    video_streams, audio_streams = get_streams(url)

    selected_video = video_combo.get()
    selected_audio = audio_combo.get()

    if selected_video != "None":
        video_stream = next(stream for stream in video_streams if stream.resolution == selected_video)
        download_thread = threading.Thread(target=download_stream, args=(video_stream, output_path))
        download_thread.start()
    elif selected_audio != "None":
        audio_stream = next(stream for stream in audio_streams if stream.abr == selected_audio)
        download_thread = threading.Thread(target=download_stream, args=(audio_stream, output_path))
        download_thread.start()
    else:
        messagebox.showerror("Error", "Please select a video or audio quality.")

def update_streams(*args):
    url = url_entry.get()
    if url:
        video_streams, audio_streams = get_streams(url)
        video_combo['values'] = ["None"] + [stream.resolution for stream in video_streams]
        audio_combo['values'] = ["None"] + [stream.abr for stream in audio_streams]

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

ttk.Label(mainframe, text="Audio Quality:").grid(column=1, row=3, sticky=W)
audio_combo = ttk.Combobox(mainframe)
audio_combo.grid(column=2, row=3, sticky=(W, E))
audio_combo['values'] = ["None"]

url_entry.bind("<FocusOut>", update_streams)

download_button = ttk.Button(mainframe, text="Download", command=download)
download_button.grid(column=2, row=4, sticky=W)

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

root.mainloop()
