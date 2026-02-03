# Freesound Downloader

A simple CLI tool to download audio files from [Freesound.org](https://freesound.org/) without logging in.

## Installation

```bash
git clone https://github.com/enXov/freesound-downloader.git
cd freesound-downloader
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Download as MP3 (default)
./freesound https://freesound.org/people/Yahujiki/sounds/843779/

# Download as OGG
./freesound https://freesound.org/people/Yahujiki/sounds/843779/ --ogg

# Download high-quality version
./freesound https://freesound.org/people/Yahujiki/sounds/843779/ --hq

# Download multiple sounds
./freesound URL1 URL2 URL3

# Specify output directory
./freesound URL -o ~/Downloads/sounds

# Download both formats in high quality
./freesound URL --mp3 --ogg --hq
```

## Options

| Option | Description |
|--------|-------------|
| `--mp3` | Download MP3 format (default) |
| `--ogg` | Download OGG format |
| `--hq` | Download high-quality version |
| `-o, --output` | Output directory |

## Requirements

- Python 3.10+
- requests
- beautifulsoup4

## License

MIT
