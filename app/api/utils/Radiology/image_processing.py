from fastapi import APIRouter, HTTPException , UploadFile
from PIL import Image
import io
import base64

def resize_and_encode_image(file: UploadFile, max_width=500, max_height=500, quality=50) -> str:
    try:
        # Open the image
        img = Image.open(file.file)
        
        # Resize the image while maintaining the aspect ratio
        img.thumbnail((max_width, max_height))
        
        # Compress the image (lower quality to reduce file size)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)  # Save as JPEG
        buffer.seek(0)
        
        # Convert the image to base64
        return base64.b64encode(buffer.read()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")


