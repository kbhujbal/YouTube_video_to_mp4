# YouTube Video Downloader

A modern web application that allows users to download YouTube videos in various quality options. Built with Python (FastAPI) backend and Next.js (React) frontend.

## Features

- Download YouTube videos in multiple quality options
- Only shows available quality options for each video
- Clean and modern user interface
- Real-time video information preview
- Automatic quality detection
- Download progress indication
- Responsive design

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

1. Start both the backend and frontend servers
2. Open your browser and navigate to `http://localhost:3000`
3. Paste a YouTube video URL in the input field
4. Click "Get Info" to fetch available quality options
5. Select your preferred quality from the available options
6. Click "Download Video" to download the video

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

## Important Notes

- This application is for educational purposes only
- Please respect YouTube's Terms of Service
- Respect copyright laws when downloading videos
- Only download videos you have the right to download
- Downloaded files are temporarily stored on the server and cleaned up automatically

## Troubleshooting

### Backend Issues

1. **ModuleNotFoundError**: Make sure you've installed all dependencies
```bash
pip install -r requirements.txt
```

2. **Port already in use**: Change the port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to any available port
```

### Frontend Issues

1. **CORS errors**: Make sure the backend is running and the URL in `frontend/app/page.tsx` matches your backend URL

2. **Image loading errors**: The application uses Next.js Image component which requires proper domain configuration in `next.config.js`

## Development

### Backend
- The backend uses FastAPI with automatic API documentation
- Visit `http://localhost:8000/docs` for interactive API documentation

### Frontend
- Built with Next.js App Router
- Uses TypeScript for type safety
- Styled with Tailwind CSS

## License

This project is for educational purposes only.

## Disclaimer

This tool is intended for personal use only. Users are responsible for ensuring they comply with YouTube's Terms of Service and applicable copyright laws.
