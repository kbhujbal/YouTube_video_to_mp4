# Quick Fix for yt-dlp Issues

## Problem
Your yt-dlp version is outdated (from November 2023). YouTube changes their API frequently, so yt-dlp needs to be updated regularly.

## Solution: Update yt-dlp

### Step 1: Stop the Backend Server
Press `Ctrl+C` in the terminal running the backend

### Step 2: Update yt-dlp

**Option A: Automatic (Recommended)**
```bash
cd backend
chmod +x update_ytdlp.sh
./update_ytdlp.sh
```

**Option B: Manual**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade yt-dlp
```

### Step 3: Verify the Update
```bash
yt-dlp --version
```

You should see a version from 2024 or 2025 (e.g., `2024.12.13` or newer)

### Step 4: Restart the Backend
```bash
python main.py
```

### Step 5: Test Again
Try the same YouTube URL again. You should now see:
- ✅ Multiple quality options (360p, 480p, 720p, 1080p, etc.)
- ✅ No HTTP 400 or 403 errors
- ✅ Successful downloads

## What Changed

1. **requirements.txt**: Changed `yt-dlp==2023.11.16` to `yt-dlp` (always latest)
2. **main.py**: Fixed the FastAPI deprecation warning by using lifespan events
3. **Update script**: Added easy update script for future updates

## Why This Happens

YouTube frequently updates their API and player to:
- Prevent bot access
- Change signature extraction methods
- Update format delivery

yt-dlp needs regular updates to keep up with these changes. The version from November 2023 is over a year old and doesn't work with current YouTube.

## Regular Maintenance

To keep your downloader working:

1. **Update yt-dlp regularly** (monthly):
   ```bash
   cd backend
   source venv/bin/activate
   pip install --upgrade yt-dlp
   ```

2. **Or use the update script**:
   ```bash
   cd backend
   ./update_ytdlp.sh
   ```

## Expected Output After Update

When you click "Get Info", you should see in the backend terminal:

```
=== Processing 25 total formats ===
Format 18: 360p, vcodec=avc1.42001E, acodec=mp4a.40.2, ext=mp4
Format 22: 720p, vcodec=avc1.64001F, acodec=mp4a.40.2, ext=mp4
Format 136: 720p, vcodec=avc1.4d401f, acodec=none, ext=mp4
Format 137: 1080p, vcodec=avc1.640028, acodec=none, ext=mp4
Format 248: 1080p, vcodec=vp9, acodec=none, ext=webm
...

=== Found 5 unique resolutions ===
  1080p: format_id=137, mp4
  720p: format_id=22, mp4
  480p: format_id=135, mp4
  360p: format_id=18, mp4
  144p: format_id=160, mp4
```

No more HTTP 400 or 403 errors!

## Still Having Issues?

If you still get errors after updating:

1. **Check yt-dlp version**:
   ```bash
   yt-dlp --version
   ```
   Should be 2024.x.x or 2025.x.x

2. **Try a different video**: Some videos may be age-restricted or region-locked

3. **Check if FFmpeg is installed** (needed for merging):
   ```bash
   ffmpeg -version
   ```
   If not installed:
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt-get install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

4. **Test with the test script**:
   ```bash
   cd backend
   python test_api.py
   ```
