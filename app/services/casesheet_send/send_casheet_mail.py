import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import base64
from app.creds.config import  MongoConnectionString, FileStorageConnectionString, FileshareName
from azure.storage.fileshare import ShareFileClient


load_dotenv()
client=MongoClient(MongoConnectionString)

def base32_decode(encoded_string):
    # Convert the encoded string to bytes
    encoded_bytes = encoded_string.encode("utf-8")

    # Decode the bytes using base32
    decoded_bytes = base64.b32decode(encoded_bytes)

    # Convert the decoded bytes back to a string
    decoded_string = decoded_bytes.decode("utf-8")

    return decoded_string
    
def send_email_with_attachment(sender_email, receiver_email, subject,attachment_path, smtp_server, smtp_port, smtp_user, smtp_password,prescription,orders):

    current_date = datetime.now()
    formatted_date = current_date.strftime("%d %B %Y")

    # Create the email container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    body=f'''Please find attached the case sheet, dated {formatted_date}.
           
    Prescription : {prescription}

    Orders : {orders}'''
    msg.attach(MIMEText(body, 'plain'))

    # Open the PDF file to send as an attachment
    with open(attachment_path, "rb") as attachment_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='CaseSheet.pdf')
        msg.attach(part)

    # Setup the SMTP server and send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")



def download_file_from_share(file_path):
    """
    Downloads a file from Azure File Share.

    :param connection_string: Azure Storage account connection string.
    :param share_name: Name of the file share.
    :param file_path: Path of the file within the file share.
    :param download_path: Local path to save the downloaded file.
    """
    try:
        # Create a ShareFileClient to access the file
        file_client = ShareFileClient.from_connection_string(
            conn_str=FileStorageConnectionString,
            share_name=FileshareName,
            file_path=file_path
        )
        file_name = file_path.split("/")[-1]
        download_path  = f"app/artifacts/sendData/{file_name}"
        # Ensure the directory exists
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        # Download the file
        with open(download_path, "wb") as file:
            data = file_client.download_file()
            file.write(data.readall())

        print(f"File '{file_path}' downloaded successfully to '{download_path}'")
        return download_path

    except Exception as e:
        print(f"Error: {e}")



def send_case_sheet_email(pdf_file_path,orders,prescription,recipient_mail_address):
    # download only neeed if the request is email send 
    pdf_path = download_file_from_share(pdf_file_path)
    db=client.TwigoCred
    collection=db.MailConfig
    mail_config=collection.find_one({"_id":1})
    for key, value in mail_config.items():
        if isinstance(value, str):
            mail_config[key] = base32_decode(mail_config[key])
    send_email_with_attachment(
    sender_email=mail_config['MailId'],
    receiver_email=recipient_mail_address,
    subject="Case Shet",
    attachment_path=pdf_path,
    smtp_server=mail_config['Host'],
    smtp_port=465,  # SSL port
    smtp_user=mail_config['Username'],
    smtp_password=mail_config['Password'],
    orders=orders,
    prescription=prescription)
    
    # removing pdf file 
    os.remove(pdf_path)
