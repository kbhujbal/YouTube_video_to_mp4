# Unicode Filename Fix

## Problem
Videos with Unicode characters in the title (like `｜`, `—`, emojis, or non-English characters) would fail to download with:
```
UnicodeEncodeError: 'latin-1' codec can't encode character '\uff5c' in position 84: ordinal not in range(256)
```

## Root Cause
HTTP headers (like `Content-Disposition`) must be encoded in **latin-1** (ISO-8859-1), which only supports characters 0-255. Unicode characters like:
- `｜` (full-width vertical bar, U+FF5C)
- `—` (em dash)
- `·` (middle dot)
- Emojis
- Chinese, Japanese, Korean characters
- Accented characters beyond basic latin

...cannot be encoded in latin-1.

## Solution
We now use **RFC 5987** encoding which supports Unicode in HTTP headers:

```python
# Before (BROKEN):
headers={
    "Content-Disposition": f'attachment; filename="{file_basename}"'
}

# After (FIXED):
safe_basename = file_basename.encode('ascii', 'ignore').decode('ascii')
encoded_filename = urllib.parse.quote(file_basename)

headers={
    "Content-Disposition": f"attachment; filename=\"{safe_basename}\"; filename*=UTF-8''{encoded_filename}"
}
```

### How it works:
1. **`filename="safe_basename"`** - ASCII-only fallback for old browsers
   - Removes Unicode characters: `｜` → `` (empty)
   - If empty after removal, uses `video.mp4`

2. **`filename*=UTF-8''encoded_filename`** - RFC 5987 for modern browsers
   - Properly encodes Unicode using URL encoding
   - `｜` → `%EF%BD%9C`
   - Modern browsers use this and get the full filename with Unicode

## Example

### Video Title
```
New 2025 Hyundai Nexo Hydrogen Car Drive Impressions ｜ Gagan Choudhary
```

### What gets sent:
```http
Content-Disposition: attachment;
  filename="e6e1cab1_New 2025 Hyundai Nexo Hydrogen Car Drive Impressions  Gagan Choudhary.mp4";
  filename*=UTF-8''e6e1cab1_New%202025%20Hyundai%20Nexo%20Hydrogen%20Car%20Drive%20Impressions%20%EF%BD%9C%20Gagan%20Choudhary.mp4
```

### What the browser downloads:
- **Modern browsers**: Full filename with Unicode intact
- **Old browsers**: ASCII-only version (with Unicode chars removed)

## Testing

### Test with Unicode characters:
Try downloading videos with titles containing:
- `｜` Full-width characters
- `—` Em dashes
- `"` Smart quotes
- `·` Middle dots
- `é` Accented characters
- `中文` Chinese characters
- `😀` Emojis

All should now download successfully!

## Technical Details

### RFC 5987 Format
```
filename*=charset'language'encoded-filename
```

Where:
- `charset`: `UTF-8`
- `language`: Empty (optional)
- `encoded-filename`: URL-encoded UTF-8 bytes

### Browser Support
- ✅ Chrome/Edge (all versions)
- ✅ Firefox (all versions)
- ✅ Safari (all versions)
- ✅ IE 11+ (uses ASCII fallback)
- ✅ Mobile browsers

## Code Reference

[backend/main.py:190-207](backend/main.py#L190-L207)
```python
# Sanitize filename for HTTP header (remove non-ASCII characters)
safe_basename = file_basename.encode('ascii', 'ignore').decode('ascii')
if not safe_basename or safe_basename == '':
    safe_basename = 'video.mp4'

# Use RFC 5987 encoding for proper Unicode support
encoded_filename = urllib.parse.quote(file_basename)

return FileResponse(
    path=filename,
    media_type='video/mp4',
    headers={
        "Content-Disposition": f"attachment; filename=\"{safe_basename}\"; filename*=UTF-8''{encoded_filename}"
    }
)
```

## References
- [RFC 5987: Character Set and Language Encoding for HTTP Header Field Parameters](https://tools.ietf.org/html/rfc5987)
- [MDN: Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition)
