"""
Simple test script to verify the backend API is working correctly
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_video_info():
    """Test fetching video information"""
    print("Testing video info endpoint...")

    # Use a short test video URL
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/video-info",
            json={"url": test_url}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Success!")
            print(f"Title: {data['title']}")
            print(f"Uploader: {data['uploader']}")
            print(f"Duration: {data['duration']} seconds")
            print(f"\nAvailable formats ({len(data['formats'])} total):")

            for i, fmt in enumerate(data['formats'], 1):
                size_info = f"{fmt['filesize_mb']} MB" if fmt['filesize_mb'] else "Unknown size"
                fps_info = f"{fmt['fps']} fps" if fmt['fps'] else "Unknown fps"
                print(f"  {i}. {fmt['resolution']} ({fmt['ext']}) - {size_info} - {fps_info}")
                print(f"     Format ID: {fmt['format_id']}")

            if len(data['formats']) == 0:
                print("  ⚠️  WARNING: No formats found!")

            return data
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(response.text)
            return None

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to backend. Is it running on http://localhost:8000?")
        return None
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("YouTube Downloader API Test")
    print("=" * 60)

    # Test if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"✓ Backend server is running: {response.json()['message']}\n")
    except:
        print("✗ Backend server is not running!")
        print("Start it with: python main.py\n")
        exit(1)

    # Test video info
    test_video_info()

    print("\n" + "=" * 60)
