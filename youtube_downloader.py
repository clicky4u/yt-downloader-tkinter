import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from threading import Thread
import os
import webbrowser
import requests
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL
import re

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, 'Logo.ico')
qr_code_path = os.path.join(script_dir, 'qr.jpg')

# Function to select directory
def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_label.config(text=f'Selected Directory: {directory}')

# Function to sanitize the video title before using it as a filename
def sanitize_filename(filename):
    # Replace invalid characters with an underscore
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_video():
    urls = url_entry.get("1.0", tk.END).strip().splitlines()
    output_directory = directory_label.cget("text").replace('Selected Directory: ', '')

    if not output_directory or not os.path.isdir(output_directory):
        status_text.insert(tk.END, 'Please select a valid directory.\n', 'error')
        return

    def download_single_video(url):
        info_dict = None  # Initialize info_dict here
        try:
            # Ensure the output directory exists
            if not os.path.isdir(output_directory):
                raise ValueError("Invalid directory")

            # Set the correct path for ffmpeg.exe
            ffmpeg_path = '_internal/ffmpeg.exe'  # Path to ffmpeg.exe

            # Check if FFmpeg executable exists at the specified path
            if not os.path.isfile(ffmpeg_path):
                raise FileNotFoundError(f"FFmpeg executable not found at {ffmpeg_path}")

            # Configure yt-dlp options (without cookiefile)
            ydl_opts = {
                'outtmpl': os.path.join(output_directory, '%(title)s.%(ext)s'),  # Output filename template
                'progress_hooks': [progress_hook],  # Progress hook function
                'quiet': True,  # Suppress most output
                'no_warnings': True,  # Disable warnings
                'geo_bypass': True,  # Allow bypassing geo restrictions
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',  # User agent string
                'ffmpeg_location': ffmpeg_path,  # Path to FFmpeg executable
            }

            # Check if Audio-only is selected
            if audio_only_var.get():
                ydl_opts['format'] = 'bestaudio/best'  # Download audio only (MP3)
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',  # Correct key for audio conversion
                    'preferredcodec': 'mp3',  # Output as mp3
                    'preferredquality': '192'
                }]
            else:
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'  # Download video in MP4 and audio in MP3

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)  # Extract info without downloading
                ydl.download([url])  # Download the content (audio or video)

                if not info_dict:
                    raise ValueError(f"Failed to extract video information for {url}")

                # If 'With Thumbnail' is selected, download the thumbnail
                if thumbnail_var.get():
                    thumbnail_url = info_dict.get('thumbnail')
                    if thumbnail_url:
                        sanitized_title = sanitize_filename(info_dict['title'])
                        thumbnail_path = os.path.join(output_directory, f"{sanitized_title}_thumbnail.jpg")
                        response = requests.get(thumbnail_url)
                        with open(thumbnail_path, 'wb') as thumbnail_file:
                            thumbnail_file.write(response.content)

                # If 'With Info' is selected, save video information
                if info_var.get():
                    sanitized_title = sanitize_filename(info_dict['title'])
                    info_path = os.path.join(output_directory, f"{sanitized_title}_info.txt")
                    with open(info_path, 'w', encoding='utf-8') as info_file:  # Ensure UTF-8 encoding
                        info_file.write(f"Title: {info_dict['title']}\n")
                        info_file.write(f"ID: {info_dict['id']}\n")
                        info_file.write(f"Length: {info_dict['duration']} seconds\n")
                        info_file.write(f"Views: {info_dict.get('view_count', 'N/A')}\n")
                        info_file.write(f"Description: {info_dict.get('description', 'N/A')}\n")

            status_text.insert(tk.END, f'Download of {info_dict["title"]} successful!\n')
            status_text.see(tk.END)  # Scroll to the end

        except Exception as e:
            status_text.insert(tk.END, f'Error downloading {url}: {str(e)}\n', 'error')
            status_text.see(tk.END)  # Scroll to the end

    def download_thread():
        for url in urls:
            download_single_video(url)

    def progress_hook(d):
        if d['status'] == 'downloading':
            # Use regular expression to find the numeric percentage
            progress_str = d['_percent_str']
            progress = float(re.sub(r'[^\d.]', '', progress_str))  # Remove any non-numeric characters
            progress_bar['value'] = progress
            window.update_idletasks()

    # Check if a directory is selected and if it is valid
    if not output_directory or not os.path.isdir(output_directory):
        status_text.insert(tk.END, 'Please select a valid directory.\n', 'error')
        return

    if not urls:
        status_text.insert(tk.END, 'Please enter YouTube URLs.\n', 'error')
        return

    Thread(target=download_thread).start()
    status_text.insert(tk.END, 'Downloading...\n', 'info')
    progress_bar['value'] = 0

# Function to clear fields
def clear_fields():
    url_entry.delete("1.0", tk.END)
    directory_label.config(text='Selected Directory: None')
    status_text.delete("1.0", tk.END)
    progress_bar['value'] = 0

# Function to open directory
def open_directory():
    output_directory = directory_label.cget("text").replace('Selected Directory: ', '')
    if output_directory and os.path.exists(output_directory):
        webbrowser.open(output_directory)
    else:
        messagebox.showerror("Error", "Directory not found")

# Create main window
window = tk.Tk()
window.title('Mini Download')
window.geometry('800x600')
window.resizable(False, False)

# Set application icon
window.iconbitmap(logo_path)

# Load the image
background_label = tk.Label(window, bg="#000000")  # Silver color
background_label.place(relwidth=1, relheight=1)  # Make it fill the entire window

# Create label for "Scan pay for coffee" text
scan_pay_label = tk.Label(window, text="Scan to pay for my coffee", font=("Fixedsys", 15), bg='#ff0090', fg='white')
scan_pay_label.place(x=575, y=10)

# URL entry
url_label = tk.Label(window, text='Enter YouTube URLs', bg='#000000', fg='white')
url_label.pack(pady=10, padx=10, anchor=tk.W)

url_entry = scrolledtext.ScrolledText(window, height=5, width=50, bg='#000000', fg='white', insertbackground='white')
url_entry.pack(padx=10, anchor=tk.W)

# Save options
save_frame = tk.Frame(window, bg='#000000')
save_frame.pack(pady=10, padx=10, anchor=tk.W)
tk.Label(save_frame, text='Save Format:', bg='#000000', fg='white').pack(side=tk.LEFT, padx=10)
save_option = tk.StringVar(value='title')
tk.Radiobutton(save_frame, text='Title', variable=save_option, value='title', bg='#000000', fg='white', selectcolor='#000000').pack(side=tk.LEFT, padx=10)
tk.Radiobutton(save_frame, text='ID Video', variable=save_option, value='id', bg='#000000', fg='white', selectcolor='#000000').pack(side=tk.LEFT, padx=10)
tk.Radiobutton(save_frame, text='Title + ID Video', variable=save_option, value='both', bg='#000000', fg='white', selectcolor='#000000').pack(side=tk.LEFT, padx=10)

# Video quality selection
quality_frame = tk.Frame(window, bg='#000000')
quality_frame.pack(pady=10, padx=10, anchor=tk.W)
tk.Label(quality_frame, text='Quality:', bg='#000000', fg='white').pack(side=tk.LEFT, padx=10)
quality_var = tk.StringVar(value='highest')
quality_combobox = ttk.Combobox(quality_frame, textvariable=quality_var, values=['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p'], state='readonly')
quality_combobox.pack(side=tk.LEFT, padx=10)

# Extra options in a horizontal row
extra_frame = tk.Frame(window, bg='#000000')
extra_frame.pack(pady=10, padx=10, anchor=tk.W)
tk.Label(extra_frame, text='Options:', bg='#000000', fg='white').pack(side=tk.LEFT, padx=10)

thumbnail_var = tk.BooleanVar()
info_var = tk.BooleanVar()
audio_only_var = tk.BooleanVar()

tk.Checkbutton(extra_frame, text='With Thumbnail', variable=thumbnail_var, bg='#000000', fg='white', selectcolor='#000000').pack(side=tk.LEFT, padx=10)
tk.Checkbutton(extra_frame, text='With Info', variable=info_var, bg='#000000', fg='white', selectcolor='#000000').pack(side=tk.LEFT, padx=10)
tk.Checkbutton(extra_frame, text='Audio-only', variable=audio_only_var, bg='#000000', fg='white', selectcolor='#000000').pack(side=tk.LEFT, padx=10)

# Select directory button
select_directory_button = tk.Button(window, text='Select Directory', command=select_directory, bg='#003399', fg='white')
select_directory_button.pack(pady=5, padx=20, ipadx=10, anchor=tk.W)

# Directory label
directory_label = tk.Label(window, text='Selected Directory: None', bg='#000000', fg='white')
directory_label.pack(pady=5, padx=10, anchor=tk.W)

# Frame for buttons
button_frame = tk.Frame(window, bg='#000000')
button_frame.pack(pady=10, padx=10, anchor=tk.W)

# Download button
download_video_button = tk.Button(button_frame, text='Download', command=download_video, bg='#003399', fg='white')
download_video_button.pack(side=tk.LEFT, padx=10, ipadx=10)

# Clear button
clear_button = tk.Button(button_frame, text='Clear', command=clear_fields, bg='#003399', fg='white')
clear_button.pack(side=tk.LEFT, padx=10, ipadx=10)

# Open directory button
open_directory_button = tk.Button(button_frame, text='Open Directory', command=open_directory, bg='#003399', fg='white')
open_directory_button.pack(side=tk.LEFT, padx=10, ipadx=10)

# Progress bar
progress_bar = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=400, mode='determinate', style='TProgressbar')
progress_bar.pack(pady=10, padx=10, anchor=tk.W)

# Status text area
status_text = scrolledtext.ScrolledText(window, height=10, width=100, bg='#000000', fg='white', insertbackground='white')
status_text.pack(pady=10, padx=10, anchor=tk.W)
status_text.tag_config('error', foreground='red')
status_text.tag_config('info', foreground='green')



# Function to toggle QR code display while keeping button size the same
def toggle_qr_code():
    global qr_label, qr_photo

    if 'qr_label' in globals() and qr_label.winfo_exists():  
        # Hide QR code
        qr_label.destroy()
        del qr_label  # Remove from globals
        load_qr_button.config(text="Enable QR")  # Update button text
    else:
        # Show QR code
        try:
            if qr_code_path and os.path.exists(qr_code_path):
                qr_image = Image.open(qr_code_path)
                qr_image = qr_image.resize((300, 300), Image.LANCZOS)  # Keep size 300x300
                qr_photo = ImageTk.PhotoImage(qr_image)

                qr_label = tk.Label(window, image=qr_photo, bg='#fcfcfc')
                qr_label.image = qr_photo
                qr_label.place(relx=1, rely=0, anchor=tk.NE, x=-20, y=80)  # Position stays same

                load_qr_button.config(text="Turn off QR")  # Update button text
            else:
                messagebox.showerror("Error", "QR code image not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load QR code image: {e}")

# Add a button to toggle QR code display with fixed size
load_qr_button = tk.Button(window, text="Enable QR", command=toggle_qr_code, bg='#003399', fg='white', width=9, height=1)
load_qr_button.place(relx=1, rely=0, anchor=tk.NE, x=-152, y=40)  # Position stays same

# Styles for progress bars
style = ttk.Style(window)
style.configure('TProgressbar', background='blue')
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Update the paths to use resource_path
logo_path = resource_path("Logo.ico")
qr_code_path = resource_path("qr.jpg")
ffmpeg_path = resource_path("_internal/ffmpeg.exe")
# Run the main loop
window.mainloop()