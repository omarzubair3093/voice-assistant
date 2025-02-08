import boto3
from typing import Dict, Any

def convert_text_to_audio(text_content: str) -> Dict[str, Any]:
    polly_client = boto3.client('polly')
    try:
        response = polly_client.synthesize_speech(  # Fixed typo in synthesize
            Engine='standard',
            LanguageCode='en-US',
            OutputFormat='mp3',
            Text=text_content,
            VoiceId='Raveena'
        )
        return response
    except Exception as e:
        raise Exception(f"Failed to convert text to audio: {str(e)}")
