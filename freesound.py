#!/usr/bin/env python3
"""
Freesound CLI Downloader

Download audio files from Freesound.org without logging in.

Usage:
    freesound https://freesound.org/people/Yahujiki/sounds/843779/
    freesound https://freesound.org/people/Yahujiki/sounds/843779/ --ogg
    freesound https://freesound.org/people/Yahujiki/sounds/843779/ --hq
    freesound URL1 URL2 URL3 --mp3 --hq -o ~/Downloads
"""

import argparse
import os
import re
import sys
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Missing dependencies. Install them with:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def extract_sound_info(url: str) -> dict | None:
    """
    Fetch the Freesound page and extract audio URLs and metadata.
    
    Args:
        url: Freesound sound page URL
        
    Returns:
        Dictionary with sound info or None on failure
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    player = soup.find(class_='bw-player')
    if not player:
        # Try alternative selector
        player = soup.find(attrs={'data-mp3': True})
    
    if not player:
        print(f"Error: Could not find audio player on page: {url}")
        return None
    
    mp3_url = player.get('data-mp3')
    ogg_url = player.get('data-ogg')
    title = player.get('data-title', 'unknown')
    sound_id = player.get('data-sound-id', '')
    duration = player.get('data-duration', '')
    
    if not mp3_url and not ogg_url:
        print(f"Error: No audio URLs found on page: {url}")
        return None
    
    return {
        'url': url,
        'mp3': mp3_url,
        'ogg': ogg_url,
        'title': title,
        'sound_id': sound_id,
        'duration': duration
    }


def get_hq_url(url: str) -> str:
    """Convert low-quality URL to high-quality URL."""
    return url.replace('-lq.', '-hq.')


def sanitize_filename(name: str) -> str:
    """Remove or replace invalid filename characters."""
    # Replace invalid characters with underscores
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing whitespace and dots
    name = name.strip(' .')
    return name if name else 'download'


def download_file(url: str, output_path: str) -> bool:
    """
    Download a file from URL to output_path with progress display.
    
    Args:
        url: URL to download from
        output_path: Local path to save file
        
    Returns:
        True on success, False on failure
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        bar_len = 30
                        filled = int(bar_len * downloaded / total_size)
                        bar = '█' * filled + '░' * (bar_len - filled)
                        print(f'\r  [{bar}] {percent:.1f}%', end='', flush=True)
        
        print()  # New line after progress bar
        return True
        
    except requests.RequestException as e:
        print(f"\nError downloading: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Download audio files from Freesound.org',
        epilog='Example: freesound https://freesound.org/people/Yahujiki/sounds/843779/ --mp3 --hq'
    )
    parser.add_argument(
        'urls',
        nargs='+',
        help='Freesound sound page URLs (e.g., https://freesound.org/people/user/sounds/12345/)'
    )
    parser.add_argument(
        '--mp3',
        action='store_true',
        help='Download MP3 format (default)'
    )
    parser.add_argument(
        '--ogg',
        action='store_true',
        help='Download OGG format'
    )
    parser.add_argument(
        '--hq',
        action='store_true',
        help='Download high-quality version (default is low-quality)'
    )
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Default to MP3 if no format specified
    if not args.mp3 and not args.ogg:
        args.mp3 = True
    
    # Create output directory if needed
    output_dir = os.path.expanduser(args.output)
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    for url in args.urls:
        print(f"\n📥 Processing: {url}")
        
        # Validate URL format
        parsed = urlparse(url)
        if 'freesound.org' not in parsed.netloc:
            print(f"  ⚠️  Skipping: Not a Freesound URL")
            fail_count += 1
            continue
        
        # Extract sound info
        info = extract_sound_info(url)
        if not info:
            fail_count += 1
            continue
        
        print(f"  📝 Title: {info['title']}")
        if info['duration']:
            try:
                duration = float(info['duration'])
                mins = int(duration // 60)
                secs = int(duration % 60)
                print(f"  ⏱️  Duration: {mins}:{secs:02d}")
            except ValueError:
                pass
        
        # Determine formats to download
        formats_to_download = []
        if args.mp3 and info['mp3']:
            formats_to_download.append(('mp3', info['mp3']))
        if args.ogg and info['ogg']:
            formats_to_download.append(('ogg', info['ogg']))
        
        for fmt, audio_url in formats_to_download:
            # Apply HQ if requested
            if args.hq:
                audio_url = get_hq_url(audio_url)
            
            # Generate filename
            quality = 'hq' if args.hq else 'lq'
            safe_title = sanitize_filename(info['title'])
            filename = f"{safe_title}_{info['sound_id']}_{quality}.{fmt}"
            output_path = os.path.join(output_dir, filename)
            
            print(f"  ⬇️  Downloading {fmt.upper()} ({'high-quality' if args.hq else 'standard'})...")
            
            if download_file(audio_url, output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(f"  ✅ Saved: {filename} ({file_size:.2f} MB)")
                success_count += 1
            else:
                fail_count += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Complete! {success_count} downloaded, {fail_count} failed")


if __name__ == '__main__':
    main()
