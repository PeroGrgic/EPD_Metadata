import json
import sys
import csv
import os
import re
import xml.etree.ElementTree as ET
import enum


class AD_csv_to_i14y_json():
    
    def __init__(self, file_path, output_file_path, file_name):
        self.file_path = file_path
        self.json_output_file_path = output_file_path
        self.codeListEntries = []
        self.fileExtension = None
        self.concept = concept()
        self.fileName = file_name

    def start(self):
        print("Starting to read CSV file on path: " + self.file_path)

    def process_csv(self):
        self.fileExtension ="csv"
        with open(self.file_path, 'r', encoding="utf-8") as csvfile:
            file = csv.reader(csvfile, quotechar='"', delimiter=';')
        
            # Read first row to get ValueSet info
            first_row = next(file)[0]  # Get first element of first row
        
            # Extract name and identifier using regex
            name_match = re.search(r'Value Set (.*?) -', first_row)
            identifier_match = re.search(r'- ([\d.]+)', first_row)
        
            # Create concept instance and set values
            concept_instance = concept()
            if name_match:
                concept_instance.set_name(name_match.group(1))
            if identifier_match:
                concept_instance.set_identifier(identifier_match.group(1))
            
            # Read second row to set indexes
            index_row = next(file)
            indexDEps = next((i for i, x in enumerate(index_row) if "de-CH" in x and "preferred" in x), None)
            indexENps = next((i for i, x in enumerate(index_row) if "en-US" in x and "preferred" in x), None)
            indexITps = next((i for i, x in enumerate(index_row) if "it-CH" in x and "preferred" in x), None)
            indexRMps = next((i for i, x in enumerate(index_row) if "rm-CH" in x and "preferred" in x), None)
            indexFRps = next((i for i, x in enumerate(index_row) if "fr-CH" in x and "preferred" in x), None)
            indexDEas = next((i for i, x in enumerate(index_row) if "de-CH" in x and "synonym" in x), None)
            indexENas = next((i for i, x in enumerate(index_row) if "en-US" in x and "synonym" in x), None)
            indexITas = next((i for i, x in enumerate(index_row) if "it-CH" in x and "synonym" in x), None)
            indexRMas = next((i for i, x in enumerate(index_row) if "rm-CH" in x and "synonym" in x), None)
            indexFRas = next((i for i, x in enumerate(index_row) if "fr-CH" in x and "synonym" in x), None)            
            # Process remaining rows
            for row in file:
                code = Code()
                code.set_code(row[2])
                code.set_DisplayNameEN(row[3]) #this is the DisplayName of the code
                if indexDEps is not None:
                    code.set_DisplayNameDE(row[indexDEps])
                if indexFRps is not None:
                    code.set_DisplayNameFR(row[indexFRps])
                if indexITps is not None:
                    code.set_DisplayNameIT(row[indexITps])
                if indexRMps is not None:
                    code.set_DisplayNameRM(row[indexRMps])

                codeSystem = CodeSystem()
                codeSystem.set_Title(row[5])
                codeSystem.set_Text_DE(row[5])
                codeSystem.set_Text_FR(row[5])
                codeSystem.set_Text_IT(row[5])
                codeSystem.set_Text_EN(row[5])
                codeSystem.set_Text_RM(row[5])
                codeSystem.set_Identifier(row[4])

                synonymPS = Synonym("Preferred")
                if indexENps is not None:
                    synonymPS.set_text_EN(row[indexENps])#this is the EN synonym of the code
                if indexDEps is not None:
                    synonymPS.set_text_DE(row[indexDEps])
                if indexFRps is not None:
                    synonymPS.set_text_FR(row[indexFRps])
                if indexITps is not None:
                    synonymPS.set_text_IT(row[indexITps])
                if indexRMps is not None:
                    synonymPS.set_text_RM(row[indexRMps])

                synonymAS = Synonym("Acceptable")
                if indexENas is not None:
                    synonymAS.set_text_EN(row[indexENas])#this is the EN synonym of the code
                if indexDEas is not None:
                    synonymAS.set_text_DE(row[indexDEas])
                if indexFRas is not None:
                    synonymAS.set_text_FR(row[indexFRas])
                if indexITas is not None:
                    synonymAS.set_text_IT(row[indexITas])
                if indexRMas is not None:
                    synonymAS.set_text_RM(row[indexRMas])

                periodStart = Period("start")
                periodStart.set_Date("01.06.2024")
                periodEnd = Period("end")
                periodEnd.set_Date("01.06.2100")

                self.codeListEntries.append([code, codeSystem, periodStart, periodEnd, synonymPS, synonymAS])

    def process_xml(self):
        self.fileExtension = "xml"
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        value_set = root.find('.//valueSet')
        concept_instance = concept()
        concept_instance.set_name(value_set.get('name'))
        concept_instance.set_identifier(value_set.get('id'))
        print(self.get_codelist_id(self.fileName))

        concept_instance.set_id(self.get_codelist_id(self.fileName))

        # Create mapping of codeSystem ids to their names
        code_system_mapping = {}
        for source_code_system in value_set.findall('sourceCodeSystem'):
            code_system_mapping[source_code_system.get('id')] = source_code_system.get('identifierName')

        # Get descriptions for each language
        for desc in value_set.findall('desc'):
            lang = desc.get('language')
            # Check for div first, if not found use direct text
            div = desc.find('div')
            text = div.text.strip() if div is not None else desc.text.strip()
        
            if lang == 'de-CH':
                concept_instance.set_descriptionDE(text)
            elif lang == 'en-US':
                concept_instance.set_descriptionEN(text)
            elif lang == 'fr-CH':
                concept_instance.set_descriptionFR(text)
            elif lang == 'it-CH':
                concept_instance.set_descriptionIT(text)

        for concept_elem in value_set.findall('.//concept'):
            code = Code()
            code.set_code(concept_elem.get('code'))
        
            # Create synonyms
            synonymPS = Synonym("Preferred")
            synonymAS = Synonym("Acceptable")
        
            # Process designations based on type
            for designation in concept_elem.findall('designation'):
                lang = designation.get('language')
                text = designation.get('displayName')
                desig_type = designation.get('type')
            
                if desig_type == 'preferred':
                    if lang == 'de-CH':
                        synonymPS.set_text_DE(text)
                    elif lang == 'en-US':
                        synonymPS.set_text_EN(text)
                    elif lang == 'fr-CH':
                        synonymPS.set_text_FR(text)
                    elif lang == 'it-CH':
                        synonymPS.set_text_IT(text)
                    elif lang == 'rm-CH':
                        synonymPS.set_text_RM(text)
                elif desig_type == 'synonym':
                    if lang == 'de-CH':
                        synonymAS.set_text_DE(text)
                    elif lang == 'en-US':
                        synonymAS.set_text_EN(text)
                    elif lang == 'fr-CH':
                        synonymAS.set_text_FR(text)
                    elif lang == 'it-CH':
                        synonymAS.set_text_IT(text)
                    elif lang == 'rm-CH':
                        synonymAS.set_text_RM(text)
                    
            codeSystem = CodeSystem()
            code_system_id = concept_elem.get('codeSystem')
            codeSystem.set_Title(code_system_mapping.get(code_system_id))
            codeSystem.set_Identifier(code_system_id)
        
            periodStart = Period("start")
            periodStart.set_Date("01.06.2024")
            periodEnd = Period("end")
            periodEnd.set_Date("01.06.2100")
        
            self.codeListEntries.append([code, codeSystem, periodStart, periodEnd, synonymPS, synonymAS])
            self.concept = concept_instance

    def create_concept_output(self):
        codeListEntries_output = create_codeListEntries_output(self.codeListEntries)        
        output = {
            "data": {
                "codeListEntries": codeListEntries_output["data"],
                "codeListEntryValueMaxLength": 13,
                "codeListEntryValueType": "Numeric",
                "conceptType": "CodeList",
                "conformsTo": [],
                "description": {
                    "de": self.concept.get_descriptionDE(),
                    "en": self.concept.get_descriptionEN(),
                    "fr": self.concept.get_descriptionFR(),
                    "it": self.concept.get_descriptionIT()
                },
                "id": self.concept.get_id(),
                "identifier": self.concept.get_identifier(),
                "isLocked": False,
                "keywords": [],
                "name": {
                    "de": self.concept.get_name(),
                    "en": self.concept.get_name(),
                    "fr": self.concept.get_name(),
                    "it": self.concept.get_name()
                },
                "publicationLevel": "Internal",
                "publisher": {
                    "identifier": "CH_eHealth",
                    "name": {
                        "de": "eHealth Suisse",
                        "en": "eHealth Suisse",
                        "fr": "eHealth Suisse",
                        "it": "eHealth Suisse"
                    }
                },
                "registrationStatus": "Incomplete",
                "responsibleDeputy": {
                    "id": "08db7190-7358-9c21-8114-9743e9051aa2",
                    "identifier": "stefanie.neuenschwander@e-health-suisse.ch",
                    "name": "Neuenschwander Stefanie eHealth Suisse",
                    "firstName": "",
                    "lastName": ""
                },
                "responsiblePerson": {
                    "id": "08db0048-2e29-6f1b-9c94-70cc06980c35",
                    "identifier": "pero.grgic@e-health-suisse.ch",
                    "name": "Grgic Pero eHealth Suisse",
                    "firstName": "",
                    "lastName": ""
                },
                "themes": [],
                "validFrom": "2024-05-31T22:00:00+00:00",
                "version": "2.0.0"
            }
        }
        
        return output

#TODO: Beim Output für XML wird der Name des Codes nicht übernommen. Zudem fehlen auch die Acceptable Synonyms.
    def write_to_json(self):
        if self.fileExtension == "csv":
            output = create_codeListEntries_output(self.codeListEntries)
        elif self.fileExtension == "xml":
            output = self.create_concept_output()
        
        with open(self.json_output_file_path, 'w', encoding="utf-8") as json_file:
            json.dump(output, json_file, indent=4, ensure_ascii=False)

    def get_codelist_id(self, filename):
        # Map filename patterns to enum values
        mapping = {
            'SubmissionSet.contentTypeCode': codeListsId.SubmissionSet_contentTypeCode.value,
            'EprRole': codeListsId.EprRole.value,
            'HCProfessional.hcProfession': codeListsId.HCProfessional_hcProfession.value,
            'DocumentEntry.classCode': codeListsId.DocumentEntry_classCode.value,
            'DocumentEntry.confidentialityCode': codeListsId.DocumentEntry_confidentialityCode.value,
            'DocumentEntry.eventCodeList': codeListsId.DocumentEntry_eventCodeList.value,
            'DocumentEntry.formatCode': codeListsId.DocumentEntry_formatCode.value,
            'DocumentEntry.healthcareFacilityTypeCode': codeListsId.DocumentEntry_healthcareFacilityTypeCode.value,
            'DocumentEntry.mimeType': codeListsId.DocumentEntry_mimeType.value,
            'DocumentEntry.practiceSettingCode': codeListsId.DocumentEntry_practiceSettingCode.value,
            'DocumentEntry.sourcePatientInfo.PID-8': codeListsId.DocumentEntry_sourcePatientInfo_PID_8.value,
            'DocumentEntry.typeCode': codeListsId.DocumentEntry_typeCode.value,
            'EprAuditTrailConsumptionEventType': codeListsId.EprAuditTrailConsumptionEventType.value,
            'EprDeletionStatus': codeListsId.EprDeletionStatus.value,
            'EprPurposeOfUse': codeListsId.EprPurposeOfUse.value,
            'DocumentEntry.languageCode': codeListsId.DocumentEntry_languageCode.value
        }
    
        # Remove file extension and path to get base filename
        # Return corresponding enum value or None if not found
        return mapping.get(filename)

class Code():
    def __init__(self):
        self.Code = None
        self.DisplayNameEN = None
        self.DisplayNameDE = None
        self.DisplayNameFR = None
        self.DisplayNameIT = None
        self.DisplayNameRM = None
    def set_code(self, code):
        self.Code = code
    def set_DisplayNameEN(self, displayNameEN):
        self.DisplayNameEN = displayNameEN
    def set_DisplayNameDE(self, displayNameDE):
        self.DisplayNameDE = displayNameDE
    def set_DisplayNameFR(self, displayNameFR):
        self.DisplayNameFR = displayNameFR
    def set_DisplayNameIT(self, displayNameIT):
        self.DisplayNameIT = displayNameIT
    def set_DisplayNameRM(self, displayNameRM):
        self.DisplayNameRM = displayNameRM
    def get_code(self):
        return self.Code
    def get_DisplayNameEN(self):
        return self.DisplayNameEN
    def get_DisplayNameDE(self):
        return self.DisplayNameDE
    def get_DisplayNameFR(self):
        return self.DisplayNameFR
    def get_DisplayNameIT(self):
        return self.DisplayNameIT
    def get_DisplayNameRM(self):
        return self.DisplayNameRM

class CodeSystem():
    def __init__(self):
        self.Title = None
        self.Text_DE = None
        self.Text_FR = None
        self.Text_IT = None
        self.Text_EN = None
        self.Text_RM = None
        self.Identifier = None
        self.URI = None
    def set_Title(self, title):
        self.Title = title
    def set_Text_DE(self, textDE):
        self.Text_DE = textDE
    def set_Text_FR(self, textFR):
        self.Text_FR = textFR
    def set_Text_IT(self, textIT):
        self.Text_IT = textIT
    def set_Text_EN(self, textEN):
        self.Text_EN = textEN
    def set_Text_RM(self, textRM):
        self.Text_RM = textRM
    def set_Identifier(self, identifier):
        self.Identifier = identifier
    def get_Title(self):
        return self.Title
    def get_Text_DE(self):
        return self.Text_DE
    def get_Text_FR(self):
        return self.Text_FR
    def get_Text_IT(self):
        return self.Text_IT
    def get_Text_EN(self):
        return self.Text_EN
    def get_Text_RM(self):
        return self.Text_RM
    def get_Identifier(self):
        return self.Identifier
    def get_URI(self):
        return self.URI   

class Period():
    def __init__(self, period_type):
        self.Title = period_type
        self.Date = None
        self.Identifier = period_type
        self.URI = None
    def set_Date(self, date):
        self.Date = date
    def get_Date(self):
        return self.Date

class Synonym():
    def __init__(self, title):
        self.Title = title
        self.Text_DE = None
        self.Text_FR = None
        self.Text_IT = None
        self.Text_EN = None
        self.Text_RM = None
        if title == "Preferred":
            self.identifier = "900000000000548007"
        else :
            self.identifier = "900000000000549004"
        self.URI = None

    def set_text_DE(self, text_DE):
        self.Text_DE = text_DE
    def set_text_FR(self, text_FR):
        self.Text_FR = text_FR
    def set_text_IT(self, text_IT):
        self.Text_IT = text_IT
    def set_text_EN(self, text_EN):
        self.Text_EN = text_EN
    def set_text_RM(self, text_RM):
        self.Text_RM = text_RM
    def get_text_DE(self):
        return self.Text_DE
    def get_text_FR(self):
        return self.Text_FR
    def get_text_IT(self):
        return self.Text_IT
    def get_text_EN(self):
        return self.Text_EN
    def get_text_RM(self):
        return self.Text_RM
    def get_identifier(self):
        return self.identifier
    def get_URI(self):
        return self.URI

class concept():
     def __init__(self):
        self.codeListEntryValueMaxLength = 14
        self.codeListEntryValueType = "String"
        self.conceptType = "CodeList"
        self.descriptionDE = None #description of the concept in german
        self.descriptionEN = None
        self.descriptionFR = None
        self.descriptionIT = None
        self.descriptionRM = None
        self.id = None #ID of concept, which is getting a new version
        self.identifier = None #human readable identifier of the concept
        self.name = None #name of the concept is same in all languages
        self.publicationLevel = "Internal"
        self.publisher_identifier = "CH_eHealth"
        self.publisher_name = "eHealth Suisse" #same in all languages
        self.validFrom = None #date from which the concept is valid. needs to be in "YYYY-MM-DD" format
        self.version = None #version of the concept. needs to be in "0.0.0" format
    
     def set_descriptionDE(self, descriptionDE):
        self.descriptionDE = descriptionDE

     def set_descriptionEN(self, descriptionEN):
        self.descriptionEN = descriptionEN

     def set_descriptionFR(self, descriptionFR):
        self.descriptionFR = descriptionFR

     def set_descriptionIT(self, descriptionIT):
        self.descriptionIT = descriptionIT

     def set_descriptionRM(self, descriptionRM):
        self.descriptionRM = descriptionRM

     def set_id(self, id):
        self.id = id

     def set_identifier(self, identifier):
        self.identifier = identifier

     def set_name (self, name):
        self.name = name
     
     def set_validFrom(self, validFrom):
        self.validFrom = validFrom
     
     def set_version(self, version):
        self.version = version

     def get_descriptionDE(self):
        return self.descriptionDE

     def get_descriptionEN(self):
        return self.descriptionEN

     def get_descriptionFR(self):
        return self.descriptionFR

     def get_descriptionIT(self):
        return self.descriptionIT
     
     def get_name(self):
        return self.name
     
     def get_identifier(self):
        return self.identifier
     
     def get_id(self):
        return self.id

        
def create_codeListEntries_output(codeListEntries):
    output = []
    
    for entry_list in codeListEntries:
        code = entry_list[0]  # Code object
        codeSystem = entry_list[1]  # CodeSystem object
        periodStart = entry_list[2]  # Period object
        periodEnd = entry_list[3]  # Period object
        synonymPS = entry_list[4]  # Synonym object
        synonymAS = entry_list[5] if len(entry_list) > 5 else None  # Synonym object (optional)
        
        # Create base annotations list
        annotations = [
            {
                "identifier": codeSystem.Identifier,
                "text": {
                    "de": codeSystem.Text_DE,
                    "en": codeSystem.Text_EN,
                    "fr": codeSystem.Text_FR,
                    "it": codeSystem.Text_IT,
                    "rm": codeSystem.Text_RM
                },
                "title": codeSystem.Title,
                "type": "CodeSystem"
            },
            {
                "identifier": periodEnd.Identifier,
                "text": {
                    "en": periodEnd.Date
                },
                "title": periodEnd.Title,
                "type": "Period"
            },
            {
                "identifier": periodStart.Identifier,
                "text": {
                    "en": periodStart.Date
                },
                "title": periodStart.Title,
                "type": "Period"
            },
            {
                "identifier": synonymPS.identifier,
                "text": {
                    "de": synonymPS.Text_DE,
                    "en": synonymPS.Text_EN,
                    "fr": synonymPS.Text_FR,
                    "it": synonymPS.Text_IT,
                    "rm": synonymPS.Text_RM
                },
                "title": synonymPS.Title,
                "type": "Designation"
            }
        ]
          # Add synonymAS to annotations if it exists
        if synonymAS is not None:
            text_dict = {}
            if synonymAS.Text_DE and synonymAS.Text_DE.strip():
                text_dict["de"] = synonymAS.Text_DE
            if synonymAS.Text_EN and synonymAS.Text_EN.strip():
                text_dict["en"] = synonymAS.Text_EN
            if synonymAS.Text_FR and synonymAS.Text_FR.strip():
                text_dict["fr"] = synonymAS.Text_FR
            if synonymAS.Text_IT and synonymAS.Text_IT.strip():
                text_dict["it"] = synonymAS.Text_IT
            if synonymAS.Text_RM and synonymAS.Text_RM.strip():
                text_dict["rm"] = synonymAS.Text_RM
        
            if text_dict:  # Only add if there are non-empty text entries
                annotations.append({
                    "identifier": synonymAS.identifier,
                    "text": text_dict,
                    "title": synonymAS.Title,
                    "type": "Designation"
                })
        json_entry = {
            "annotations": annotations,
            "code": code.Code,
            "name": {
                "de": code.DisplayNameDE,
                "en": code.DisplayNameEN,
                "fr": code.DisplayNameFR,
                "it": code.DisplayNameIT,
                "rm": code.DisplayNameRM
            }
        }
        output.append(json_entry)
    
    return {"data": output}



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


class publisherPersons():
    def __init__(self):
        self.PGR = {
            "id": "08db0048-2e29-6f1b-9c94-70cc06980c35",
            "identifier": "pero.grgic@e-health-suisse.ch",
            "name": "Grgic Pero eHealth Suisse",
            "firstName": "",
            "lastName": ""
        }
        self.SNE = {
            "id": "08db7190-7358-9c21-8114-9743e9051aa2",
            "identifier": "stefanie.neuenschwander@e-health-suisse.ch",
            "name": "Neuenschwander Stefanie eHealth Suisse",
            "firstName": "",
            "lastName": ""
        }

    def get_PGR(self):
        return {
            "PGR": self.PGR,
        }
    def get_SNE(self):
        return {
            "SNE": self.SNE,
        }

    
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        print("Usage: python AD_I14Y_transformator.py <input_folder_path> <output_folder_path>")
        sys.exit(1)
        
    input_folder = args[0]
    output_folder = args[1]
    
    os.makedirs(output_folder, exist_ok=True)
    
    print("Starting transformation of files...")
    for filename in os.listdir(input_folder):
        if filename.endswith(('.csv', '.xml')):
            input_file = os.path.join(input_folder, filename)
            
            # Extract text between "VS " and "("
            match = re.search(r'VS (.*?)\(', filename)
            if match:
                new_filename = match.group(1).strip() + '_transformed.json'
            else:
                new_filename = filename.replace('.csv', '_transformed.json').replace('.xml', '_transformed.json')
                
            output_file = os.path.join(output_folder, new_filename)
            
            print(f"Processing {filename}...")
            file_name = re.search(r'VS (.*?)\(', filename).group(1).strip()
            transformer = AD_csv_to_i14y_json(input_file, output_file, file_name)
            
            if filename.endswith('.csv'):
                transformer.process_csv()
            else:
                transformer.process_xml()
                
            transformer.write_to_json()
            print(f"Transformed {filename} -> {new_filename}")
    
    print(f"All transformations complete. Output files written to: {output_folder}")


#TODO: Mapping handling ergänzen
#TODO: Schrieben von ganzen ValueSet implementieren

