"""PDF Parser Implementation"""
import io
from PyPDF2 import PdfReader


class PDFParser:
    """Extract text from PDF files"""

    @staticmethod
    def extract_text(file_content: bytes) -> str:
        """
        Extract text from PDF file

        Args:
            file_content: PDF file bytes

        Returns:
            Extracted text content
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)

            text_content = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)

            return "\n".join(text_content)

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
