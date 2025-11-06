from pymongo import MongoClient
from app.creds.config import MongoConnectionString, DbName, TranscriptionCollection
from datetime import datetime
# Establish a connection to MongoDB

client = MongoClient(MongoConnectionString)
db = client[DbName]
collection = db[TranscriptionCollection]



async def upload_transcription_to_mongo(document_id, chunk_id, blob_name, enhanced_audio_blob_path, language_code ,original_text, translated_text, service, purpose,  latest_diarized_text_list = False, isgeneral = False, ErrorLog = False, isAudioEnhanced = False, enhancedDetails = None):
    # Specify the _id of the document you want to update
    # document_id = 1234  # Replace this with your actual _id value
    
    print("chunkid", chunk_id)

    chunk_data = {
        chunk_id: {
            "FilePath": blob_name,
            "LanguageCode": language_code,
            "TranslatedText": translated_text,
            "OriginalText": original_text,
            "Service": service,
            "Purpose": purpose,
            "isAudioEnhanced": isAudioEnhanced,
            "EnhancedAudioPath": "",
            "enhancedDetails": enhancedDetails,
            "CreatedAt": datetime.utcnow()
           
        }
    }

    if latest_diarized_text_list:
        chunk_data[chunk_id]["DiarizationText"] =  latest_diarized_text_list
    if isAudioEnhanced:
        chunk_data[chunk_id]["EnhancedAudioPath"] =  enhanced_audio_blob_path


    

    
    # Define the fields you want to update
    update_fields = {"$set": chunk_data, "$setOnInsert": {"CreatedOn": datetime.utcnow()}}  # Add your field(s) and new value(s) here
    if isgeneral:
        result = db[purpose].update_one({"_id": document_id}, update_fields, upsert=True)

    elif ErrorLog:
        result = db["AudioErrorLog"].update_one({"_id": document_id}, update_fields, upsert=True)

    else:    
    # Perform the update
        result = collection.update_one({"_id": document_id}, update_fields, upsert=True)

    # Check if the document was updated
    # Check if a new document was inserted
    if result.upserted_id is not None:
        print("Document didn't exist and was inserted with _id:", result.upserted_id)
    else:
        print("Document updated successfully.")
   

