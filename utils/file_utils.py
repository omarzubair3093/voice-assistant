import tempfile
import os
from uuid import uuid4

TMP_FOLDER_NAME = 'oz_voice_assistant'

def create_if_not_exists(path: str):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def get_tmp_folder_path():
    """Get path to temporary folder, create if doesn't exist"""
    path = tempfile.gettempdir()
    path = os.path.join(path, TMP_FOLDER_NAME)
    create_if_not_exists(path)
    return path

def get_unique_tmp_file_path():
    """Generate a unique temporary file path"""
    return os.path.join(get_tmp_folder_path(), str(uuid4()))

def create_unique_tmp_file(file_suffix: str) -> str:
    """Create a unique temporary file with the given suffix"""
    return f"{get_unique_tmp_file_path()}{file_suffix}"

def persist_binary_file_locally(data: bytes, file_suffix: str) -> str:
    """
    Save binary data to a temporary file with a unique name
    Args:
        data: Binary data to save
        file_suffix: File extension (e.g., '.wav', '.mp3')
    Returns:
        str: Path to the saved file
    """
    file_path = create_unique_tmp_file(file_suffix)
    with open(file_path, 'wb') as f:
        f.write(data)
    return file_path