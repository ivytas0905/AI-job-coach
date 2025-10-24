"""File Storage Utilities"""
import os
import aiofiles
from pathlib import Path
from typing import Tuple
from ...config import get_settings

settings = get_settings()


class FileStorage:
    """Handle file upload and storage"""

    def __init__(self, upload_dir: str = "uploads"):
        """
        Initialize file storage

        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        """
        Save file to storage

        Args:
            filename: Original filename
            content: File content bytes

        Returns:
            Path to saved file
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)
        file_path = self.upload_dir / safe_filename

        # Write file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        return str(file_path)

    async def read_file(self, file_path: str) -> bytes:
        """
        Read file from storage

        Args:
            file_path: Path to file

        Returns:
            File content bytes
        """
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()

    def delete_file(self, file_path: str) -> None:
        """
        Delete file from storage

        Args:
            file_path: Path to file
        """
        try:
            os.remove(file_path)
        except OSError:
            pass

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove directory path
        filename = os.path.basename(filename)
        # Replace unsafe characters
        unsafe_chars = ['/', '\\', '..', '\0']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        return filename

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get file extension

        Args:
            filename: Filename

        Returns:
            File extension (lowercase, without dot)
        """
        _, ext = os.path.splitext(filename)
        return ext.lower().lstrip('.')
