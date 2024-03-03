# YouTube Video Downloader

A modern, full-stack web application that allows users to download YouTube videos in various quality options. Built with Python (FastAPI) backend and Next.js (React) frontend with real-time download progress tracking.

## Features

- 📥 Download YouTube videos in multiple quality options (144p to 4K)
- 🎯 Only shows quality options actually available for each video
- 💫 Real-time download progress indicator with percentage display
- 📊 File size estimation for all quality options
- 🎨 Clean and modern user interface
- 🖼️ Video thumbnail and metadata preview
- 🔄 Automatic quality detection and format merging
- 📱 Responsive design for all devices
- ⚡ Fast downloads with optimized streaming

## Tech Stack

### Backend
- Python 3.8+
- FastAPI - Modern web framework
- yt-dlp - YouTube video downloader
- uvicorn - ASGI server

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Axios

## Project Structure

```
YouTube video to mp4/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .gitignore
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Main page component
│   │   └── globals.css      # Global styles
│   ├── package.json         # Node dependencies
│   ├── tsconfig.json        # TypeScript config
│   ├── tailwind.config.ts   # Tailwind config
│   ├── next.config.js       # Next.js config
│   └── .gitignore
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- FFmpeg (required for video/audio merging)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

The frontend will start on `http://localhost:3000`

## Usage

1. **Start the backend server**:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   ```
   Backend will run on `http://localhost:8000`

2. **Start the frontend server** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on `http://localhost:3000`

3. **Use the application**:
   - Open `http://localhost:3000` in your browser
   - Paste a YouTube video URL
   - Click "Get Info" to fetch available quality options
   - Browse available formats with file sizes
   - Select your preferred quality
   - Click "Download Video"
   - Watch the real-time progress bar
   - Video will download to your browser's default download folder

## API Endpoints

### POST `/api/video-info`
Fetch video information and available quality options

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "title": "Video Title",
  "thumbnail": "https://...",
  "duration": 300,
  "uploader": "Channel Name",
  "formats": [
    {
      "format_id": "22",
      "resolution": "720p",
      "ext": "mp4",
      "filesize": 52428800,
      "filesize_mb": 50.0,
      "fps": 30,
      "vcodec": "avc1.64001F"
    }
  ]
}
```

### POST `/api/download`
Download video in specified quality

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "format_id": "22"
}
```

**Response:**
File download stream (video/mp4)

## How It Works

### Download Flow
1. **User Input**: User pastes YouTube URL and clicks "Get Info"
2. **Backend Processing**:
   - Extracts video metadata using yt-dlp
   - Analyzes all available formats (video-only and combined streams)
   - Estimates file sizes using bitrate calculations when direct size unavailable
   - Returns format list sorted by quality
3. **Format Selection**: User selects desired quality from available options
4. **Download Process**:
   - Backend downloads video from YouTube (with progress tracking)
   - Merges video and audio streams if necessary using FFmpeg
   - Streams file to user's browser
   - Frontend displays real-time download progress
5. **Completion**: Browser saves video to user's Downloads folder
6. **Cleanup**: Backend automatically deletes temporary files

### File Storage
- **Server**: Videos are temporarily stored in `backend/downloads/` during processing
- **User**: Final video downloads to browser's default download folder
- **Cleanup**: Temporary files are automatically deleted after serving

### File Size Estimation
When YouTube doesn't provide direct file sizes, the application estimates using:
```
File Size (MB) = (Bitrate in kbps × Duration in seconds × 1000) ÷ (8 × 1024 × 1024)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. yt-dlp Errors (HTTP 400, 403, nsig extraction failed)
**Cause**: Outdated yt-dlp version. YouTube frequently updates their API.

**Solution**: Update yt-dlp to the latest version
```bash
cd backend
source venv/bin/activate
pip install --upgrade yt-dlp
```

Verify version (should be 2024.x.x or 2025.x.x):
```bash
yt-dlp --version
```

#### 2. "No downloadable formats found"
**Cause**: Video is age-restricted, region-locked, or private

**Solutions**:
- Try a different video
- Check if the video is accessible in your region
- Ensure the video is public

#### 3. Unicode Filename Errors
**Cause**: Video titles with special characters (｜, emojis, etc.)

**Solution**: Already handled! The application uses RFC 5987 encoding for proper Unicode support.

#### 4. FFmpeg Not Found
**Error**: `ERROR: Postprocessing: ffprobe and ffmpeg not found`

**Solution**: Install FFmpeg
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt-get install ffmpeg`
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

#### 5. Download Progress Not Showing
**Cause**: Missing Content-Length header or network issues

**Check**:
- Browser console (F12) for errors
- Backend terminal for download logs
- Try a different video

#### 6. ModuleNotFoundError
**Solution**: Reinstall dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 7. CORS Errors
**Cause**: Backend not running or wrong URL

**Solution**:
- Ensure backend is running on `http://localhost:8000`
- Check `API_BASE_URL` in `frontend/app/page.tsx`

#### 8. Port Already in Use
**Backend**: Change port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Frontend**: Change port when starting:
```bash
npm run dev -- -p 3001
```

### Debugging Tips

1. **Check Backend Logs**: Terminal running `python main.py` shows detailed logs
2. **Check Browser Console**: Press F12 and look for errors
3. **Test Backend Directly**: Visit `http://localhost:8000/docs` for API documentation
4. **Verify FFmpeg**: Run `ffmpeg -version` to ensure it's installed

### Maintenance

**Keep yt-dlp Updated**: YouTube updates frequently, so update yt-dlp monthly:
```bash
cd backend
source venv/bin/activate
pip install --upgrade yt-dlp
```

## Development

### Backend
- **Framework**: FastAPI with automatic API documentation
- **API Docs**: Visit `http://localhost:8000/docs` for interactive Swagger UI
- **Video Processing**: yt-dlp handles YouTube extraction and downloads
- **File Serving**: FastAPI FileResponse with streaming support
- **Lifespan Events**: Automatic cleanup on server shutdown

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for responsive design
- **HTTP Client**: Axios with progress tracking
- **State Management**: React hooks (useState)

### Key Features Implementation

#### Real-time Download Progress
- Uses Axios `onDownloadProgress` callback
- Calculates percentage based on `Content-Length` header
- Updates UI in real-time with smooth animations
- Progress bar with gradient (blue to green)

#### File Size Estimation
- Primary: Direct `filesize` from yt-dlp
- Fallback 1: `filesize_approx` from yt-dlp
- Fallback 2: Bitrate-based calculation `(bitrate × duration) ÷ 8`
- Displays "Size unknown" when no estimation possible

#### Unicode Filename Support
- Implements RFC 5987 encoding for HTTP headers
- Supports emojis, special characters, and non-English text
- Dual filename format for broad browser compatibility

## Architecture

### Request Flow
```
User Browser → Next.js Frontend → FastAPI Backend → yt-dlp → YouTube
                     ↓                    ↓
              Download Progress    Temporary Storage
                     ↓                    ↓
              Progress Bar          FFmpeg Merge
                     ↓                    ↓
              User Downloads      Auto Cleanup
```

### Technology Choices

**Why FastAPI?**
- Async support for better performance
- Automatic API documentation
- Modern Python with type hints
- Easy file streaming

**Why Next.js?**
- React framework with great DX
- Built-in TypeScript support
- Optimized image handling
- Fast refresh during development

**Why yt-dlp?**
- Most reliable YouTube downloader
- Actively maintained
- Supports format merging
- Extensive format options

## Performance Optimizations

- **Streaming**: Videos are streamed directly to user, not fully loaded in memory
- **Cleanup**: Automatic file cleanup prevents disk space issues
- **Format Selection**: Prefers combined formats to avoid unnecessary merging
- **Progress Tracking**: Real-time updates without polling
- **Async Operations**: Non-blocking I/O for better concurrency

## Security Considerations

- **Input Validation**: URL validation on both frontend and backend
- **File Cleanup**: Automatic deletion of temporary files
- **CORS**: Restricted to frontend origin only
- **No User Data**: No personal information collected or stored
- **Temporary Storage**: Files deleted immediately after serving

## Known Limitations

1. **YouTube API Changes**: Requires regular yt-dlp updates
2. **Large Files**: Very large videos (>2GB) may timeout
3. **Region Restrictions**: Cannot bypass geo-blocking
4. **Age Restrictions**: Cannot download age-restricted content without authentication
5. **Live Streams**: Live content not supported
6. **Download Speed**: Limited by server bandwidth and YouTube throttling

## Future Enhancements

Potential features for future versions:
- Playlist support for bulk downloads
- Video preview before download
- Audio-only download option
- Download queue management
- Custom output format selection
- Download history tracking
- Server-side WebSocket for better progress tracking
- Thumbnail extraction
- Subtitle download support

## Important Notes

⚠️ **Legal and Ethical Use**
- This application is for **educational purposes only**
- **Respect YouTube's Terms of Service**
- **Respect copyright laws** when downloading videos
- Only download videos you have the **right to download**
- Do not use for **commercial purposes**
- Do not distribute downloaded content without permission

## License

This project is open source and available for educational purposes only.

## Disclaimer

This tool is intended for **personal, educational use only**. Users are solely responsible for ensuring they comply with:
- YouTube's Terms of Service
- Applicable copyright laws
- Content creator's rights
- Local laws and regulations

The developers assume no liability for misuse of this software.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review closed issues on GitHub
- Open a new issue with detailed information
