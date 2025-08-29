import base64

def encode_image(path: str) -> str:
        """Convert an image file to Base64 string for sending to LLM."""
        with open(path, "rb") as f:
         return base64.b64encode(f.read()).decode("utf-8")



# def decode_image(b64_string: str, output_path: str) -> None:
#     """Decode a Base64 string and save it as an image file."""
#     with open(output_path, "wb") as f:
#         f.write(base64.b64decode(b64_string))