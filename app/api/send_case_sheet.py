from fastapi import APIRouter,UploadFile,File,Form
from pydantic import BaseModel
import os
from app.services.casesheet_send.send_casheet_mail import send_case_sheet_email
from app.services.casesheet_send.send_casesheet_whatsaap import send_through_whatsapp
from threading import Thread

router = APIRouter()
class Casesheet(BaseModel):
    Orders: str
    Prescription: str

@router.post("/SendCaseSheet")
async def sendCaseSheet(filePath: str = Form(...), Orders: str = Form(...), Prescription: str = Form(...),EmailAddress: str = Form(None), PhoneNumber: str = Form(None)):
    
    
    if EmailAddress:
        
        thread1 = Thread(target=send_case_sheet_email, args=(filePath, Orders, Prescription, EmailAddress,))
        thread1.start()

    if PhoneNumber:
        print("sending on whatsapp")
        thread2 = Thread(target=send_through_whatsapp, args=(PhoneNumber, Prescription, Orders, filePath))
        thread2.start()

    # Wait for both threads to complete
    if EmailAddress:
        thread1.join()
    if PhoneNumber:
        thread2.join()

    # os.remove(pdf_path)
    return 'Email and WhatsApp message sent successfully!'