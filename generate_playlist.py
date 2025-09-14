import os
import json
import requests
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.m4a import M4A
from flask import Flask, send_from_directory, request, jsonify

# --- Configuration ---
# The path to your audio folder. os.path.expanduser('~/Music') is a good cross-platform default for the user's music library.
AUDIO_FOLDER = os.path.expanduser('~/Music')
# The path to your album art folder, relative to the script.
ALBUM_ART_FOLDER = os.path.join('assets', 'album art')
# A default album art to use if no match is found.
DEFAULT_IMAGE = os.path.join(ALBUM_ART_FOLDER, 'bad and bougee.jfif').replace('\\', '/') # Note: This is no longer used for background fetching.
# --- API Configuration ---
# Get a free API key from https://www.theaudiodb.com/api_apply.php
# The key '1' is a test key, but it's recommended to get your own for better reliability.
THEAUDIODB_API_KEY = "123" # <-- PASTE YOUR API KEY HERE

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

def fetch_metadata_from_api(title, artist, verbose=True):
    """Fetches enhanced metadata from The AudioDB API."""
    if THEAUDIODB_API_KEY in ['1', 'YOUR_API_KEY_HERE'] or not artist or not title or artist == "Unknown Artist":
        return None

    if verbose:
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
        if verbose:
            print(f"  - API Error: Could not connect. {e}")
    except Exception as e:
        if verbose:
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

def generate_playlist():
    """Scans for audio files, fetches metadata, and writes playlist.js."""
    songs_list = []

    print("="*50)
    print("Starting Playlist Generation...")
    print("NOTE: This script now includes a web server.")
    print("You may need to install the required packages:")
    print("pip install -r requirements.txt")
    if THEAUDIODB_API_KEY in ['1', 'YOUR_API_KEY_HERE']:
        print("\nWARNING: Using test API key. For best results, get a free key from:")
        print("https://www.theaudiodb.com/api_apply.php")
    print("="*50)

    # --- Interactive Audio Folder Configuration ---
    global AUDIO_FOLDER
    while True:
        print(f"\nMusic folder is currently set to: {AUDIO_FOLDER}")
        
        path_is_valid = os.path.isdir(AUDIO_FOLDER)
        has_music = path_is_valid and any(f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')) for f in os.listdir(AUDIO_FOLDER))

        if not has_music:
            if not path_is_valid:
                print("This folder does not exist.")
            else:
                print("This folder doesn't seem to contain any music files.")
            prompt = "Please enter the full path to your music folder (or press Enter to exit): "
        else:
            prompt = "Press Enter to scan this folder, or enter a new path: "

        user_path = input(prompt).strip()

        if not user_path: # User pressed Enter
            if not has_music:
                print("Exiting script.")
                return
            break # Continue with the current valid AUDIO_FOLDER
        
        # User entered a new path, let's validate it
        potential_new_path = os.path.expanduser(user_path)
        if os.path.isdir(potential_new_path):
            AUDIO_FOLDER = potential_new_path
            # Loop will re-evaluate the new path
        else:
            print(f"Error: '{potential_new_path}' is not a valid directory. Please try again.")

    print(f"\nScanning for music in '{AUDIO_FOLDER}'...")

    if not os.path.exists(AUDIO_FOLDER):
        print(f"Error: Audio folder not found at '{AUDIO_FOLDER}'. Please check the path.")
        return

    for filename in sorted(os.listdir(AUDIO_FOLDER)):
        filepath = os.path.join(AUDIO_FOLDER, filename)
        if filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            print(f"\nProcessing: {filename}")
            
            file_info = get_audio_info(filepath)
            title, artist, album, duration = file_info['title'], file_info['artist'], file_info['album'], file_info['duration']

            if not title or not artist:
                print("  - No tags found, parsing filename...")
                base_name = os.path.splitext(filename)[0].replace('_', ' ')
                if ' - ' in base_name:
                    parts = base_name.split(' - ', 1)
                    if not artist: artist = parts[0].strip()
                    if not title: title = parts[1].strip()
                else:
                    if not title: title = base_name.strip()

            final_title = (title or os.path.splitext(filename)[0]).title()
            final_artist = (artist or "Unknown Artist").title()
            final_album = (album or "Unknown Album").title()

            song_data = {
                "title": final_title,
                "artist": final_artist,
                "album": final_album,
                "duration": duration,
                "src": f"music/{filename}", # Use a relative URL for the server
                "image": None # Set to None, will be fetched by the frontend
            }
            songs_list.append(song_data)
            print(f"  -> Added '{final_title}' by '{final_artist}'")

    js_array_string = f"const localSongs = {json.dumps(songs_list, indent=4)};"
    output_js_file = 'playlist.js'
    try:
        with open(output_js_file, 'w', encoding='utf-8') as f:
            f.write(js_array_string)
        print("\n" + "="*50)
        print(f"SUCCESS! Playlist has been generated and saved to '{output_js_file}'.")
        print("="*50)
    except Exception as e:
        print(f"\nError writing to file: {e}")

def run_server():
    """Runs a simple Flask web server to serve the music player and audio files."""
    print("\n" + "="*50)
    print("Starting web server...")
    print("Your music player will be available at: http://127.0.0.1:5000")
    print("Keep this script running to use the player.")
    print("="*50)

    project_root = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__)

    @app.route('/api/health')
    def health_check():
        """An endpoint to confirm the server is running."""
        return {"status": "ok"}

    @app.route('/api/metadata')
    def get_metadata():
        """On-demand endpoint for the frontend to fetch album art."""
        title = request.args.get('title')
        artist = request.args.get('artist')

        if not title or not artist:
            return jsonify({"error": "Missing title or artist"}), 400

        image_path = None
        
        # 1. Try API first (with verbose logging turned off)
        api_data = fetch_metadata_from_api(title, artist, verbose=False)
        if api_data and api_data.get('image'):
            image_path = api_data['image'] + "/preview"
        
        # 2. If API fails or has no image, try local files
        if not image_path:
            image_files = []
            if os.path.exists(ALBUM_ART_FOLDER):
                image_files = os.listdir(ALBUM_ART_FOLDER)
            
            matching_image = find_best_match_image(title, image_files)
            if matching_image:
                image_path = os.path.join(ALBUM_ART_FOLDER, matching_image).replace('\\', '/')

        # 3. Return the found image path or null
        return jsonify({"image": image_path})

    @app.route('/music/<path:filename>')
    def serve_music(filename):
        """Serves audio files from the configured AUDIO_FOLDER."""
        return send_from_directory(AUDIO_FOLDER, filename)

    # This route serves the main index.html file and all other static assets.
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(project_root, path)

    # Disable caching to ensure latest playlist.js is always used
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == "__main__":
    generate_playlist()
    run_server()
