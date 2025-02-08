from openai import OpenAI


def convert_audio_to_text(local_input_file_path: str) -> dict:
    """
    Convert audio file to text using OpenAI's Whisper model

    Args:
        local_input_file_path (str): Path to the local audio file

    Returns:
        str: Transcribed text from the audio file
    """
    # Initialize OpenAI client
    client = OpenAI()

    try:
        # Open and transcribe the audio file
        with open(local_input_file_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Return the transcribed text
        return transcription.text

    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    try:
        audio_path = "path/to/your/audio/file.mp3"
        text = convert_audio_to_text(audio_path)
        print(f"Transcribed text: {text}")
    except Exception as e:
        print(f"Failed to transcribe: {str(e)}")