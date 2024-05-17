from lib.utils import *
import keyboard
import re

# -------------------------------------------------------------------- #
'''
The Base_eval class is a parent class that contains the common methods 
and attributes for all the plan classes.
'''
# -------------------------------------------------------------------- #

class Base_rebar():
    def __init__(self, **kwargs) -> None:
        self.pdf_path = kwargs.get("pdf_path")
        self.csv_path = kwargs.get("csv_path")
        self.output_path = kwargs.get("output_path")
        self.use_azure = kwargs.get("use_azure")
        if self.use_azure:
            self.clinet = construct_GPT4()

    def run(self):
        pass
    def extract_data(self):
        pass
    def save_to_xml(self):
        pass

    def wait_pdf(self):
        """Wait for a PDF file to be available, showing a loading animation."""
        loader = Loader(self.pdf_path + " is being created. Please wait..", "PDF File has been created!", 0.05).start()
        try:
            while not os.path.exists(self.pdf_path):
                if keyboard.is_pressed("esc"):
                    loader.stop()
                    print("PDF creation cancelled by user.")
                    break
            loader.stop()
        except Exception as e:
            print(f"Error during PDF wait: {e}")

# -------------------------------------------------------------------- #

class SheetPile_rebar(Base_rebar):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ocr_tool = OCRTool(type='en')
    
    def extract_data(self, imgs_list):
        num_imgs = len(imgs_list)
        response_list = []

        for i, img in enumerate(imgs_list):
            print(f"Processing image {i+1}/{num_imgs}")
            ocr_results = self.ocr_tool.ocr(img)
            converted_text = None
            for text_info in ocr_results:
                if text_info[1].find("SHEET PILE") != -1:
                    extracted_rawtext = text_info[1]
                    converted_text = self.convert_sheet_pile_typename(extracted_rawtext)
                    response_list.append(converted_text)

        return response_list
    
    def run(self):
        # change pdf to images
        imgs_list = pdf_to_images(self.pdf_path, dpi=210, output_folder="./", drawing_type="sheet_pile-eval")

        # extract data from images
        response_list = self.extract_data(imgs_list)
        
        # remove duplicated response
        response_list = list(set(response_list))

        # write the response to xml file
        self.save_to_xml(response_list)
    
    def save_to_xml(self, response_list):
        print("資料萃取結果: ", response_list)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        rebars = root.find(".//Drawing[@description='配筋圖']")
        if rebars is None:
            rebars = ET.SubElement(root, "Drawing", description="配筋圖")
        else:
            # 移除plans的所有子節點
            for child in list(rebars):
                rebars.remove(child)
        # 將response_list寫入平面圖子節點
        for pile_type in response_list:
            sheetpile_type, sheetpile_depth = extract_sheetpile_type_depth(pile_type)
            print(sheetpile_type, sheetpile_depth)
            pile = ET.SubElement(rebars, 'WorkItemType', description="DEPTH", DEPTH=f"Depth {str(sheetpile_depth)}m")
            # 在pile底下建立Sheetpile子節點
            sheetpile = ET.SubElement(pile, 'Sheetpile', description="鋼板樁")
            # 在pile底下建立type子節點
            type = ET.SubElement(sheetpile, 'Type', description="鋼板樁型號")
            type_value = ET.SubElement(type, 'Value')
            type_value.text = sheetpile_type
            # 在type底下建立height子節點
            depth = ET.SubElement(sheetpile, 'Depth', description="鋼板樁深度")
            depth_value = ET.SubElement(depth, 'Value', unit="m")
            depth_value.text = str(sheetpile_depth)
        
        # 寫入xml檔案，utf-8編碼
        tree.write(self.output_path, encoding="utf-8")

    def convert_sheet_pile_typename(self, sheet_pile_type):
        replacements = {
            "SP-W": "SP-III",
            "SP-MI": "SP-III",
            "SP- m": "SP-III",
            "SP- MI": "SP-III",
            "SP- W": "SP-III",
            "SP- I": "SP-III",
            "SP-I": "SP-III",
            "SP-II": "SP-III",
            "SP- H": "SP-III",
            "SP-H": "SP-III"
        }

        # 通過正則表達式替換以確保只替換完整的詞組
        for key, value in replacements.items():
            pattern = r'\b' + re.escape(key) + r'\b'
            sheet_pile_type = re.sub(pattern, value, sheet_pile_type)

        return sheet_pile_type


class Diaphragm_rebar():
    def __init__(self) -> None:
        pass