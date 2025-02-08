import asyncio
import aiohttp
import wave
import numpy as np
import os


async def test_simple_audio():
    print("\n🎤 Testing with simple audio file")
    print("=" * 50)

    # Create a very simple WAV file
    filename = "simple_test.wav"
    sample_rate = 44100
    duration = 1  # 1 second
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    audio_data = (audio_data * 32767).astype(np.int16)

    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    print(f"✅ Created test file: {filename}")

    try:
        async with aiohttp.ClientSession() as session:
            url = "http://localhost:8001/voice-assistant/audio-message"

            data = aiohttp.FormData()
            data.add_field('file',
                           open(filename, 'rb'),
                           filename=filename,
                           content_type='audio/wav')

            print("\n📤 Sending request...")
            async with session.post(url, data=data) as response:
                print(f"Status: {response.status}")
                if response.status != 200:
                    print("Error details:", await response.text())
                else:
                    print("Success!")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Cleaned up {filename}")


if __name__ == "__main__":
    asyncio.run(test_simple_audio())