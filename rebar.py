from lib.utils import *
import keyboard
import pandas as pd
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
    
    def run(self):
        rows = custom_csv_parser(self.csv_path)

        columns = ["FileName", "EntityName", "ObjectType", "RotationAngle", "CentreCoor", "Height", "Width", "Text"]

        # 將結果轉換為 DataFrame
        df = pd.DataFrame(rows[1:], columns=columns)

        grouped = df.groupby('FileName')
        # 初始化一個集合，用於存儲鋼板樁文字(未經處理)
        sheet_pile_text: set = set()
        # 初始劃一個字典，用於存儲鋼板樁文字(經過處理)
        sheet_pile_text_dict: dict = {}

        for name, group in grouped:
            print(f'File Name: {name}')

            pattern:str=  r"(\S+)\s+SHEET\s+PILE\s+\(L=(\d+)m\)"

            group['Type_name'], group['Length'] = zip(*group['Text'].str.extract(pattern).values)
            group['Length'] = pd.to_numeric(group['Length'], errors='coerce')
            group['Length'] = group['Length'].astype('Int64')

            # get all the sheet pile text without Nan
            sheet_pile_rows: pd.DataFrame = group.dropna(subset=['Type_name', 'Length']).copy()
            # combine the 'Type_name' and 'Length' columns
            sheet_pile_rows['Full_name'] = sheet_pile_rows['Type_name'] + ' ' + sheet_pile_rows['Length'].astype(str) + 'm'
            # add the 'Full_name' to the set
            sheet_pile_text.update(sheet_pile_rows['Full_name'])

        print(sheet_pile_text)
        # extract the sheet pile text from the set and add it to the dictionary
        for text in sheet_pile_text:
            pattern = r"(\S+)\s+(\d+)m"
            name, length = re.match(pattern, text).groups()
            sheet_pile_text_dict[text] = {'name': name, 'length': int(length)}
        
        # wait for the pdf to be created
        self.output_path = create_gui(sheet_pile_text_dict, "Sheet Pile Rebar")

        # write the response to xml file
        self.save_to_xml(sheet_pile_text_dict)

        # remove the pdf
        os.remove(self.csv_path)
    
    def save_to_xml(self, response_dic):
        print("已將資料寫入xml檔案: ", self.output_path)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        rebars = root.find(".//Drawing[@description='配筋圖']")
        if rebars is None:
            rebars = ET.SubElement(root, "Drawing", description="配筋圖")

        # 將response_list寫入配筋圖子節點
        for pile_type, pile_info in response_dic.items():
            sheetpile_type = pile_info['name']
            sheetpile_depth = pile_info['length']
            if check_attribute_exists(rebars, 'DEPTH', f"Depth {str(sheetpile_depth)}m"):
                continue
            else:
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


class BoredPile_rebar(Base_rebar):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def run(self):
        # init the result dic
        response_dic = {}

        rows = custom_csv_parser(self.csv_path)
        columns = ["FileName", "EntityName", "ObjectType", "RotationAngle", "CentreCoor", "Height", "Width", "Text"]

        # 將結果轉換為 DataFrame
        df = pd.DataFrame(rows[1:], columns=columns)

        grouped = df.groupby('FileName')
        # 遍歷每個組
        for name, group in grouped:
            print(f"組名: {name}")

            # 初始化儲存排樁形式的列表
            type_name: str = 'Unknown'
            # 初始化每種類型排樁的資料
            type_data: dict = {'Depth':0,
                            'Diameter':0,
                            'Tiebeam_width':0,
                            'Tiebeam_length':0,
                            'Main_rebar':'Unknown',
                            'Stirrup_rebar':'Unknown',
                            'Concrete_strength':0}
            
            ''' 0. 一些預抓取資料'''
            # EL
            EL_pattern:str = r'^EL\s+(\d+\.\d+)'
            group['Extracted_EL'] = group['Text'].str.extract(EL_pattern)
            group['Extracted_EL'] = group['Extracted_EL'].astype(float)
            EL_min: float = group['Extracted_EL'].dropna().min()
            EL_max: float = group['Extracted_EL'].dropna().max()
            # print(f"EL: {EL_min} ~ {EL_max}")

            # 鋼筋
            stirrup_rebar_pattern:str = r'^D(\d+)@(\d+)$'
            group['Extracted_Rebar_diameter'], group['Extracted_Rebar_spacing'] = zip(*group['Text'].str.extract(stirrup_rebar_pattern).values)
            group['Extracted_Rebar_diameter'] = pd.to_numeric(group['Extracted_Rebar_diameter'], errors='coerce')
            group['Extracted_Rebar_spacing'] = pd.to_numeric(group['Extracted_Rebar_spacing'], errors='coerce')
            group['Extracted_Rebar_diameter'] = group['Extracted_Rebar_diameter'].astype('Int64')
            group['Extracted_Rebar_spacing'] = group['Extracted_Rebar_spacing'].astype('Int64')
            # print(group[group['Extracted_Rebar_diameter'].notna()]['Text'])

            # int numbers
            int_pattern:str = r'^(\d+)$'
            group['Extracted_Int'] = group['Text'].str.extract(int_pattern)
            group['Extracted_Int'] = group['Extracted_Int'].astype(float)
            # print(group[group['Extracted_Int'].notna()]['Text'])

            # 混凝土強度
            concrete_strength_pattern:str = r'(\d+)\s+kgf/cm\\U\+00B2$'
            group['Extracted_Concrete_strength'] = group['Text'].str.extract(concrete_strength_pattern)
            group['Extracted_Concrete_strength'] = group['Extracted_Concrete_strength'].astype(float)
            
            # 主筋
            main_rebar_pattern:str = r'^(\d+)-D(\d+)$'
            group['Extracted_Main_rebar_count'], group['Extracted_Main_rebar_diameter'] = zip(*group['Text'].str.extract(main_rebar_pattern).values)
            group['Extracted_Main_rebar_count'] = pd.to_numeric(group['Extracted_Main_rebar_count'], errors='coerce')
            group['Extracted_Main_rebar_diameter'] = pd.to_numeric(group['Extracted_Main_rebar_diameter'], errors='coerce')
            group['Extracted_Main_rebar_count'] = group['Extracted_Main_rebar_count'].astype('Int64')
            group['Extracted_Main_rebar_diameter'] = group['Extracted_Main_rebar_diameter'].astype('Int64')
            # print(group[group['Extracted_Main_rebar_count'].notna()]['Text'])

            ''' 1. 萃取型號 '''
            type_pattern:str = r'BORED\s+PILE\s+TYPE\s+(\S+)'
            group['Type_name'] = group['Text'].str.extract(type_pattern)
            type_name = group['Type_name'].dropna().unique()
            if len(type_name) > 0:
                type_name = type_name[0]
            else:
                type_name = 'Unknown'
            print(f"型號: {type_name}")
            

            ''' 2. 萃取深度 '''
            Depth = EL_max - EL_min
            type_data['Depth'] = Depth
            print(f"深度: {Depth}")

            ''' 3. 萃取直徑 '''
            # extract the row which 'Text' equals to '場鑄擋土排樁'
            diameter_row:pd.Series = group[group['Text'] == '場鑄擋土排樁']
            x, y, z = parse_coordinate(diameter_row['CentreCoor'].values[0])
            # 尋找距離(x,y)最近的'int number'列
            int_rows:pd.DataFrame = group.dropna(subset=['Extracted_Int']).copy()
            nearest_index:int = find_nearest('Extracted_Int', x, y, int_rows)
            diameter:float = int_rows.iloc[nearest_index]['Extracted_Int']
            type_data['Diameter'] = diameter
            print(f"直徑: {diameter}")

            ''' 4. 混凝土強度 '''
            concrete_strength_rows:pd.DataFrame = group.dropna(subset=['Extracted_Concrete_strength']).copy()
            if len(concrete_strength_rows) > 0:
                concrete_strength:float = concrete_strength_rows['Extracted_Concrete_strength'].values[0]
            else:
                concrete_strength = 0
                print("無法找到混凝土強度")
            type_data['Concrete_strength'] = concrete_strength
            print(f"混凝土強度: {concrete_strength}")

            ''' 5. 主筋 & 箍筋 '''
            section_row:pd.Series = group[group['Text'] == '剖 面']
            if len(section_row) > 1:
                print("找到多個剖面")
            elif len(section_row) == 0:
                print("未找到剖面")
            else:
                x, y, z = parse_coordinate(section_row['CentreCoor'].values[0])
                # 尋找距離(x,y)最近的'main rebar'列
                main_rebar_rows:pd.DataFrame = group.dropna(subset=['Extracted_Main_rebar_count']).copy()
                nearest_index:int = find_nearest('Extracted_Main_rebar_count', x, y, main_rebar_rows)
                main_rebar_count:int = main_rebar_rows.iloc[nearest_index]['Extracted_Main_rebar_count']
                main_rebar_diameter:int = main_rebar_rows.iloc[nearest_index]['Extracted_Main_rebar_diameter']
                type_data['Main_rebar'] = str(main_rebar_count) + '-D' + str(main_rebar_diameter)
                print(f"主筋: {main_rebar_count} - D{main_rebar_diameter}")

                # 尋找距離(x,y)最近的'stirrup rebar'列
                stirrup_rebar_rows:pd.DataFrame = group.dropna(subset=['Extracted_Rebar_diameter']).copy()
                nearest_index:int = find_nearest('Extracted_Rebar_diameter', x, y, stirrup_rebar_rows)
                stirrup_rebar_diameter:int = stirrup_rebar_rows.iloc[nearest_index]['Extracted_Rebar_diameter']
                stirrup_rebar_spacing:int = stirrup_rebar_rows.iloc[nearest_index]['Extracted_Rebar_spacing']
                type_data['Stirrup_rebar'] = 'D' + str(stirrup_rebar_diameter) + '@' + str(stirrup_rebar_spacing)
                print(f"箍筋: D{stirrup_rebar_diameter} @ {stirrup_rebar_spacing}")

            ''' 6. 梁寬 & 梁長 '''
            beam_row:pd.Series = group[group['Text'] == '擋土排樁繫梁詳圖']
            if len(beam_row) > 1:
                print("找到多個擋土排樁繫梁詳圖")
            elif len(beam_row) == 0:
                print("未找到擋土排樁繫梁詳圖")
            else:
                x, y, z = parse_coordinate(beam_row['CentreCoor'].values[0])
                # 尋找距離(x,y)最近的'int number'列
                int_rows:pd.DataFrame = group.dropna(subset=['Extracted_Int']).copy()
                nearest_index:int = find_nearest('Extracted_Int', x, y, int_rows)
                beam_width:float = int_rows.iloc[nearest_index]['Extracted_Int']
                type_data['Tiebeam_width'] = beam_width
                print(f"梁寬: {beam_width}")
                
                int_rotated_rows:pd.DataFrame = group.dropna(subset=['Extracted_Int']).copy()
                int_rotated_rows = int_rotated_rows[int_rotated_rows['RotationAngle'] != '0.0']
                nearest_index:int = find_nearest('Extracted_Int', x, y, int_rotated_rows)
                beam_length:float = int_rotated_rows.iloc[nearest_index]['Extracted_Int']
                type_data['Tiebeam_length'] = beam_length
                print(f"梁長: {beam_length}")

            response_dic[type_name] = type_data

        self.output_path = create_gui(response_dic, "Bored Pile Rebar")

        # write the response to xml file
        self.save_to_xml(response_dic)

        # remove the pdf
        os.remove(self.csv_path)

    def save_to_xml(self, response_dic):
        print("已將資料寫入xml檔案: ", self.output_path)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        rebars = root.find(".//Drawing[@description='配筋圖']")
        if rebars is None:
            rebars = ET.SubElement(root, "Drawing", description="配筋圖")

        # 將response_list寫入配筋圖子節點
        for pile_type, pile_info in response_dic.items():
            if check_attribute_exists(rebars, 'TYPE', pile_type):
                continue
            else:
                pile = ET.SubElement(rebars, 'WorkItemType', description="PILE TYPE", TYPE=pile_type)
                # 在 pile 底下建立 Rowpile 子節點
                Rowpile = ET.SubElement(pile, 'Rowpile', description="排樁")
                # 在 pile 底下建立 Beam子 節點
                Beam = ET.SubElement(pile, 'Beam', description="繫樑")
                for key, value in pile_info.items():
                    if key == "Tiebeam_width":
                        TieBeam_W = ET.SubElement(Beam, 'Width', description="繫樑寬")
                        TieBeam_W_value = ET.SubElement(TieBeam_W, 'Value', unit="mm")
                        TieBeam_W_value.text = str(value)
                    elif key == "Tiebeam_length":
                        TieBeam_H = ET.SubElement(Beam, 'Length', description="繫樑長")
                        TieBeam_H_value = ET.SubElement(TieBeam_H, 'Value', unit="mm")
                        TieBeam_H_value.text = str(value)
                    elif key == "Diameter":
                        diameter = ET.SubElement(Rowpile, 'Diameter', description="直徑")
                        diameter_value = ET.SubElement(diameter, 'Value', unit="mm")
                        diameter_value.text = str(value)
                    elif key == "Depth":
                        depth = ET.SubElement(Rowpile, 'Height', description="深度")
                        depth_value = ET.SubElement(depth, 'Value', unit="m")
                        depth_value.text = str(value)
                    elif key == "Main_rebar":
                        ShearRebar = ET.SubElement(Rowpile, 'ShearRebar', description="剪力筋")
                        ShearRebar_value = ET.SubElement(ShearRebar, 'Value')
                        ShearRebar_value.text = str(value)
                    elif key == "Stirrup_rebar":
                        Stirrup = ET.SubElement(Rowpile, 'Stirrup', description="箍筋")
                        Stirrup_value = ET.SubElement(Stirrup, 'Value')
                        Stirrup_value.text = str(value)
                    elif key == "Concrete_strength":
                        # 在 Rowpile 底下建立 Concrete 子節點
                        Concrete = ET.SubElement(Rowpile, 'Concrete', description="混凝土")
                        ConcreteStrength = ET.SubElement(Concrete, 'Strength', description="混凝土強度")
                        ConcreteStrength_value = ET.SubElement(ConcreteStrength, 'Value', unit="kgf/cm^2")
                        ConcreteStrength_value.text = str(value)
        
        # 寫入xml檔案，utf-8編碼
        tree.write(self.output_path, encoding="utf-8")


class Diaphragm_rebar():
    def __init__(self) -> None:
        pass