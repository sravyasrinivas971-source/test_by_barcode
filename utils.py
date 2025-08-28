import base64

def encode_image(path: str) -> str:
        """Convert an image file to Base64 string for sending to LLM."""
        with open(path, "rb") as f:
         return base64.b64encode(f.read()).decode("utf-8")

