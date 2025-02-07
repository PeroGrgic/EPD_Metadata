import requests
import logging
import os
import json
import enum
import sys
import glob

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class i14y_api_calls():

    def __init__(self, auth_token, directory_path):
        self.AUTH_TOKEN = auth_token
        self.DIRECTORY_PATH = directory_path
    
    def post_file(self, file_path, concept_id):
        headers = {
            'Authorization': f'Bearer {self.AUTH_TOKEN}',
            'accept': '*/*'
        }
        
        POST_URL = f'https://api.i14y.admin.ch/api/partner/v1/concepts/{concept_id}/codelist-entries/imports/json'

            
        # Check if the file exists before making the request
        if not os.path.isfile(file_path):
            logging.error(f"File not found: {file_path}")
            return

        # Prepare the file to be sent in the request
        files = {'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/json')}
        
        try:
            logging.info(f"Posting file to URL: {POST_URL}")
            response = requests.post(POST_URL, headers=headers, files=files)
            response.raise_for_status()  # Raise an error for bad status codes
            logging.info("File posted successfully")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
        return None

    def fetch_data(self): #TODO: verbinden mit save_data_to_file
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.AUTH_TOKEN}'
        }
        
        logging.info(f"Fetching data from URL: {self.GET_URL}")
        
        try:
            response = requests.get(self.GET_URL, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            logging.info("Received response from the API")
            return data
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
        return None
    
    def delete_codelist_entries(self, concept_id):
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.AUTH_TOKEN}'
        }
        DELETE_URL = f'https://api.i14y.admin.ch/api/partner/v1/concepts/{concept_id}/codelist-entries'

        try:
            logging.info(f"Sending DELETE request to URL: {DELETE_URL}")
            response = requests.delete(DELETE_URL, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
            logging.info("DELETE request successful")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
        return None
    
    def save_data_to_file(data, file_path):
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            logging.info(f"Data has been written to {file_path}")
        except Exception as e:
            logging.error(f"Failed to write data to file: {e}")

    def update_codelist_entries (self, file_path, concept_id):
        self.delete_codelist_entries(concept_id)
        self.post_file(file_path, concept_id)
    
    def post_all_valuesets(self, directory_path):
        # Find all JSON files in the directory
        json_files = glob.glob(os.path.join(directory_path, "*_transformed.json"))
 
        print(f"Found {len(json_files)} files to process")

        for json_file in json_files:
            # Get the codelist ID based on filename
            print(f"Processing file: {json_file}")
            codelist_id = self.get_codelist_id(json_file)

            if codelist_id:
                print(f"Posting {json_file} with codelist ID: {codelist_id.value}")
                self.update_codelist_entries(json_file, codelist_id.value)
            else:
                print(f"No matching codelist ID found for {json_file}")

    def get_codelist_id(self, filename):
        # Map filename patterns to enum values
        mapping = {
            'SubmissionSet.contentTypeCode_transformed': codeListsId.SubmissionSet_contentTypeCode,
            'EprRole_transformed': codeListsId.EprRole,
            'HCProfessional.hcProfession_transformed': codeListsId.HCProfessional_hcProfession,
            'DocumentEntry.classCode_transformed': codeListsId.DocumentEntry_classCode,
            'DocumentEntry.confidentialityCode_transformed': codeListsId.DocumentEntry_confidentialityCode,
            'DocumentEntry.eventCodeList_transformed': codeListsId.DocumentEntry_eventCodeList,
            'DocumentEntry.formatCode_transformed': codeListsId.DocumentEntry_formatCode,
            'DocumentEntry.healthcareFacilityTypeCode_transformed': codeListsId.DocumentEntry_healthcareFacilityTypeCode,
            'DocumentEntry.mimeType_transformed': codeListsId.DocumentEntry_mimeType,
            'DocumentEntry.practiceSettingCode_transformed': codeListsId.DocumentEntry_practiceSettingCode,
            'DocumentEntry.sourcePatientInfo.PID-8_transformed': codeListsId.DocumentEntry_sourcePatientInfo_PID_8,
            'DocumentEntry.typeCode_transformed': codeListsId.DocumentEntry_typeCode,
            'EprAuditTrailConsumptionEventType_transformed': codeListsId.EprAuditTrailConsumptionEventType,
            'EprDeletionStatus_transformed': codeListsId.EprDeletionStatus,
            'EprPurposeOfUse_transformed': codeListsId.EprPurposeOfUse,
            'DocumentEntry.languageCode_transformed': codeListsId.DocumentEntry_languageCode
        }
    
        # Remove file extension and path to get base filename
        base_filename = os.path.splitext(os.path.basename(filename))[0]
        # Return corresponding enum value or None if not found
        return mapping.get(base_filename)

class codeListsId(enum.Enum):
    #Id of codelists version 2.0.0
    SubmissionSet_contentTypeCode = '08dd3ac4-5400-26c2-9c23-aa5161d6f1ee'
    EprRole = '08dd3ac5-3368-7166-8321-752d51b4c7fa' #The value sets SubmissionSet.Author.AuthorRole and DocumentEntry.author.authorRole are referencing this value set
    HCProfessional_hcSpecialisation = '' #import content from value set 
    HCProfessional_hcProfession = '08dd3acd-7a56-0e11-b17a-793d26b64c01'
    DocumentEntry_classCode = '08dd3a24-ed88-0a70-9837-bd77662abde7'
    DocumentEntry_author_authorSpeciality = '' #i14y hat Probleme und ich kann keine neue version erstellen
    DocumentEntry_confidentialityCode = '08dd3ac7-c913-0f55-add6-6e700fbd0b5a'
    DocumentEntry_eventCodeList = '08dd3ac7-f8c5-1206-a6be-6a18a5d03aaf'
    DocumentEntry_formatCode = '08dd3ac8-2381-0ee1-a776-b33cd44de513'
    DocumentEntry_healthcareFacilityTypeCode ='08dd3ac8-4ae2-c5a2-ac9a-9570e73e6bf4'
    DocumentEntry_mimeType = '08dd3ac8-b015-2aa9-8c23-41e386fd578a'
    DocumentEntry_practiceSettingCode = '08dd3ac8-d173-9334-9f4f-84c5b4f7c665'
    DocumentEntry_sourcePatientInfo_PID_8 = '08dd3ac9-0867-a02f-83c7-49f36a893f9d'
    DocumentEntry_typeCode = '08dd3acb-b3be-14a8-9fea-5275a5798da7'
    EprAuditTrailConsumptionEventType = '08dd3acb-d3eb-355a-a495-4ec8a225f127'
    EprDeletionStatus = '08dd3acc-4897-11b5-ab2f-20a123bbc17c'
    DocumentEntry_languageCode = '08dd3acc-c0f2-6dcf-8612-d87241707c19'
    EprPurposeOfUse = '08dd3acc-eee9-b32e-ba19-4bb6f87f502b'

# Main execution

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python I14_API_handling.py <directory_path> <I14Y_user_token>")
        sys.exit(1)

    directory_path = sys.argv[1]
    i14y_user_tokern = sys.argv[2]
    
    #auth_token = sys.argv[2]
    api_handler = i14y_api_calls(i14y_user_tokern, directory_path=directory_path,)
    api_handler.post_all_valuesets(directory_path)
    logging.info("Script execution completed.")

#TODO: Erstellen neuer Version eines VS implementieren
#TODO: Agrs anpassen um alles notwendige beim ausführen anzugeben. [1] dir path [2] auth token [3] welche operation ausgeführt werden soll (upload (new VS oder CodeListEntries), download, delete)