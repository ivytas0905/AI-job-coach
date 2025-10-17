from together import Together
import os

class TogetherProvider:
    def __init__(self, api_key: str = None):
        self.client = Together(api_key=api_key or os.environ.get("TOGETHER_API_KEY"))
