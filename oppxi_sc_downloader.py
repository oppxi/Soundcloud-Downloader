# main.py
import yt_dlp
import os
import re
import platform
import sys
from colorama import init, Fore, Style

init(autoreset=True)

if platform.system() == "Windows":
    import ctypes

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, WOAS, TIT2, error

def get_console_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80

def center_text(text, width=None):
    """

    """
    if width is None:
        width = get_console_width()
    
    clean_text = re.sub(r'\x1b\[[0-9;]*[mG]', '', text)
    text_length = len(clean_text)
    
    if text_length >= width:
        return text
    
    padding = (width - text_length) // 2
    return " " * padding + text + " " * (width - text_length - padding)

def clear_screen():
    """

    """
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def set_window_title(title):
    """

    """
    try:
        if platform.system() == "Windows":
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif platform.system() in ("Linux", "Darwin"):
            sys.stdout.write(f"\033]0;{title}\007")
            sys.stdout.flush()
        else:
            print(center_text(f"{Fore.YELLOW}Setting window title not supported on {platform.system()}"))
    except Exception as e:
        print(center_text(f"{Fore.RED}Error setting window title: {e}"))

def existing_function():
    header = f"{Fore.CYAN}=========================== Existing Features ==========================="
    print(center_text(header))

def clean_title(title):
    """

    """
    if not title or title.lower() == 'unknown title':
        return "Untitled"
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def validate_url(url):
    """

    """
    if not url:
        return False, "URL cannot be empty."
    if not re.match(r'^https?://(www\.)?soundcloud\.com/[\w-]+(/[\w-]+)?$', url):
        return False, "Invalid SoundCloud URL. Please provide a valid track or playlist URL."
    return True, "URL is valid."

def download_soundcloud(url, output_dir="downloads"):
    """

    """
    is_valid, message = validate_url(url)
    if not is_valid:
        print(center_text(f"{Fore.RED} {message}"))
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(artist)s - %(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'embedthumbnail': True,
        'writethumbnail': True,
        'addmetadata': True,
        'postprocessor_args': ['-metadata', 'comment=Downloaded from SoundCloud'],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:  # Playlist
                for entry in info['entries']:
                    if entry:
                        add_custom_metadata(entry, url)
            else:  # Single track
                add_custom_metadata(info, url)
                
        print(center_text(f"{Fore.GREEN} Download completed successfully!"))
    except Exception as e:
        print(center_text(f"{Fore.RED} Download failed: {str(e)}"))

def add_custom_metadata(info, source_url):
    """

    """
    try:
        title = info.get('title', 'Unknown Title')
        cleaned_title = clean_title(title)
        
        artist = info.get('artist', 'Unknown Artist')
        if not artist or artist.lower() == 'unknown artist':
            artist = "SoundCloud Artist"
        
        filename = f"downloads/{artist} - {cleaned_title}.mp3"
        
        if os.path.exists(filename):
            audio = MP3(filename, ID3=ID3)
            
            try:
                audio.add_tags()
            except error:
                pass
            
            audio.tags.add(TPE1(encoding=3, text=artist))
            audio.tags.add(TIT2(encoding=3, text=cleaned_title))
            audio.tags.add(WOAS(encoding=3, url=source_url))
            
            audio.save(v2_version=3)
            print(center_text(f"{Fore.GREEN} Metadata set for '{cleaned_title}' by {artist}"))
        else:
            print(center_text(f"{Fore.YELLOW} File not found: {filename}"))
    except Exception as e:
        print(center_text(f"{Fore.RED} Metadata error for '{cleaned_title}': {str(e)}"))

if __name__ == "__main__":
    clear_screen()
    set_window_title("SoundLoader by OPPXI")
    
    print(center_text(f"{Fore.MAGENTA}Soundcloud Downloader v1.0 by OPPXI"))
    print(center_text(f"{Fore.MAGENTA}=================================="))
    existing_function()
    
    prompt = f"{Fore.CYAN}Enter SoundCloud URL (track/playlist): "
    print(center_text(prompt), end="")
    print(Style.RESET_ALL, end="")
    url = input().strip()
    download_soundcloud(url)