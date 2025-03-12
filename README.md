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
- **Enhanced File Information**: View size, type, duration, and bitrate of downloaded files
- **Download History**: Maintains a log of all downloaded media (for personal use)
- **Performance Optimized**: Uses session state to minimize redundant operations

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
- Streamlit
- yt-dlp
- FFmpeg (used for media processing)
- Pillow (for image handling)
- Requests (for fetching thumbnails)
- Pandas (for format tables)

## Installation

```bash
# Clone the repository
git clone [your-repository-url]

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Technical Details

This application uses:

- **Streamlit** for the web interface
- **yt-dlp** for downloading and processing media
- **FFmpeg** for format conversion and embedding subtitles
- **Pillow** for thumbnail image processing
- **Requests** for fetching remote resources
- **Pandas** for data formatting and display
- **UTF-8 Encoding** for proper handling of international characters and symbols
