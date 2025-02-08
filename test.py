# test_imports.py
def test_imports():
    print("Testing imports...")

    try:
        from assistant.assistant_controller import controller
        print("✅ assistant_controller imported successfully")
    except Exception as e:
        print(f"❌ Error importing assistant_controller: {str(e)}")

    try:
        from assistant.assistant_service import handle_audio_from_user
        print("✅ assistant_service imported successfully")
    except Exception as e:
        print(f"❌ Error importing assistant_service: {str(e)}")

    try:
        from audio_handling.audio_transcription_service import convert_audio_to_text
        print("✅ audio_transcription_service imported successfully")
    except Exception as e:
        print(f"❌ Error importing audio_transcription_service: {str(e)}")

    try:
        from audio_handling.audio_generation_service import convert_text_to_audio
        print("✅ audio_generation_service imported successfully")
    except Exception as e:
        print(f"❌ Error importing audio_generation_service: {str(e)}")

    try:
        from transcoding.transcoding_services import convert_file_to_readable_mp3
        print("✅ transcoding_services imported successfully")
    except Exception as e:
        print(f"❌ Error importing transcoding_services: {str(e)}")

    try:
        from utils.file_utils import persist_binary_file_locally, create_unique_tmp_file
        print("✅ file_utils imported successfully")
    except Exception as e:
        print(f"❌ Error importing file_utils: {str(e)}")


if __name__ == "__main__":
    test_imports()