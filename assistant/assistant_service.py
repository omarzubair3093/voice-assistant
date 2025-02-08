from utils.file_utils import persist_binary_file_locally, create_unique_tmp_file
from transcoding.transcoding_services import convert_file_to_readable_mp3
from audio_handling.audio_transcription_service import convert_audio_to_text
from audio_handling.audio_generation_service import convert_text_to_audio
from chat_service import handle_get_response_for_user
import os
import traceback


def __get_transcoded_audio_file_path(data: bytes) -> str:
    try:
        # Step 1: Save the original audio data to a temporary file
        local_file_path = persist_binary_file_locally(data, file_suffix='user_audio.mp3')
        print(f"✓ Saved original audio to: {local_file_path}")

        # Step 2: Create a new unique path for the transcoded file
        local_output_file_path = create_unique_tmp_file(file_suffix='transcoded_user_audio.mp3')
        print(f"✓ Created output path: {local_output_file_path}")

        # Step 3: Convert the audio file to a readable MP3 format
        convert_file_to_readable_mp3(
            local_input_file_path=local_file_path,
            local_output_file_path=local_output_file_path
        )
        print("✓ Converted audio file")

        return local_output_file_path
    except Exception as e:
        print(f"Error in __get_transcoded_audio_file_path: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise


async def handle_audio_from_user(file: bytes) -> str:
    try:
        print("\nProcessing audio file...")

        # Transcode the audio
        print("1. Transcoding audio...")
        transcoded_user_audio_file_path = __get_transcoded_audio_file_path(file)
        print(f"   ✓ Audio transcoded to: {transcoded_user_audio_file_path}")

        # Convert audio to text
        print("\n2. Converting audio to text...")
        text_content = convert_audio_to_text(transcoded_user_audio_file_path)
        print(f"   ✓ Transcribed text: {text_content[:100]}...")

        # Get AI response
        print("\n3. Getting AI response...")
        ai_text_reply = await handle_get_response_for_user(text_content)
        print(f"   ✓ AI response: {ai_text_reply[:100]}...")

        # Convert response to audio
        print("\n4. Converting response to audio...")
        generated_audio_ai = convert_text_to_audio(ai_text_reply)
        print("   ✓ Generated audio response")

        # Save and return the audio file path
        print("\n5. Saving audio response...")
        output_audio_file_path = persist_binary_file_locally(
            data=generated_audio_ai['AudioStream'].read(),
            file_suffix='ai_audio_reply.mp3'
        )
        print(f"   ✓ Saved to: {output_audio_file_path}")

        return output_audio_file_path

    except Exception as e:
        print(f"\n❌ Error in handle_audio_from_user: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise