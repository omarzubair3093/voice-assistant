from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import FileResponse
from assistant.assistant_service import handle_audio_from_user
import traceback

controller = APIRouter(prefix='/voice-assistant')


@controller.post('/audio-message', status_code=200)
async def handle_receive_audio_data(file: UploadFile):
    try:
        print('\n=== Received audio file ===')
        print(f'Filename: {file.filename}')
        print(f'Content type: {file.content_type}')

        file_data = await file.read()
        print(f'File size: {len(file_data)} bytes')

        generated_ai_audio_file_path = await handle_audio_from_user(file_data)
        print(f'Generated audio path: {generated_ai_audio_file_path}')

        return FileResponse(
            generated_ai_audio_file_path,
            media_type='audio/mpeg',
            filename='ai_output.mp3'
        )

    except Exception as e:
        print(f"\n❌ Error in handle_receive_audio_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )