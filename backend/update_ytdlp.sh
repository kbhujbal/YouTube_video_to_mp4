#!/bin/bash
# Script to update yt-dlp to the latest version

echo "========================================"
echo "Updating yt-dlp to latest version..."
echo "========================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Upgrade yt-dlp
echo "Upgrading yt-dlp..."
pip install --upgrade yt-dlp

# Show version
echo ""
echo "yt-dlp version:"
yt-dlp --version

echo ""
echo "========================================"
echo "Update complete!"
echo "Please restart your backend server."
echo "========================================"
