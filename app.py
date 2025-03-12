import streamlit as st
import os
import tempfile
from yt_dlp import YoutubeDL
import time
import json
import subprocess
from pathlib import Path
import datetime
from PIL import Image
import requests
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Media Downloader", page_icon="🎵")

# Check for FFmpeg availability
def is_ffmpeg_available():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

st.title("Media Downloader")
st.write("Download audio or video from various platforms")

# Set environment-specific paths
is_deployed = os.environ.get('STREAMLIT_DEPLOYED', '') == 'true'
if is_deployed:
    # In deployed environment, use temp directory
    DOWNLOAD_DIR = tempfile.gettempdir()
    # Display message about download location
    st.info("You are using the deployed version. Files will be available for download but not saved permanently.")
else:
    # In local environment, use user's Downloads folder
    DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

# Show warning if FFmpeg is not available
if not is_ffmpeg_available():
    st.warning("FFmpeg is not available. Some features like audio extraction and subtitle embedding may not work. " 
               "If you're using the deployed version, please contact the administrator.")

# Set up history file path (try to use app directory, fallback to temp dir if needed)
try:
    HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download_history.json")
except Exception:
    HISTORY_FILE = os.path.join(tempfile.gettempdir(), "download_history.json")

# Initialize session state
if 'previous_url' not in st.session_state:
    st.session_state.previous_url = ""
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'formats_info' not in st.session_state:
    st.session_state.formats_info = None

# Input URL
url = st.text_input("Enter URL:", placeholder="https://www.youtube.com/watch?v=...")

# Function to load download history
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"Error loading history: {str(e)}")
            return []
    return []

# Function to save download history
def save_to_history(entry):
    try:
        history = load_history()
        history.append(entry)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # Silent fail in deployed environment
        print(f"Could not save download history: {str(e)}")

# Function to format duration in HH:MM:SS.mmm format
def format_duration(seconds):
    # Ensure we have a float for accurate calculations
    seconds_float = float(seconds)
    
    hours, remainder = divmod(seconds_float, 3600)
    minutes, secs = divmod(remainder, 60)
    
    # Get integer parts
    hours_int = int(hours)
    minutes_int = int(minutes)
    seconds_int = int(secs)
    
    # Get milliseconds (remaining fractional part)
    milliseconds = int((secs - seconds_int) * 1000)
    
    return f"{hours_int:02d}:{minutes_int:02d}:{seconds_int:02d}.{milliseconds:03d}"

# Function to safely format numeric values
def safe_format_number(value, format_str, default="N/A"):
    if value is None:
        return default
    try:
        if isinstance(value, (int, float)):
            return format_str.format(value)
        return default
    except:
        return default

# Function to get formats info with improved error handling
def get_formats_info(video_url):
    try:
        if not video_url:
            return []
            
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if not info:
                return []
                
            formats = info.get('formats', [])
            if not formats:
                return []
            
            # Create a DataFrame for better display
            formats_data = []
            for f in formats:
                format_id = str(f.get('format_id', 'N/A'))
                ext = str(f.get('ext', 'N/A'))
                resolution = str(f.get('resolution', 'N/A'))
                
                # Handle FPS field properly - ensure it's a string
                fps = f.get('fps')
                if fps is not None and fps != 'N/A':
                    try:
                        fps = f"{float(fps):.1f}"
                    except (ValueError, TypeError):
                        fps = 'N/A'
                else:
                    fps = 'N/A'
                
                # Safe handling of file size
                file_size = f.get('filesize')
                if file_size is not None:
                    try:
                        file_size = f"{file_size / 1024 / 1024:.2f} MB"
                    except (TypeError, ValueError):
                        file_size = "N/A"
                else:
                    file_size = "N/A"
                
                # Safe handling of bitrate
                tbr = f.get('tbr')
                if tbr is not None:
                    try:
                        tbr = f"{float(tbr):.1f} kbps"
                    except (TypeError, ValueError):
                        tbr = "N/A"
                else:
                    tbr = "N/A"
                
                format_note = str(f.get('format_note', ''))
                
                formats_data.append({
                    "ID": format_id,
                    "Extension": ext,
                    "Resolution": resolution,
                    "FPS": fps,
                    "Size": file_size,
                    "Bitrate": tbr,
                    "Note": format_note
                })
            
            # Create DataFrame and ensure consistent types
            if formats_data:
                df = pd.DataFrame(formats_data)
                # Ensure all columns are treated as strings to avoid type conversion issues
                for col in df.columns:
                    df[col] = df[col].astype(str)
                return df
            return []
            
    except Exception as e:
        # Don't display the error in the UI, just log it and return empty list
        print(f"Error fetching formats: {str(e)}")
        return []

# Preview and info section - only update when URL changes
if url != st.session_state.previous_url:
    st.session_state.video_info = None
    st.session_state.formats_info = None
    
    if url:
        try:
            with st.spinner("Fetching video information..."):
                # Extract info without downloading
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                }
                with YoutubeDL(ydl_opts) as ydl:
                    video_info = ydl.extract_info(url, download=False)
                    if video_info:
                        st.session_state.video_info = video_info
                        # Only get formats if we successfully got video info
                        st.session_state.formats_info = get_formats_info(url)
                        st.session_state.previous_url = url
        except Exception as e:
            st.error(f"Error: Could not fetch video information. Please check the URL.")
            print(f"Error details: {str(e)}")

# Display video info if available
if st.session_state.video_info:
    video_info = st.session_state.video_info
    
    # Display thumbnail at full width
    if 'thumbnail' in video_info:
        try:
            response = requests.get(video_info['thumbnail'])
            img = Image.open(BytesIO(response.content))
            st.image(img, caption="", use_container_width=True)
        except Exception:
            st.warning("Thumbnail preview unavailable")
    
    # Display video information below the thumbnail
    st.header(video_info.get('title', 'Unknown Title'))
    
    # Create a more organized info section
    info_cols = st.columns(2)
    
    # Duration in minutes:seconds format
    if 'duration' in video_info:
        mins, secs = divmod(int(video_info['duration']), 60)
        with info_cols[0]:
            st.write(f"**Duration:** {mins}:{secs:02d}")
    
    # Uploader info
    if 'uploader' in video_info:
        with info_cols[1]:
            st.write(f"**Uploader:** {video_info['uploader']}")
    
    # View count
    if 'view_count' in video_info:
        with info_cols[0]:
            st.write(f"**Views:** {video_info['view_count']:,}")
    
    # Upload date
    if 'upload_date' in video_info:
        date = video_info['upload_date']
        if len(date) == 8:  # Format YYYYMMDD
            formatted_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
            with info_cols[1]:
                st.write(f"**Upload date:** {formatted_date}")
                
    # Description (expandable)
    if 'description' in video_info and video_info['description']:
        with st.expander("Show Description"):
            st.markdown(video_info['description'])
    
    # Add a separator
    st.markdown("---")

# Download options
download_type = st.radio("Download Type:", ["Audio", "Video"])

# Audio options (show if audio is selected)
if download_type == "Audio":
    audio_format = st.selectbox("Audio Format:", 
                               ["m4a", "mp3", "opus", "flac", "wav", "aac", "vorbis"])
    audio_quality = st.slider("Quality (0=best, 10=worst):", 
                             min_value=0.0, max_value=10.0, value=0.0, step=0.1)

# Video options (show if video is selected)
else:
    video_format = st.selectbox("Video Format:", 
                               ["mp4", "webm", "mkv", "flv", "avi", "mov"])
    fetch_subtitle = st.checkbox("Download Subtitles", value=False)
    
    if fetch_subtitle:
        subtitle_language = st.selectbox("Subtitle Language:", 
                                        ["all", "en", "es", "fr", "ja", "zh-Hans", "zh-Hant"])
        subtitle_file_type = st.selectbox("Subtitle Format:", 
                                         ["best", "srt", "vtt", "ass"])

# Format table
if isinstance(st.session_state.formats_info, pd.DataFrame) and not st.session_state.formats_info.empty and url:
    with st.expander("Available Formats", expanded=False):
        try:
            st.dataframe(st.session_state.formats_info, use_container_width=True)
        except Exception as e:
            st.info("Format information available but cannot be displayed in table format.")
            print(f"Error displaying formats table: {e}")
else:
    # Only show the formats section if URL is provided
    if url:
        with st.expander("Available Formats", expanded=False):
            st.info("No detailed format information available")

# Download button
if st.button("Download"):
    if not url:
        st.error("Please enter a valid URL")
    else:
        with st.spinner("Downloading..."):
            try:
                # Set download path based on environment
                if is_deployed:
                    # For deployed version, use a temporary directory
                    # with a simplified filename to avoid path issues
                    file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_template = f'media_{file_timestamp}.%(ext)s'
                    download_path = os.path.join(DOWNLOAD_DIR, file_template)
                else:
                    # For local version, use the regular path with full title
                    download_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

                if download_type == "Audio":
                    # Audio download logic
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': audio_format,
                            'preferredquality': str(audio_quality),
                        }],
                        'outtmpl': download_path,
                        'addmetadata': True,
                        'embedchapters': True,
                        'embedthumbnail': True,
                        'prefer_ffmpeg': True,
                        'verbose': False,
                    }
                else:
                    # Video download logic
                    ydl_opts = {
                        'format': f'bestvideo[ext={video_format}]+bestaudio[ext=m4a]/best[ext={video_format}]',
                        'merge_output_format': video_format,
                        'outtmpl': download_path,
                        'addmetadata': True,
                        'embedchapters': True,
                        'embedthumbnail': True,
                        'prefer_ffmpeg': True,
                    }
                    
                    if fetch_subtitle:
                        ydl_opts.update({
                            'subtitleslangs': [subtitle_language],
                            'subtitlesformat': subtitle_file_type,
                            'writesubtitles': True,
                            'embedsubtitles': True,
                            'postprocessors': [{
                                'key': 'FFmpegEmbedSubtitle',
                            }],
                        })
                
                # Execute download
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    downloaded_file = ydl.prepare_filename(info)
                    
                    # Handle extension change for audio files
                    if download_type == "Audio":
                        base = os.path.splitext(downloaded_file)[0]
                        downloaded_file = f"{base}.{audio_format}"
                
                # Check if file exists and show success message
                if os.path.exists(downloaded_file):
                    file_name = os.path.basename(downloaded_file)
                    file_size = round(os.path.getsize(downloaded_file) / (1024 * 1024), 3)
                    
                    # Calculate duration and bitrate
                    duration_seconds = info.get('duration', 0)
                    duration_formatted = format_duration(duration_seconds)
                    
                    # Calculate bitrate (file size in bits / duration in seconds)
                    file_size_bits = os.path.getsize(downloaded_file) * 8
                    bitrate = round(file_size_bits / 1000 / duration_seconds, 3) if duration_seconds > 0 else 0
                    
                    # Log to download history
                    history_entry = {
                        "title": info.get('title', 'Unknown Title'),
                        "url": url,
                        "type": download_type,
                        "format": audio_format if download_type == "Audio" else video_format,
                        "file_path": downloaded_file,
                        "file_size_mb": file_size,
                        "download_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "metadata": {
                            "uploader": info.get('uploader', 'Unknown'),
                            "duration": duration_seconds,
                            "view_count": info.get('view_count', 0),
                            "upload_date": info.get('upload_date', '')
                        }
                    }
                    save_to_history(history_entry)
                    
                    # Display success message
                    st.success("Downloaded Successfully")
                    
                    # Add a separator above file information
                    st.markdown("---")
                    
                    # Display enhanced file information
                    st.subheader("File Information")
                    st.write(f"Size: {file_size} MB")
                    st.write(f"Type: {os.path.splitext(file_name)[1][1:]}")
                    st.write(f"Duration: {duration_formatted}")
                    st.write(f"Bitrate: {bitrate} kbps")

                    # After download, in deployed environment, provide download link
                    if is_deployed and os.path.exists(downloaded_file):
                        with open(downloaded_file, "rb") as file:
                            file_name = os.path.basename(downloaded_file)
                            # Create a download button for the user to get the file
                            st.download_button(
                                label="Download your file",
                                data=file,
                                file_name=file_name,
                                mime=f'{"audio" if download_type == "Audio" else "video"}/{os.path.splitext(file_name)[1][1:]}'
                            )
                        st.info("In the deployed version, files aren't saved to your Downloads folder. Use the download button above to save the file to your device.")
                else:
                    st.error("Download failed or file not found")
            
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")