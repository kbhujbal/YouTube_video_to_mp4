from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yt_dlp
import os
import re
from pathlib import Path
import uuid

app = FastAPI()

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
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video.url, download=False)

            if not info:
                raise HTTPException(status_code=400, detail="Could not extract video information")

            # Get available formats (video + audio combined)
            formats = []
            seen_resolutions = set()

            for f in info.get('formats', []):
                # Only include formats that have both video and audio or are mp4
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    resolution = f.get('resolution', 'unknown')
                    height = f.get('height')
                    format_id = f.get('format_id')
                    ext = f.get('ext', 'mp4')
                    filesize = f.get('filesize') or f.get('filesize_approx', 0)

                    if height and height not in seen_resolutions:
                        seen_resolutions.add(height)
                        formats.append({
                            'format_id': format_id,
                            'resolution': f"{height}p",
                            'ext': ext,
                            'filesize': filesize,
                            'filesize_mb': round(filesize / (1024 * 1024), 2) if filesize else None,
                            'fps': f.get('fps'),
                            'vcodec': f.get('vcodec', 'unknown')[:20],
                        })

            # Sort by resolution (height) in descending order
            formats.sort(key=lambda x: int(x['resolution'].replace('p', '')), reverse=True)

            # If no combined formats found, suggest best video + audio merge
            if not formats:
                # Get best video-only formats
                video_formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') == 'none']
                for f in video_formats:
                    height = f.get('height')
                    if height and height not in seen_resolutions:
                        seen_resolutions.add(height)
                        formats.append({
                            'format_id': f.get('format_id'),
                            'resolution': f"{height}p",
                            'ext': 'mp4',
                            'filesize': f.get('filesize') or f.get('filesize_approx', 0),
                            'filesize_mb': round((f.get('filesize') or f.get('filesize_approx', 0)) / (1024 * 1024), 2),
                            'fps': f.get('fps'),
                            'vcodec': f.get('vcodec', 'unknown')[:20],
                            'needs_merge': True
                        })
                formats.sort(key=lambda x: int(x['resolution'].replace('p', '')), reverse=True)

            return {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader', 'Unknown'),
                'formats': formats[:10]  # Limit to top 10 qualities
            }

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YouTube URL or video unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.post("/api/download")
async def download_video(request: DownloadRequest):
    """Download video in specified quality"""
    try:
        # Clean old files before downloading new one
        clean_old_files()

        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]

        ydl_opts = {
            'format': f'{request.format_id}+bestaudio/best',  # Download video + best audio
            'outtmpl': str(DOWNLOAD_DIR / f'{unique_id}_%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',  # Merge to mp4
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)

            # Find the downloaded file
            filename = ydl.prepare_filename(info)

            # Handle cases where the extension might be different
            if not os.path.exists(filename):
                # Try to find the file with the unique_id
                files = list(DOWNLOAD_DIR.glob(f"{unique_id}_*"))
                if files:
                    filename = str(files[0])
                else:
                    raise HTTPException(status_code=500, detail="Downloaded file not found")

            if not os.path.exists(filename):
                raise HTTPException(status_code=500, detail="Downloaded file not found")

            # Get just the filename without path
            file_basename = os.path.basename(filename)

            return FileResponse(
                path=filename,
                filename=file_basename,
                media_type='video/mp4',
                headers={
                    "Content-Disposition": f'attachment; filename="{file_basename}"'
                }
            )

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up files on shutdown"""
    clean_old_files()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
