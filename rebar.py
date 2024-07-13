from lib.utils import *
import keyboard
import re
import math

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
        response_dic = {}
        for pile_type in response_list:
            single_type_result = {}
            sheetpile_type, sheetpile_depth = extract_sheetpile_type_depth(pile_type)
            single_type_result['Depth'] = sheetpile_depth
            single_type_result['Type'] = sheetpile_type
            full_name = f"{sheetpile_type} {sheetpile_depth}m"
            response_dic[full_name] = single_type_result

        self.output_path = create_gui(response_dic, "Sheet Pile Rebar")

        # write the response to xml file
        self.save_to_xml(response_list)

        # remove the pdf
        os.remove(self.pdf_path)
    
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
        # 將response_list寫入配筋圖子節點
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
            depth = ET.SubElement(sheetpile, 'Height', description="鋼板樁深度")
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


class BoredPile_rebar(Base_rebar):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ocr_tool = OCRTool(type='en')

    def run(self):
        # init the result dic
        response_dic = {}

        # change pdf to images
        imgs_list = pdf_to_images(self.pdf_path, dpi=300, preprocess=False)

        # extract data from images
        for i, img in enumerate(imgs_list):
            print(f"Processing image {i+1}/{len(imgs_list)}")
            type_name, type_result = self.extract_data(img)

            # add to the response_dic
            response_dic[type_name] = type_result

        self.output_path = create_gui(response_dic, "Bored Pile Rebar")

        # write the response to xml file
        self.save_to_xml(response_dic)

        # remove the pdf
        os.remove(self.pdf_path)

    def save_to_xml(self, response_dic):
        print("資料萃取結果: ", response_dic)
        print("已將資料寫入xml檔案: ", self.output_path)
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
        # 將response_list寫入配筋圖子節點
        for pile_type, pile_info in response_dic.items():
            pile = ET.SubElement(rebars, 'WorkItemType', description="PILE TYPE", TYPE=pile_type)
            # 在 pile 底下建立 Rowpile 子節點
            Rowpile = ET.SubElement(pile, 'Rowpile', description="排樁")
            # 在 pile 底下建立 eam子 節點
            Beam = ET.SubElement(pile, 'Beam', description="繫樑")
            for key, value in pile_info.items():
                if key == "TieBeam":
                    TieBeam_W = ET.SubElement(Beam, 'Width', description="繫樑寬")
                    TieBeam_W_value = ET.SubElement(TieBeam_W, 'Value', unit="mm")
                    TieBeam_W_value.text = str(value)
                    TieBeam_H = ET.SubElement(Beam, 'Length', description="繫樑長")
                    TieBeam_H_value = ET.SubElement(TieBeam_H, 'Value', unit="mm")
                    TieBeam_H_value.text = str(value)
                elif key == "diameter":
                    diameter = ET.SubElement(Rowpile, 'Diameter', description="直徑")
                    diameter_value = ET.SubElement(diameter, 'Value', unit="mm")
                    diameter_value.text = str(value)
                elif key == "depth":
                    depth = ET.SubElement(Rowpile, 'Height', description="深度")
                    depth_value = ET.SubElement(depth, 'Value', unit="mm")
                    depth_value.text = str(value)
                elif key == "ShearRebar":
                    ShearRebar = ET.SubElement(Rowpile, 'ShearRebar', description="剪力筋")
                    ShearRebar_value = ET.SubElement(ShearRebar, 'Value')
                    ShearRebar_value.text = str(value)
                elif key == "Stirrup":
                    Stirrup = ET.SubElement(Rowpile, 'Stirrup', description="箍筋")
                    Stirrup_value = ET.SubElement(Stirrup, 'Value')
                    Stirrup_value.text = str(value)
                elif key == "ConcreteStrength":
                    # 在 Rowpile 底下建立 Concrete 子節點
                    Concrete = ET.SubElement(Rowpile, 'Concrete', description="混凝土")
                    ConcreteStrength = ET.SubElement(Concrete, 'Strength', description="混凝土強度")
                    ConcreteStrength_value = ET.SubElement(ConcreteStrength, 'Value', unit="kgf/cm^2")
                    ConcreteStrength_value.text = str(value)
        
        # 寫入xml檔案，utf-8編碼
        tree.write(self.output_path, encoding="utf-8")
    
    def extract_data(self, img):
            
        # init the result dic
        single_type_result = {
            "type": None,
            "diameter": None,
            "depth": None,
            "TieBeam": [],
            "ShearRebar": None,
            "Stirrup": None,
            "ConcreteStrength": None
        }

        # image preprocessing
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img_th = cv2.threshold (img_gray, 240, 255, 0)

        # OCR
        bounds = self.ocr_tool.ocr(img_th)

        # rotated image clockwise 90 degree
        img_rotated = cv2.rotate(img_th, cv2.ROTATE_90_CLOCKWISE)
        bounds_rotated = self.ocr_tool.ocr(img_rotated)

        # extract data from bounds
        TieBeam = None # 格式為 [x, y]
        BoardPileDetial = None # 格式為 [x, y]
        Section = None # 格式為 [x, y]
        listOfNumbers = [] # 儲存格式為 [數字, [x, y], index]
        listOfShearRebars = [] # 儲存格式為 [文字, [x, y], index]
        listOfstirrups = [] # 儲存格式為 [文字, [x, y], index]
        listOfstrength = [] # 儲存格式為 [文字, [x, y], index

        for i, bound in enumerate(bounds):
            # 找繫樑標註關鍵字
            if bound[1].find("TIE BEAM FOR BORED PILE") != -1:
                TieBeam = bound[0][0]
            # 找出排樁標註關鍵字
            elif bound[1].find("BORED PILE DETAIL") != -1:
                BoardPileDetial = bound[0][0]
            # 找出排樁斷面標註關鍵字
            elif bound[1].find("SECTION") != -1:
                area = (bound[0][0][0] - bound[0][1][0]) * (bound[0][0][1] - bound[0][2][1])
                if area > 15000:
                    Section = bound[0][0]


            # 找出排樁型式
            match = re.match(r'^BORED PILE TYPE ([A-Z]\d+)$', bound[1])
            if match:
                extracted = match.group(1)
                single_type_result["type"] = extracted

            # 找出剪力筋號數
            match = re.match(r'D(\d+)@(\d+)', bound[1])
            if match:
                listOfShearRebars.append([bound[1], bound[0][0], i])

            # 找出挎筋號數
            match = re.match(r'(\d+)-D(\d+)', bound[1])
            if match:
                listOfstirrups.append([bound[1], bound[0][0], i])

            # 找出混凝土強度
            match = re.match(r'(\d+) kgf.*', bound[1])
            if match:
                listOfstrength.append([int(match.group(1)), bound[0][0], i])

            # 找出可以被轉換成int的數字 (預設是標註的那些數字)
            try:
                listOfNumbers.append([int(bound[1]), bound[0][0], i])
            except:
                pass


        # according to the x,y points of bored pile detail, find the most closest int number with using listOfNumbers
        if TieBeam == None or listOfNumbers == []:
            print("TieBeam or listOfNumbers is None")
            single_type_result["TieBeam"] = 'None'
        else:
            min_distance = math.inf
            TeiBeam_index = -1
            for i in range(len(listOfNumbers)):
                distance = math.sqrt((listOfNumbers[i][1][0] - TieBeam[0])**2 + (listOfNumbers[i][1][1] - TieBeam[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    TeiBeam_index = i

            single_type_result["TieBeam"] = listOfNumbers[TeiBeam_index][0]

        if BoardPileDetial == None or listOfNumbers == []:
            print("BoardPileDetial or listOfNumbers is None")
            single_type_result["diameter"] = 'None'
        else:
            min_distance = math.inf
            BoardPile_index = -1
            for i in range(len(listOfNumbers)):
                distance = math.sqrt((listOfNumbers[i][1][0] - BoardPileDetial[0])**2 + (listOfNumbers[i][1][1] - BoardPileDetial[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    BoardPile_index = i

            single_type_result["diameter"] = listOfNumbers[BoardPile_index][0]

        if Section == None or listOfShearRebars == []:
            print("Section or listOfShearRebars is None")
            single_type_result["ShearRebar"] = 'None'
        else:
            min_distance = math.inf
            ShearRebar_index = -1
            for i in range(len(listOfShearRebars)):
                distance = math.sqrt((listOfShearRebars[i][1][0] - Section[0])**2 + (listOfShearRebars[i][1][1] - Section[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    ShearRebar_index = i

            single_type_result["ShearRebar"] = listOfShearRebars[ShearRebar_index][0]

        if Section == None or listOfstirrups == []:
            print("Section or listOfstirrups is None")
            single_type_result["Stirrup"] = 'None'
        else:
            min_distance = math.inf
            Stirrup_index = -1
            for i in range(len(listOfstirrups)):
                distance = math.sqrt((listOfstirrups[i][1][0] - Section[0])**2 + (listOfstirrups[i][1][1] - Section[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    Stirrup_index = i

            single_type_result["Stirrup"] = listOfstirrups[Stirrup_index][0]

        if Section == None or listOfstrength == []:
            print("Section or listOfstrength is None")
            single_type_result["ConcreteStrength"] = 'None'
        else:
            min_distance = math.inf
            ConcreteStrength_index = -1
            for i in range(len(listOfstrength)):
                distance = math.sqrt((listOfstrength[i][1][0] - Section[0])**2 + (listOfstrength[i][1][1] - Section[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    ConcreteStrength_index = i

            single_type_result["ConcreteStrength"] = listOfstrength[ConcreteStrength_index][0]

        # extract data from bounds_rotated
        try:
            single_type_result["depth"] = int(bounds_rotated[0][1])
        except:
            print("depth is None")
            single_type_result["depth"] = 'None'

        return single_type_result["type"], single_type_result


class Diaphragm_rebar():
    def __init__(self) -> None:
        pass