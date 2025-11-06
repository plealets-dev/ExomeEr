import requests
import json
import base64
import requests
import os
from dotenv import load_dotenv

from pymongo import MongoClient
from app.creds.config import  MongoConnectionString, WhatsappBaseUrl, bluejaydoc_url, bluejay_api_key


def get_temp_bluejay_url(storage_path):

  import requests

  url = f"{bluejaydoc_url}?storage_path={storage_path}&api_key={bluejay_api_key}&endpoint=direct_preview"
  print("url", url)
  payload = ""
  headers = {}

  response = requests.request("GET", url, headers=headers, data=payload)

  print(response.text)

  media_url = response.json()


  return media_url["PreUrl"]


client=MongoClient(MongoConnectionString)
db=client.TwigoCred
collection=db.MailConfig

whatsapp_config = collection.find_one({"_id":2})

def send_through_whatsapp(phone_number,prescription,orders,storage_path):
    
    
    file_url= get_temp_bluejay_url(storage_path)
    
    
    message=f'''Prescription : {prescription}
            Orders : {orders}'''
  
    print(file_url)
    
    params = {
        "number": phone_number,
        "type": "media",
        "message": message,
        "instance_id": whatsapp_config['instance_id'],
        "access_token": whatsapp_config['access_token'],
        "media_url": file_url
    }
  
    response = requests.get(WhatsappBaseUrl, params=params)
    if response.status_code==200:
       print("WhatsApp message sent successfully")
    else:
       print("WhatsApp message sent failed !")
       print("Response code: ",response.status_code)
