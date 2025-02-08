import asyncio
import aiohttp
import wave
import numpy as np
import os
import shutil
import subprocess


def get_ffmpeg_path():
    """Get the full path to ffmpeg executable"""
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path

    # Common ffmpeg locations on Mac (Homebrew)
    mac_locations = [
        '/opt/homebrew/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
    ]

    for location in mac_locations:
        if os.path.exists(location):
            return location

    raise FileNotFoundError("ffmpeg not found. Please ensure it's installed and in PATH")


async def test_voice_assistant():
    print("\n🎤 Testing Voice Assistant API")
    print("=" * 50)

    # Create a test MP3 file
    filename = "test_input.mp3"
    sample_rate = 44100
    duration = 1  # 1 second
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    audio_data = (audio_data * 32767).astype(np.int16)

    # Save as WAV first
    wav_filename = "temp.wav"
    with wave.open(wav_filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    # Convert to MP3 using ffmpeg with full path
    try:
        ffmpeg_path = get_ffmpeg_path()
        print(f"Using ffmpeg at: {ffmpeg_path}")

        subprocess.run([
            ffmpeg_path,
            '-i', wav_filename,
            '-acodec', 'libmp3lame',
            '-q:a', '2',
            filename
        ], check=True)

        os.remove(wav_filename)
        print(f"✅ Created test file: {filename}")

    except Exception as e:
        print(f"Error creating MP3: {str(e)}")
        return

    try:
        async with aiohttp.ClientSession() as session:
            url = "http://localhost:8001/voice-assistant/audio-message"

            data = aiohttp.FormData()
            data.add_field('file',
                           open(filename, 'rb'),
                           filename=filename,
                           content_type='audio/mpeg')

            print("\n📤 Sending request...")
            async with session.post(url, data=data) as response:
                print(f"Status: {response.status}")
                if response.status != 200:
                    print("Error details:", await response.text())
                else:
                    content = await response.read()
                    with open("ai_response.mp3", "wb") as f:
                        f.write(content)
                    print("✅ Received and saved AI response")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Cleanup
        for f in [filename]:
            if os.path.exists(f):
                os.remove(f)
                print(f"Cleaned up {f}")


if __name__ == "__main__":
    asyncio.run(test_voice_assistant())