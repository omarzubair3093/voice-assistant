import subprocess
import shutil


def get_ffmpeg_path():
    """Get the full path to ffmpeg executable"""
    # First try to get ffmpeg from PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path

    # Common ffmpeg locations on Mac (Homebrew)
    mac_locations = [
        '/opt/homebrew/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
    ]

    # Try common locations
    for location in mac_locations:
        if shutil.which(location):
            return location

    raise FileNotFoundError("ffmpeg not found. Please ensure it's installed and in PATH")


def convert_file_to_readable_mp3(local_input_file_path: str, local_output_file_path: str) -> None:
    """
    Convert audio file to MP3 format using ffmpeg
    """
    try:
        ffmpeg_path = get_ffmpeg_path()
        print(f"Using ffmpeg at: {ffmpeg_path}")

        # Run ffmpeg with full path
        result = subprocess.run([
            ffmpeg_path,
            '-i', local_input_file_path,
            '-acodec', 'libmp3lame',
            '-q:a', '2',  # High quality MP3
            local_output_file_path
        ], capture_output=True, text=True, check=True)

        print("Conversion successful")
        return True

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        raise Exception(f"Failed to convert audio file: {e.stderr}")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        raise