# Troubleshooting Guide

## Issue: Only 360p quality showing

### Cause
YouTube provides formats in different ways. Some videos have combined video+audio streams, while most modern videos have separate video and audio streams that need to be merged.

### Solution
The updated backend now:
1. Scans ALL available formats (both combined and video-only)
2. Automatically detects and lists all resolutions
3. Enables debug logging to see what's happening

### How to Debug
1. **Restart the backend server** to apply the new changes:
   ```bash
   # Stop the current server (Ctrl+C)
   cd backend
   python main.py
   ```

2. When you paste a YouTube URL and click "Get Info", check the **backend terminal**. You should see output like:
   ```
   === Processing 30 total formats ===
   Format 18: 360p, vcodec=avc1.42001E, acodec=mp4a.40.2, ext=mp4
   Format 22: 720p, vcodec=avc1.64001F, acodec=mp4a.40.2, ext=mp4
   Format 137: 1080p, vcodec=avc1.640028, acodec=none, ext=mp4

   === Found 3 unique resolutions ===
     1080p: format_id=137, mp4
     720p: format_id=22, mp4
     360p: format_id=18, mp4
   ```

3. Check the **browser console** (F12 → Console tab):
   ```
   Video Info Response: {title: "...", formats: Array(3)}
   Available formats: [...]
   Selected format: "137"
   ```

## Issue: Download button fails

### Common Causes & Solutions

#### 1. FFmpeg not installed
**Error message:** `ERROR: Postprocessing: ffprobe and ffmpeg not found`

**Solution:** Install FFmpeg
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
- **Windows:** Download from https://ffmpeg.org/download.html and add to PATH

#### 2. Format not compatible
**Error message:** `Download failed: Requested format is not available`

**Solution:** The backend will now try multiple fallback options:
1. Specified format + best audio
2. Specified format + any audio
3. Best available format

#### 3. Network/timeout issues
**Error message:** `Failed to download video`

**Solution:**
- Check your internet connection
- Try a different video
- Increase timeout in frontend (already set to 5 minutes)

### How to Debug Download Issues

1. **Check backend logs** - The terminal running `python main.py` will show:
   ```
   === Download Request ===
   URL: https://www.youtube.com/watch?v=...
   Format ID: 137
   Download options: {...}
   Starting download...
   Looking for downloaded file...
   Found files: [PosixPath('downloads/abc123_Video Title.mp4')]
   Using file: downloads/abc123_Video Title.mp4
   Sending file: abc123_Video Title.mp4
   ```

2. **Check browser console** for error details

3. **Check browser Network tab** (F12 → Network):
   - Look for the `/api/download` request
   - Check if it returns 200 OK or an error
   - Click on it to see the response details

## Testing the Fix

### Step 1: Restart Backend
```bash
# In the backend directory
cd backend
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
# Restart server
python main.py
```

### Step 2: Test with Known Working Video
Try this short test video: `https://www.youtube.com/watch?v=jNQXAC9IVRw`

### Step 3: Check Output
You should see:
- ✅ Multiple quality options (not just 360p)
- ✅ Download button enabled
- ✅ Successful download when clicked

## Still Having Issues?

### Run the Test Script
```bash
cd backend
source venv/bin/activate
python test_api.py
```

This will test the API and show you exactly what formats are being detected.

### Common Issues

1. **CORS errors**
   - Make sure frontend is running on `http://localhost:3000`
   - Make sure backend is running on `http://localhost:8000`

2. **Module not found errors**
   - Reinstall dependencies: `pip install -r requirements.txt`
   - Make sure virtual environment is activated

3. **Port already in use**
   - Kill the process using the port
   - Or change the port in `main.py` and `frontend/app/page.tsx`

4. **YouTube rate limiting**
   - Wait a few minutes
   - Try a different video
   - Check if you can access the video directly in YouTube

## Debug Checklist

- [ ] Backend server is running (`http://localhost:8000`)
- [ ] Frontend server is running (`http://localhost:3000`)
- [ ] Virtual environment is activated for backend
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] FFmpeg is installed (for video merging)
- [ ] Browser console shows no CORS errors
- [ ] Backend terminal shows format detection logs
- [ ] Multiple quality options appear in UI
- [ ] Download button is enabled after selecting quality
