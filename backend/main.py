from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import yt_dlp
import os
import re
from pathlib import Path
import uuid
import urllib.parse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    clean_old_files()

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create downloads directory
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

class VideoURL(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str

def clean_old_files():
    """Clean up old downloaded files"""
    try:
        for file in DOWNLOAD_DIR.glob("*"):
            if file.is_file():
                file.unlink()
    except Exception as e:
        print(f"Error cleaning files: {e}")

def sanitize_filename(filename: str) -> str:
    """Remove special characters from filename"""
    return re.sub(r'[^\w\s-]', '', filename).strip()

@app.get("/")
async def root():
    return {"message": "YouTube Video Downloader API"}

@app.post("/api/video-info")
async def get_video_info(video: VideoURL):
    """Get available video qualities for a YouTube URL"""
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video.url, download=False)

            if not info:
                raise HTTPException(status_code=400, detail="Could not extract video information")

            # Get available formats
            formats = []
            seen_resolutions = {}  # Changed to dict to store format_id for each resolution

            all_formats = info.get('formats', [])
            print(f"\n=== Processing {len(all_formats)} total formats ===")

            # Collect all video formats (both combined and video-only)
            for f in all_formats:
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')
                height = f.get('height')
                format_id = f.get('format_id')
                ext = f.get('ext', 'unknown')

                # Skip audio-only or formats without height
                if vcodec == 'none' or not height:
                    continue

                print(f"Format {format_id}: {height}p, vcodec={vcodec}, acodec={acodec}, ext={ext}")

                # Prefer combined formats (video+audio) over video-only for the same resolution
                if height not in seen_resolutions or (acodec != 'none' and seen_resolutions[height].get('has_audio') == False):
                    filesize = f.get('filesize') or f.get('filesize_approx', 0)
                    has_audio = acodec != 'none'

                    seen_resolutions[height] = {
                        'format_id': format_id,
                        'resolution': f"{height}p",
                        'ext': ext if ext != 'unknown' else 'mp4',
                        'filesize': filesize,
                        'filesize_mb': round(filesize / (1024 * 1024), 2) if filesize else None,
                        'fps': f.get('fps'),
                        'vcodec': vcodec[:20] if vcodec else 'unknown',
                        'has_audio': has_audio
                    }

            # Convert to list and remove the has_audio flag
            formats = []
            for height, fmt_data in seen_resolutions.items():
                fmt = dict(fmt_data)
                fmt.pop('has_audio', None)  # Remove internal flag
                formats.append(fmt)

            # Sort by resolution (height) in descending order
            formats.sort(key=lambda x: int(x['resolution'].replace('p', '')), reverse=True)

            print(f"\n=== Found {len(formats)} unique resolutions ===")
            for fmt in formats:
                print(f"  {fmt['resolution']}: format_id={fmt['format_id']}, {fmt['ext']}")

            return {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader', 'Unknown'),
                'formats': formats  # Return all formats
            }

    except yt_dlp.utils.DownloadError as e:
        print(f"DownloadError: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid YouTube URL or video unavailable: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.post("/api/download")
async def download_video(request: DownloadRequest):
    """Download video in specified quality"""
    try:
        print(f"\n=== Download Request ===")
        print(f"URL: {request.url}")
        print(f"Format ID: {request.format_id}")

        # Clean old files before downloading new one
        clean_old_files()

        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]

        ydl_opts = {
            'format': f'{request.format_id}+bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': str(DOWNLOAD_DIR / f'{unique_id}_%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        print(f"Download options: {ydl_opts}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Starting download...")
            info = ydl.extract_info(request.url, download=True)

            # Find the downloaded file
            print(f"Looking for downloaded file...")
            files = list(DOWNLOAD_DIR.glob(f"{unique_id}_*"))
            print(f"Found files: {files}")

            if not files:
                raise HTTPException(status_code=500, detail="Downloaded file not found")

            filename = str(files[0])
            print(f"Using file: {filename}")

            if not os.path.exists(filename):
                raise HTTPException(status_code=500, detail=f"File does not exist: {filename}")

            # Get just the filename without path
            file_basename = os.path.basename(filename)
            print(f"Sending file: {file_basename}")

            # Sanitize filename for HTTP header (remove non-ASCII characters)
            # Keep the original filename safe for download
            safe_basename = file_basename.encode('ascii', 'ignore').decode('ascii')
            if not safe_basename or safe_basename == '':
                safe_basename = 'video.mp4'

            # Use RFC 5987 encoding for proper Unicode support in Content-Disposition
            encoded_filename = urllib.parse.quote(file_basename)

            print(f"Safe filename for header: {safe_basename}")

            return FileResponse(
                path=filename,
                media_type='video/mp4',
                headers={
                    "Content-Disposition": f"attachment; filename=\"{safe_basename}\"; filename*=UTF-8''{encoded_filename}"
                }
            )

    except yt_dlp.utils.DownloadError as e:
        error_msg = f"Download failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error downloading video: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
