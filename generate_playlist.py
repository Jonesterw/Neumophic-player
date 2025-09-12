import os
import json
import requests
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.m4a import M4A

# --- Configuration ---
# The path to your audio folder, relative to the main project folder.
AUDIO_FOLDER = 'C:\\Users\\HARRIET\\Music'
# The path to your album art folder.
ALBUM_ART_FOLDER = 'assets/album-art'
# A default album art to use if no match is found.
DEFAULT_IMAGE = os.path.join(ALBUM_ART_FOLDER, 'bad and bougee.jfif').replace('\\', '/')
# --- API Configuration ---
# Get a free API key from https://www.theaudiodb.com/api_apply.php
# The key '1' is a test key, but it's recommended to get your own for better reliability.
THEAUDIODB_API_KEY = "1" # <-- PASTE YOUR API KEY HERE

# --- Helper Functions ---
def get_audio_info(filepath):
    """Extracts metadata tags and duration from an audio file."""
    info = {
        "title": None,
        "artist": None,
        "album": None,
        "duration": "0:00"
    }
    audio = None
    try:
        if filepath.lower().endswith('.mp3'):
            audio = MP3(filepath)
            # Mutagen keys can be complex, use .get() for safety
            info['artist'] = audio.get('TPE1', [None])[0]
            info['album'] = audio.get('TALB', [None])[0]
            info['title'] = audio.get('TIT2', [None])[0]
        elif filepath.lower().endswith('.m4a'):
            audio = M4A(filepath)
            info['artist'] = audio.get('\xa9ART', [None])[0]
            info['album'] = audio.get('\xa9alb', [None])[0]
            info['title'] = audio.get('\xa9nam', [None])[0]
        elif filepath.lower().endswith('.wav'):
            audio = WAVE(filepath)
        elif filepath.lower().endswith('.ogg'):
            audio = OggVorbis(filepath)

        # Get duration for all supported types
        if audio and hasattr(audio, 'info') and hasattr(audio.info, 'length'):
            duration_in_seconds = int(audio.info.length)
            minutes = duration_in_seconds // 60
            seconds = duration_in_seconds % 60
            info['duration'] = f"{minutes}:{seconds:02d}"

    except Exception as e:
        print(f"  - Warning: Could not read tags for {os.path.basename(filepath)}. Error: {e}")

    # Cleanup potential byte strings or whitespace from mutagen
    for key, value in info.items():
        if isinstance(value, str):
            info[key] = value.strip()

    return info

def fetch_metadata_from_api(title, artist):
    """Fetches enhanced metadata from The AudioDB API."""
    if THEAUDIODB_API_KEY in ['1', 'YOUR_API_KEY_HERE'] or not artist or not title or artist == "Unknown Artist":
        return None

    print(f"  - Querying API for: '{artist} - {title}'...")
    try:
        cleaned_title = title.split('(feat.')[0].strip()
        url = f"https://www.theaudiodb.com/api/v1/json/{THEAUDIODB_API_KEY}/searchtrack.php?s={artist}&t={cleaned_title}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data and data.get('track'):
            track_data = data['track'][0]
            return {
                "artist": track_data.get('strArtist') or None,
                "album": track_data.get('strAlbum') or None,
                "image": track_data.get('strTrackThumb') or None
            }
    except requests.exceptions.RequestException as e:
        print(f"  - API Error: Could not connect. {e}")
    except Exception as e:
        print(f"  - API Error: An unexpected error occurred. {e}")
    
    return None

def find_best_match_image(song_title, image_files):
    """Finds the best matching image file for a given song title."""
    best_match = None
    highest_score = 0
    
    # Prepare song title words (lowercase, alphanumeric only)
    song_words = set(word for word in song_title.lower().split() if word.isalnum())
    
    if not song_words:
        return None

    for image_file in image_files:
        # Prepare image filename words
        image_name = os.path.splitext(image_file)[0]
        image_words = set(word for word in image_name.lower().replace('_', ' ').replace('-', ' ').split() if word.isalnum())
        
        # Calculate score based on common words
        score = len(song_words.intersection(image_words))
        
        if score > highest_score:
            highest_score = score
            best_match = image_file
            
    return best_match

# --- Main Script ---
songs_list = []

print("="*50)
print("Starting Playlist Generation...")
print("NOTE: This script now uses The AudioDB API to fetch metadata.")
print("You may need to install the 'requests' library: pip install requests")
if THEAUDIODB_API_KEY in ['1', 'YOUR_API_KEY_HERE']:
    print("WARNING: Using test API key. For best results, get a free key from:")
    print("https://www.theaudiodb.com/api_apply.php")
print("="*50)

print(f"\nScanning for music in '{AUDIO_FOLDER}'...")
print(f"Scanning for local album art in '{ALBUM_ART_FOLDER}'...")

# Pre-scan for all available album art
image_files = []
if os.path.exists(ALBUM_ART_FOLDER):
    image_files = os.listdir(ALBUM_ART_FOLDER)
else:
    print(f"Warning: Local album art folder not found at '{ALBUM_ART_FOLDER}'.")

if not os.path.exists(AUDIO_FOLDER):
    print(f"Error: Audio folder not found at '{AUDIO_FOLDER}'. Please check the path.")
else:
    # Loop through all files in the audio folder
    for filename in sorted(os.listdir(AUDIO_FOLDER)):
        filepath = os.path.join(AUDIO_FOLDER, filename)
        # Check for common audio file extensions
        if filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            print(f"\nProcessing: {filename}")

            # 1. Get info from file tags (most reliable source)
            file_info = get_audio_info(filepath)
            title = file_info['title']
            artist = file_info['artist']
            album = file_info['album']
            duration = file_info['duration']

            # 2. Fallback to filename parsing if tags are missing
            if not title or not artist:
                print("  - No tags found, parsing filename...")
                base_name = os.path.splitext(filename)[0].replace('_', ' ')
                if ' - ' in base_name:
                    parts = base_name.split(' - ', 1)
                    # Only overwrite if the tag was missing
                    if not artist: artist = parts[0].strip()
                    if not title: title = parts[1].strip()
                else:
                    if not title: title = base_name.strip()

            # 3. Set defaults for display and API query
            final_title = (title or os.path.splitext(filename)[0]).title()
            final_artist = (artist or "Unknown Artist").title()
            final_album = (album or "Unknown Album").title()
            
            # 4. Fetch from API for enhancement
            api_data = fetch_metadata_from_api(final_title, final_artist)
            
            image_path = DEFAULT_IMAGE

            if api_data:
                print("  - API Success! Found enhanced metadata.")
                final_artist = (api_data.get('artist') or final_artist).title()
                final_album = (api_data.get('album') or final_album).title()
                if api_data.get('image'):
                    # TheAudioDB provides a preview URL, which is great
                    image_path = api_data['image'] + "/preview"
                    print(f"  - Found API image: {os.path.basename(image_path)}")
                else:
                    print("  - API data found, but no image. Falling back to local search.")
                    matching_image_filename = find_best_match_image(final_title, image_files)
                    if matching_image_filename:
                        image_path = os.path.join(ALBUM_ART_FOLDER, matching_image_filename).replace('\\', '/')
            else:
                print("  - API lookup failed or skipped. Falling back to local image search.")
                matching_image_filename = find_best_match_image(final_title, image_files)
                if matching_image_filename:
                    image_path = os.path.join(ALBUM_ART_FOLDER, matching_image_filename).replace('\\', '/')

            song_data = {
                "title": final_title,
                "artist": final_artist,
                "album": final_album,
                "duration": duration,
                "src": filepath.replace('\\', '/'), # Ensure forward slashes for web paths
                "image": image_path
            }
            songs_list.append(song_data)
            print(f"  -> Added '{final_title}' by '{final_artist}'")

# Format the output as a JavaScript array string
# Using json.dumps with indentation makes it pretty and easy to copy.
js_array_string = f"const localSongs = {json.dumps(songs_list, indent=4)};"

output_js_file = 'playlist.js'
try:
    with open(output_js_file, 'w', encoding='utf-8') as f:
        f.write(js_array_string)
    print("\n" + "="*50)
    print(f"SUCCESS! Playlist has been generated and saved to '{output_js_file}'.")
    print("Your HTML file is now linked to this playlist.")
    print("="*50)
except Exception as e:
    print(f"\nError writing to file: {e}")
