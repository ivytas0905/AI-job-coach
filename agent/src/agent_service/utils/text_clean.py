"""Text Cleaning Utilities"""
import re


class TextCleaner:
    """Clean and normalize text"""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s@.,;:()\-/]', '', text)

        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Remove multiple consecutive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def extract_email(text: str) -> str:
        """
        Extract email from text

        Args:
            text: Text content

        Returns:
            Email address or empty string
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_phone(text: str) -> str:
        """
        Extract phone number from text

        Args:
            text: Text content

        Returns:
            Phone number or empty string
        """
        # Match various phone formats
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-234-567-8900
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (234) 567-8900
            r'\d{3}[-.\s]?\d{4}',  # 567-8900
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return ""

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """
        Extract URLs from text

        Args:
            text: Text content

        Returns:
            List of URLs
        """
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
