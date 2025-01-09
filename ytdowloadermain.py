import yt_dlp
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import os
import time

# directory default dl
download_directory = os.getcwd()

# update opt
def update_stream_options():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a valid YouTube URL.")
        return

    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

            video_qualities = []
            audio_qualities = []

            for f in formats:
                if f.get("vcodec") != "none" and f.get("acodec") == "none":
                    resolution = f.get("format_note") or f.get("height")
                    if resolution:
                        video_qualities.append(f"{resolution}p")

                if f.get("acodec") != "none" and f.get("vcodec") == "none":
                    abr = f.get("abr")
                    if abr:
                        audio_qualities.append(f"{int(abr)}kbps")

            video_combo["values"] = sorted(set(video_qualities))
            audio_combo["values"] = sorted(set(audio_qualities))

            if video_qualities:
                video_combo.current(0)
            else:
                video_combo["values"] = ["None"]
                video_combo.current(0)

            if audio_qualities:
                audio_combo.current(0)
            else:
                audio_combo["values"] = ["None"]
                audio_combo.current(0)
    except Exception as e:
        messagebox.showerror("Error", f"Could not retrieve formats: {e}")

# audio dan video quality
def download():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a valid YouTube URL.")
        return

    selected_video_quality = video_combo.get()
    selected_audio_quality = audio_combo.get()

    if not selected_video_quality and not selected_audio_quality:
        messagebox.showerror("Error", "Please select a video or audio quality.")
        return

    ydl_opts = {
        "quiet": True,
        "outtmpl": os.path.join(download_directory, "%(title)s.%(ext)s"),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if selected_video_quality and selected_video_quality != "None":
                ydl_opts["format"] = f"bestvideo[height<={selected_video_quality.rstrip('p')}]"
            if selected_audio_quality and selected_audio_quality != "None":
                ydl_opts["format"] += "+bestaudio/best"

            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            # for file time 
            current_time = time.time()
            os.utime(file_path, (current_time, current_time))

            messagebox.showinfo("Success", f"Download completed! File saved in: {download_directory}")
    except Exception as e:
        messagebox.showerror("Error", f"Download failed: {e}")

# download function
def browse_directory():
    global download_directory
    directory = filedialog.askdirectory()
    if directory:
        download_directory = directory
        directory_label.config(text=f"Download Directory: {download_directory}")

# UI Setup
root = Tk()
root.title("YouTube Downloader")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

#YT url
url_label = ttk.Label(mainframe, text="YouTube URL:")
url_label.grid(column=0, row=0, padx=5, pady=5, sticky=W)
url_entry = ttk.Entry(mainframe, width=50)
url_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(W, E))

#video quality
video_label = ttk.Label(mainframe, text="Video Quality:")
video_label.grid(column=0, row=1, padx=5, pady=5, sticky=W)
video_combo = ttk.Combobox(mainframe, state="readonly")
video_combo.grid(column=1, row=1, padx=5, pady=5, sticky=(W, E))
video_combo["values"] = []

#audio quality
audio_label = ttk.Label(mainframe, text="Audio Quality:")
audio_label.grid(column=0, row=2, padx=5, pady=5, sticky=W)
audio_combo = ttk.Combobox(mainframe, state="readonly")
audio_combo.grid(column=1, row=2, padx=5, pady=5, sticky=(W, E))
audio_combo["values"] = []

#download location
browse_button = ttk.Button(mainframe, text="Browse", command=browse_directory)
browse_button.grid(column=0, row=3, padx=5, pady=5, sticky=W)

directory_label = ttk.Label(mainframe, text=f"Download Directory: {download_directory}")
directory_label.grid(column=1, row=3, padx=5, pady=5, sticky=(W, E))

#download and refresh opt
download_button = ttk.Button(mainframe, text="Download", command=download)
download_button.grid(column=0, row=4, padx=5, pady=5, sticky=W)

refresh_button = ttk.Button(mainframe, text="Refresh Options", command=update_stream_options)
refresh_button.grid(column=1, row=4, padx=5, pady=5, sticky=(W, E))



root.mainloop()
