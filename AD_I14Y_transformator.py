import json
import sys
import csv
import os
import re

class AD_csv_to_i14y_json():
    
    def __init__(self, csv_file_path, output_file_path):
        self.csv_file_path = csv_file_path
        self.json_output_file_path = output_file_path
        self.codeListEntries = []

    def start(self):
        print("Starting to read CSV file on path: " + self.csv_file_path)

    def process_csv(self):
        import csv
        with open(self.csv_file_path, 'r', encoding="utf-8") as csvfile:
            file = csv.reader(csvfile, quotechar='"', delimiter=';')
            next(file)  # Skip first row
            
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

                synonymPS = Synonym("Preferred Synonym")
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

                synonymAS = Synonym("Acceptable Synonym")
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

    def write_to_json(self):
        output = create_json_output(self.codeListEntries)

        with open(self.json_output_file_path, 'w', encoding="utf-8") as json_file:
            json.dump(output, json_file, indent=4, ensure_ascii=False)

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
        if title == "Preferred Synonym":
            self.identifier = "PS"
        else :
            self.identifier = "AS"
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
        
def read_file(file_path, encoding="utf-8"):
    with open(file_path, 'r', encoding=encoding) as csvfile:
        file = csv.reader(csvfile, quotechar='"', delimiter=';')
        next(file)  # Skip first row
        next(file)  # Skip second row
        
        codes = []
        for row in file:
            if row[0] == "Code":
                code = Code()
                code.set_code(row[1])
                code.set_DisplayNameEN(row[2])
                code.set_DisplayNameDE(row[3])
                code.set_DisplayNameFR(row[4])
                code.set_DisplayNameIT(row[5])
                code.set_DisplayNameRM(row[6])
                codes.append(code)
            elif row[0] == "CodeSystem":
                codeSystem = CodeSystem()
                codeSystem.set_Title(row[1])
                codeSystem.set_Text_DE(row[2])
                codeSystem.set_Text_FR(row[3])
                codeSystem.set_Text_IT(row[4])
                codeSystem.set_Text_EN(row[5])
                codeSystem.set_Text_RM(row[6])
                codeSystem.set_Identifier(row[7])
                codeSystem.set_URI(row[8])
                return codeSystem
        return codes

def create_json_output(codeListEntries):
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
                "type": "Synonym"
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
                    "type": "Synonym"
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
    
    return {"codeListEntries": output}

if __name__ == "__main__":
    
    args = sys.argv[1:]
    if len(args) != 2:
        print("Usage: python AD_I14Y_transformator.py <input_folder_path> <output_folder_path>")
        sys.exit(1)
        
    input_folder = args[0]
    output_folder = args[1]
    
    os.makedirs(output_folder, exist_ok=True)
    
    print("Starting transformation of CSV files...")
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            input_file = os.path.join(input_folder, filename)
            
            # Extract text between "VS " and "("
            match = re.search(r'VS (.*?)\(', filename)
            if match:
                new_filename = match.group(1).strip() + '_transformed.json'
            else:
                new_filename = filename.replace('.csv', '_transformed.json')
                
            output_file = os.path.join(output_folder, new_filename)
            
            print(f"Processing {filename}...")
            transformer = AD_csv_to_i14y_json(input_file, output_file)
            transformer.process_csv()
            transformer.write_to_json()
            print(f"Transformed {filename} -> {new_filename}")
    
    print(f"All transformations complete. Output files written to: {output_folder}")
