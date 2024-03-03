# Download Flow & File Storage

## How Downloads Work

### 1. **User Clicks "Download Video"**
   - Frontend sends download request to backend with URL and quality

### 2. **Backend Processing** (in `backend/downloads/`)
   - Backend downloads video from YouTube to temporary storage
   - Location: `backend/downloads/[unique-id]_[video-title].mp4`
   - Example: `backend/downloads/8dcada14_My Video Title.mp4`

### 3. **File Transfer to User**
   - Backend sends the file to user's browser using HTTP streaming
   - Browser receives the file and prompts download dialog

### 4. **User's Download** (Final Destination)
   - File is saved to **user's browser default download folder**:
     - Windows: `C:\Users\[Username]\Downloads\`
     - macOS: `/Users/[Username]/Downloads/`
     - Linux: `/home/[Username]/Downloads/`

### 5. **Automatic Cleanup**
   - Backend automatically deletes temporary files from `backend/downloads/`
   - Cleanup happens:
     - Before each new download
     - When the server shuts down

## File Structure

```
YouTube video to mp4/
├── backend/
│   ├── downloads/              ← Temporary storage (auto-cleaned)
│   │   └── [videos stored here temporarily]
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── ...
```

## Storage Management

### Temporary Server Storage
- **Location**: `backend/downloads/`
- **Purpose**: Temporary storage during processing
- **Retention**: Files are deleted after serving to user
- **Size**: Only one video at a time (previous downloads are cleaned)

### End User Storage
- **Location**: User's browser download folder
- **Purpose**: Permanent storage on user's device
- **Retention**: User manages these files
- **Size**: User's responsibility

## Important Notes

### 1. **Server Disk Space**
- Only one video is stored at a time in `backend/downloads/`
- Files are automatically cleaned before each new download
- No disk space issues unless a download fails mid-process

### 2. **User Download Location**
Users can change their download location in browser settings:
- **Chrome**: Settings → Downloads → Location
- **Firefox**: Settings → General → Downloads → Save files to
- **Safari**: Preferences → General → File download location

### 3. **Network Transfer**
The video is transferred via HTTP streaming:
```
YouTube → Backend Server → User's Browser → User's Download Folder
```

## Code Reference

### Backend Storage Location
[backend/main.py:30-32](backend/main.py#L30-L32)
```python
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
```

### Cleanup Function
[backend/main.py:41-48](backend/main.py#L41-L48)
```python
def clean_old_files():
    """Clean up old downloaded files"""
    try:
        for file in DOWNLOAD_DIR.glob("*"):
            if file.is_file():
                file.unlink()
    except Exception as e:
        print(f"Error cleaning files: {e}")
```

### Download Endpoint
[backend/main.py:140-141](backend/main.py#L140-L141)
```python
# Clean old files before downloading new one
clean_old_files()
```

### File Response to User
[backend/main.py:182-189](backend/main.py#L182-L189)
```python
return FileResponse(
    path=filename,
    filename=file_basename,
    media_type='video/mp4',
    headers={
        "Content-Disposition": f'attachment; filename="{file_basename}"'
    }
)
```

The `Content-Disposition: attachment` header tells the browser to download the file instead of playing it.

## Changing Download Behavior

### If you want users to preview instead of download:
Change `attachment` to `inline` in [backend/main.py:187](backend/main.py#L187):
```python
"Content-Disposition": f'inline; filename="{file_basename}"'
```

### If you want to keep server copies:
Comment out the cleanup in [backend/main.py:141](backend/main.py#L141):
```python
# clean_old_files()  # Disabled - will keep all downloads
```

**Warning**: This will fill up your server disk space over time!

## Privacy & Security

1. **Temporary Storage**: Videos are NOT permanently stored on your server
2. **Auto Cleanup**: Files are deleted immediately after serving
3. **No User Data**: No user information or download history is stored
4. **Unique IDs**: Each download gets a unique temporary ID to prevent conflicts

## Troubleshooting

### "Downloaded file not found" error
- The file was cleaned up before being sent
- Solution: The code already prevents this with proper file handling

### Server disk full
- Old files weren't cleaned up (server crashed mid-download)
- Solution: Manually delete files in `backend/downloads/` or restart server

### User can't find downloaded file
- Check their browser's download folder
- Check browser's download history (Ctrl+J in Chrome/Firefox)
- File might be in a custom download location set in browser settings
