from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from app.api.routes import router  # Import the router
from app.websockets.Medical.dr_patinet_transcript import router as dr_patinet_conversation
from app.websockets.Medical.dictation import router as medical_dictation_router
from app.websockets.Law.dictation import router as law_dictation_router
from app.websockets.wc_session_testing import wc_router as wc_testing_router
from app.websockets.general_audio_transcript import general_transcript_router
# from app.api.audio_transcript import transcript_router
from app.api.case_sheet_router import generate_case_sheet_router
from app.api.radiology_router import generate_radiology_router
from app.api.health_check import health_check
from app.api.send_case_sheet import router as send_case_sheet_router
from app.api.api_load_testing import api_test_router
from app.api.get_blob_file import get_blob_audio
from app.api.medical_coding import medical_coding
from app.api.get_alternate_medicine import alternate_medicine
from app.api.find_defect_part import find_part_defect_router
from app.api.docextract_router import extract_document_router
import os

app = FastAPI()

# CORS settings to allow requests from the client (like HTML/JS)
# origins = [
#     "http://localhost",  # Assuming you're running the HTML locally
#     "http://localhost:8000",  # In case the HTML is hosted on the same server
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")

# Include WebSocket routes
app.include_router(wc_testing_router, prefix="/ws")
app.include_router(dr_patinet_conversation, prefix="/ws") # Trascription
app.include_router(general_transcript_router, prefix="/ws")
app.include_router(medical_dictation_router, prefix="/ws") # 
app.include_router(law_dictation_router, prefix="/ws")
# app.include_router(transcript_router, prefix="/api")
app.include_router(api_test_router, prefix="/api/v1.0")
app.include_router(generate_case_sheet_router, prefix="/api/v1.0")
app.include_router(send_case_sheet_router, prefix="/api/v1.0")
app.include_router(get_blob_audio, prefix="/api")
app.include_router(medical_coding, prefix="/api/v1.0")
app.include_router(alternate_medicine, prefix="/api/v1.0")
app.include_router(generate_radiology_router, prefix="/api/v1.0")
app.include_router(find_part_defect_router, prefix="/api/v1.0")
app.include_router(extract_document_router,prefix="/api/v1.0")
# Redirect to index.html for the root route
# @app.get("/")
# async def serve_index():
#     return {"message": "Welcome to the WebSocket app. Access the index.html under /static/index.html"}

import logging
from datetime import datetime, timedelta


# # Set up logging configuration
# log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
# os.makedirs("logs", exist_ok=True)
# logging.basicConfig(filename=log_filename, level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


from fastapi.responses import HTMLResponse


@app.get("/")
async def get():
    # Basic HTML to test the WebSocket
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Echo</h1>
        <input id="messageInput" type="text" placeholder="Enter message">
        <button onclick="sendMessage()">Send</button>
        <ul id="messages"></ul>
        <script>
            const ws = new WebSocket("ws://localhost:7000/ws/testws");
            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                const message = document.createElement('li');
                message.textContent = event.data;
                messages.appendChild(message);
            };
            function sendMessage() {
                const input = document.getElementById("messageInput");
                ws.send(input.value);
                input.value = '';
            }
        </script>
    </body>
    </html>
    """)
