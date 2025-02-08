import asyncio
import aiohttp
import os
import shutil
from datetime import datetime
import sounddevice as sd
import soundfile as sf
import numpy as np


class VoiceAssistantTester:
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.test_folder = "test_recordings"
        self.ffmpeg_path = '/opt/homebrew/bin/ffmpeg'  # Full path to ffmpeg
        os.makedirs(self.test_folder, exist_ok=True)

    def get_ffmpeg_path(self):
        """Get the full path to ffmpeg executable"""
        if os.path.exists(self.ffmpeg_path):
            return self.ffmpeg_path

        # Try to find ffmpeg in PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path

        # Common ffmpeg locations on Mac
        mac_locations = [
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg'
        ]

        for location in mac_locations:
            if os.path.exists(location):
                return location

        raise FileNotFoundError("ffmpeg not found. Please install it using 'brew install ffmpeg'")

    async def record_audio(self, duration=5):
        """Record audio from microphone"""
        try:
            print(f"\n🎤 Recording for {duration} seconds...")
            print("Speak now...")

            # Record audio
            sample_rate = 44100
            recording = sd.rec(int(duration * sample_rate),
                               samplerate=sample_rate,
                               channels=1,
                               dtype='float32')

            # Wait for recording to complete
            sd.wait()
            print("✅ Recording complete!")

            # Save as WAV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            wav_path = os.path.join(self.test_folder, f"recording_{timestamp}.wav")
            sf.write(wav_path, recording, sample_rate)

            # Convert to MP3
            mp3_path = os.path.join(self.test_folder, f"recording_{timestamp}.mp3")
            ffmpeg = self.get_ffmpeg_path()

            conversion_command = f'"{ffmpeg}" -i "{wav_path}" -q:a 2 "{mp3_path}" -y -loglevel error'
            result = os.system(conversion_command)

            if result != 0:
                raise Exception("Failed to convert WAV to MP3")

            # Verify MP3 file exists
            if not os.path.exists(mp3_path):
                raise Exception("MP3 file was not created")

            # Clean up WAV file
            if os.path.exists(wav_path):
                os.remove(wav_path)

            print(f"✅ Created MP3 file: {mp3_path}")
            return mp3_path

        except Exception as e:
            print(f"❌ Error during recording: {str(e)}")
            return None

    async def send_audio_get_response(self, audio_file_path):
        """Send audio file to server and get response"""
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            print("\n📤 Sending audio to server...")

            async with aiohttp.ClientSession() as session:
                url = f"{self.server_url}/voice-assistant/audio-message"

                # Prepare file upload
                data = aiohttp.FormData()
                data.add_field('file',
                               open(audio_file_path, 'rb'),
                               filename=os.path.basename(audio_file_path),
                               content_type='audio/mpeg')

                # Send request
                async with session.post(url, data=data) as response:
                    print(f"Server response status: {response.status}")

                    if response.status == 200:
                        # Save response audio
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        response_path = os.path.join(
                            self.test_folder,
                            f"ai_response_{timestamp}.mp3"
                        )

                        content = await response.read()
                        with open(response_path, 'wb') as f:
                            f.write(content)

                        print(f"✅ Saved AI response to: {response_path}")
                        return response_path
                    else:
                        error_text = await response.text()
                        print(f"❌ Error: {error_text}")
                        return None

        except Exception as e:
            print(f"❌ Error sending audio: {str(e)}")
            return None

    async def play_audio(self, file_path):
        """Play audio file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            print(f"\n🔊 Playing: {os.path.basename(file_path)}")

            # For Mac
            if os.system(f'afplay "{file_path}"') != 0:
                raise Exception("Failed to play audio")

        except Exception as e:
            print(f"❌ Error playing audio: {str(e)}")

    async def test_conversation(self):
        """Run a complete conversation test"""
        try:
            while True:
                print("\n=== Voice Assistant Test ===")
                print("1. Record and send new message")
                print("2. Send existing audio file")
                print("3. List all recordings")
                print("4. Play a recording")
                print("5. Exit")

                choice = input("\nEnter your choice (1-5): ").strip()

                if choice == '1':
                    try:
                        duration = float(input("Enter recording duration in seconds: "))
                        audio_path = await self.record_audio(duration)

                        if audio_path and os.path.exists(audio_path):
                            print(f"Recorded: {audio_path}")

                            # Play recorded audio
                            print("\nPlaying your recording...")
                            await self.play_audio(audio_path)

                            # Send and get response
                            response_path = await self.send_audio_get_response(audio_path)
                            if response_path:
                                print("\nPlaying AI response...")
                                await self.play_audio(response_path)
                        else:
                            print("❌ Failed to create recording")

                    except ValueError:
                        print("❌ Please enter a valid number for duration")

                elif choice == '2':
                    file_path = input("Enter path to audio file (MP3): ").strip()
                    if os.path.exists(file_path):
                        response_path = await self.send_audio_get_response(file_path)
                        if response_path:
                            await self.play_audio(response_path)
                    else:
                        print("❌ File not found!")

                elif choice == '3':
                    print("\nAvailable recordings:")
                    recordings = [f for f in os.listdir(self.test_folder) if f.endswith('.mp3')]
                    if recordings:
                        for file in recordings:
                            print(f"- {file}")
                    else:
                        print("No recordings found")

                elif choice == '4':
                    recordings = [f for f in os.listdir(self.test_folder) if f.endswith('.mp3')]
                    if recordings:
                        print("\nAvailable recordings:")
                        for i, file in enumerate(recordings):
                            print(f"{i + 1}. {file}")

                        try:
                            idx = int(input("\nEnter number to play: ")) - 1
                            if 0 <= idx < len(recordings):
                                file_path = os.path.join(self.test_folder, recordings[idx])
                                await self.play_audio(file_path)
                            else:
                                print("❌ Invalid selection!")
                        except ValueError:
                            print("❌ Please enter a valid number")
                    else:
                        print("No recordings found!")

                elif choice == '5':
                    print("\nGoodbye! 👋")
                    break

                else:
                    print("❌ Invalid choice!")

        except Exception as e:
            print(f"❌ Error in test conversation: {str(e)}")


def check_requirements():
    """Check and install required packages"""
    required_packages = ['sounddevice', 'soundfile', 'numpy', 'aiohttp']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            os.system(f'pip install {package}')


if __name__ == "__main__":
    # Check requirements
    check_requirements()

    # Verify ffmpeg installation
    try:
        tester = VoiceAssistantTester()
        ffmpeg_path = tester.get_ffmpeg_path()
        print(f"Found ffmpeg at: {ffmpeg_path}")

        # Run the test
        asyncio.run(tester.test_conversation())

    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
        print("Please install ffmpeg using:")
        print("  Mac: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")