import boto3
from pdf2image import convert_from_bytes
from io import BytesIO
import pdfplumber
import fitz
from PIL import Image
import io

def extract_text_with_textract(file_content):
    # Convert PDF to a list of images (one image per page)
    images = convert_from_bytes(file_content)
    textract = boto3.client(
        'textract',
        region_name='eu-west-1'
    )
    
    extracted_text = ""

    for page_number, image in enumerate(images, start=1):
        # Convert the image to bytes
        from io import BytesIO
        image_buffer = BytesIO()
        image.save(image_buffer, format='PNG')
        image_bytes = image_buffer.getvalue()

        # Call Textract on the image
        response = textract.analyze_document(
            Document={'Bytes': image_bytes},
            FeatureTypes=['TABLES', 'FORMS']
        )
        if 'Blocks' not in response or not response['Blocks']:
            raise ValueError(f"Textract returned an empty response for page {page_number}")
        # Extract text from the response
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                extracted_text += block['Text'] + "\n"

        extracted_text += f"\n--- End of Page {page_number} ---\n"
    return extracted_text.strip()

def extract_text_from_pdf(file_content):
    try:
        # Open the PDF file using pdfplumber
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            full_text = ""
            
            # Iterate through all the pages
            for page in pdf.pages:
                full_text += page.extract_text()  # Extract the text from the page
                
            return full_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    

def is_scanned_pdf(file_content):
    # Check if the PDF is scanned (image-based) by trying to extract text
    try:
        # Try extracting text with PDF library (non-image-based PDFs)
        full_text = extract_text_from_pdf(file_content)
        if full_text.strip() == "":
            return True  # Likely a scanned image-based PDF
        return False
    except Exception as e:
        return True  # If extraction fails, assume it's an image-based PDF
    

def process_all_pdf_file(pdf_path: str = None):
    if pdf_path is None:
        return None

    try:
        doc = fitz.open(pdf_path)
        images = []

        for page_num in range(doc.page_count):
            try:
                page = doc[page_num]
                zoom = 3
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                img = img.convert("RGB")

                # Resize if needed
                max_size = 1600
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                images.append(img)

            except Exception as e:
                print(e)
                continue

        doc.close()

        if len(images) == 0:
            raise ValueError("No valid images could be extracted from the PDF")

        return images
    except Exception as e:
        print(e)
        return None