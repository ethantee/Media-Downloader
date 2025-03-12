# Media Downloader

A streamlined web application for downloading audio and video content from various online platforms including YouTube, Vimeo, SoundCloud, and many others.

## Features

- **Content Preview**: See thumbnails and video information before downloading
- **Format Information**: View available format options before downloading
- **Media Format Selection**: Download content as audio or video
- **Multiple Format Support**:
  - **Audio**: MP3, M4A, OPUS, FLAC, WAV, AAC, Vorbis
  - **Video**: MP4, WebM, MKV, FLV, AVI, MOV
- **Quality Control**: Adjust audio quality settings
- **Subtitle Options**: Download and embed subtitles in various languages and formats
- **Metadata Inclusion**: Preserves metadata, thumbnails, and chapters from the original content
- **Unicode Support**: Full support for international characters in titles and filenames
- **Direct Downloads**: Files are saved directly to your Downloads folder
- **File Information**: View size, type, duration, and bitrate of downloaded files

## How to Use

1. Enter the URL of the media you want to download
2. Preview the content and check available information
3. Explore available formats (expandable section)
4. Select whether you want audio or video
5. Choose your preferred format and quality settings
6. Click the "Download" button
7. The file will be saved directly to your Downloads folder

## Requirements

- Python 3.11 or higher
- Streamlit (for the web interface)
- yt-dlp (for downloading media)
- FFmpeg (used for media processing)
- Pillow (for image handling)
- Requests (for fetching thumbnails)
- Pandas (for format tables)

## Installation

### Option 1: Using pip (Traditional)

```bash
# Clone the repository
git clone https://github.com/ethantee/Media-Downloader.git

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Option 2: Using uv (Fast Python Package Manager)

```bash
# Install uv globally
pip install uv

# Clone the repository 
git clone https://github.com/ethantee/Media-Downloader.git
cd Media-Downloader

# Create a virtual environment
uv venv

# Activate the virtual environment
# On Windows
.\.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run the application
streamlit run app.py
```
