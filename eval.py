from lib.utils import *
import keyboard

# -------------------------------------------------------------------- #
'''
The Base_eval class is a parent class that contains the common methods 
and attributes for all the plan classes.
'''
# -------------------------------------------------------------------- #

class Base_eval():
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

class SheetPile_eval(Base_eval):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.prompt = "Tell me if the drawing is about a sheet pile, if not return 'None', if yes tell me the type of the sheet pile and the length of it. please response as the following template:{pile_type}:{length} e.g. SP-III:10m. just return the template, do not return any other information." 
        self.ocr_tool = OCRTool(type="en")
    def extract_data(self, imgs_list):
        num_imgs = len(imgs_list)
        response_list = []

        for i, img in enumerate(imgs_list):
            print(f"Processing image {i+1}/{num_imgs}")

            if self.use_azure:
                # construct roboflow model
                self.robo_model = construct_robolow_model()

                # predict the image
                result = self.robo_model.predict(img, confidence=10, overlap=30).json()

                # split the image into blocks
                for k, block in enumerate(block_split_by_roboflow(result)):
                    x, y, w, h = block
                    crop_img = img[int(y):int(h), int(x):int(w)]
                    block_img_path = f"{self.output_path}/block_{k+1}_img_{i+1}.png"
                    cv2.imwrite(block_img_path, crop_img)
                    img_url = local_image_to_data_url(block_img_path)
                    response = GPT4_call(self.client, img_url, self.prompt)
                    response_list.append(response.choices[0].message.content)
                    os.remove(block_img_path)
            else:
                ocr_reulst = self.ocr_tool.ocr(img)
                response = []
                converted_text = None
                for text_info in ocr_reulst:
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

        # remove the pdf
        os.remove(self.pdf_path)

    def save_to_xml(self, response_list):
        print("資料萃取結果: ",response_list)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        evals = root.find(".//Drawing[@description='立面圖']")
        if evals is None:
            evals = ET.SubElement(root, "Drawing", description="立面圖")
        else:
            # 移除plans的所有子節點
            for child in list(evals):
                evals.remove(child)
        # 將response_list寫入平面圖子節點
        for pile_type in response_list:
            sheetpile_type, sheetpile_depth = extract_sheetpile_type_depth(pile_type)
            print(sheetpile_type, sheetpile_depth)
            pile = ET.SubElement(evals, 'WorkItemType', description="DEPTH", DEPTH=f"Depth {str(sheetpile_depth)}m")
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
            
        tree.write(self.output_path, encoding="utf-8")




    
    def convert_sheet_pile_typename(self, sheet_pile_type):
            # 檢查是否含有 "SP-W" 或 "SP-MI"
        if "SP-W" in sheet_pile_type:
            # 將 "SP-W" 替換為 "SP-III"
            sheet_pile_type = sheet_pile_type.replace("SP-W", "SP-III")
            return sheet_pile_type
        elif "SP-MI" in sheet_pile_type:
            # 將 "SP-MI" 替換為 "SP-III"
            sheet_pile_type = sheet_pile_type.replace("SP-MI", "SP-III")
            return sheet_pile_type
        elif "SP- m" in sheet_pile_type:
            # 將 "SP-MI" 替換為 "SP-III"
            sheet_pile_type = sheet_pile_type.replace("SP- m", "SP-III")
            return sheet_pile_type
        elif "SP- MI" in sheet_pile_type:
            # 將 "SP-MI" 替換為 "SP-III"
            sheet_pile_type = sheet_pile_type.replace("SP- MI", "SP-III")
            return sheet_pile_type
        elif "SP- W" in sheet_pile_type:
            # 將 "SP-MI" 替換為 "SP-III"
            sheet_pile_type = sheet_pile_type.replace("SP- W", "SP-III")
            return sheet_pile_type
        else:
            # 如果輸入不含有 "SP-W" 或 "SP-MI"，返回原始輸入
            return sheet_pile_type

        

    

class Diaphragm_eval(Base_eval):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def run(self):
        pass