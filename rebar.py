from lib.utils import *
import keyboard
import string
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

        columns: list = ["FileName", "EntityName", "ObjectType", "RotationAngle", "CentreCoor", "Height", "Width", "Text"]

        # 將結果轉換為 DataFrame
        df: pd.DataFrame = pd.DataFrame(rows[1:], columns=columns)

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
    def __init__(self, **kwargs) -> None:
        self.rebar_path = kwargs.get("csv_path")
        self.vertical_path = kwargs.get("vertical_path")
        self.v_helper_path = kwargs.get("v_helper_path")
        self.sh_helper_path = kwargs.get("sh_helper_path")
        self.output_path = kwargs.get("output_path")

    def run(self):

        def custom_csv_parser(file_path, encoding='ISO-8859-1'):
            rows = []
            with open(file_path, encoding=encoding) as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) > 8:
                        row[7] = ', '.join(row[7:])
                        row = row[:8]
                    row[-1] = row[-1].rstrip(', ')
                    rows.append(row)
            return rows
        
        def extract_types(text: str) -> list:
            matches = re.findall(r'[A-Z]\d+-?\d?[A-Z]?', text)
            return matches

        def parse_coordinate(coord_str: str) -> list:
            # 使用正則表達式提取坐標值
            match = re.match(r'\(([\d.]+)\s+([\d.]+)\s+([\d.]+)\)', coord_str)
            if match:
                return [float(match.group(1)), float(match.group(2)), float(match.group(3))]
            else:
                raise ValueError(f"無法解析坐標: {coord_str}")\
                
        def parse_coordinate2(coord_str: str) -> list:
            # 使用正則表達式提取坐標值
            match = re.match(r'\(([\d.]+)\s+([\d.]+)\)', coord_str)
            if match:
                return [float(match.group(1)), float(match.group(2))]
            else:
                raise ValueError(f"無法解析坐標: {coord_str}")\

        def transform_vertical_coords(row):
            start_y = row['StartCoor'][1]
            end_y = row['EndCoor'][1]
            
            if start_y >= end_y:
                # Swap StartCoor and EndCoor
                return [row['EndCoor'], row['StartCoor']]
            else:
                return [row['StartCoor'], row['EndCoor']]
            
        def find_nearest(candidate_columns: str, x: float, y: float, df: pd.DataFrame) -> int:
            """
            Find the index of the nearest row in the DataFrame based on the given coordinates.

            Parameters:
            - candidate_columns (str): The column name(s) to consider as candidates for nearest rows.
            - x (float): The x-coordinate of the target point.
            - y (float): The y-coordinate of the target point.
            - df (pd.DataFrame): The DataFrame to search for nearest rows.

            Returns:
            - int: The index of the nearest row in the DataFrame.
            """
            # 選擇有效的候選行（非空值）
            candidate_rows = df[df[candidate_columns].notna()]

            # 解析候選行的坐標
            candidate_coords = np.array([parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

            # 創建目標坐標
            target_coords = np.array([x, y])

            # 計算距離
            distances = np.sqrt(np.sum((candidate_coords[:, :2] - target_coords)**2, axis=1))

            # 找出最近的點
            nearest_index = np.argmin(distances)

            # 返回最近點的相應列
            return nearest_index
        
        def v_rebar_find_el(candidate_columns: str, y: float, df: pd.DataFrame)-> float:
            '''
            Fine the index of the nearest(only consider the y distance) and the bigger y value row in the DataFrame based on the given coordinates.

            Parameters:
            - candidate_columns (str): The column name(s) to consider as candidates for nearest rows.
            - y (float): The y-coordinate of the target point.
            - df (pd.DataFrame): The DataFrame to search for nearest rows.

            Returns:
            - int: The level of the nearest row in the DataFrame.
            '''
            # 選擇有效的候選行（非空值）
            candidate_rows = df[df[candidate_columns].notna()].reset_index()
            

            # 解析候選行的坐標
            candidate_coords = np.array([parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

            # 篩選出 y 坐標大於目標 y 坐標的行
            valid_indices = candidate_coords[:, 1] > y
            candidate_coords = candidate_coords[valid_indices]
            candidate_rows = candidate_rows[valid_indices].reset_index(drop=True)

            # 找出距離 y 坐標最近的行
            distances = np.abs(candidate_coords[:, 1] - y)
            nearest_index = np.argmin(distances)
            # print(nearest_index)
            # print(candidate_rows.iloc[nearest_index])
            result_level = candidate_rows.iloc[nearest_index]['EL_GL']
            # print(result_level)

            return result_level

        def v_rebar_find_side(x:float, y: float, df: pd.DataFrame)-> str:
            # 選擇有效的候選行（非空值）
            candidate_rows = df.reset_index()

            # 解析候選行的坐標
            candidate_coords = np.array([parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

            # 篩選出 y 坐標小於目標 y 坐標的行
            valid_indices = candidate_coords[:, 1] < y
            candidate_coords = candidate_coords[valid_indices]
            candidate_rows = candidate_rows[valid_indices].reset_index(drop=True)

            # 創建目標坐標
            target_coords = np.array([x, y])

            # 計算距離
            distances = np.sqrt(np.sum((candidate_coords[:, :2] - target_coords)**2, axis=1))

            # 找出最近的點
            nearest_index = np.argmin(distances)

            result_side = candidate_rows.iloc[nearest_index]['Text']

            return result_side

        def v_rebar_find_rebar_dia(x:float, y: float, df: pd.DataFrame)-> float:
            # 選擇有效的候選行（非空值）
            candidate_rows = df.reset_index()

            # 解析候選行的坐標
            candidate_coords = np.array([parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

            # 篩選出 y 坐標大於目標 y 坐標的行
            valid_indices = candidate_coords[:, 1] > y
            candidate_coords = candidate_coords[valid_indices]
            candidate_rows = candidate_rows[valid_indices].reset_index(drop=True)

            # 創建目標坐標
            target_coords = np.array([x, y])

            # 計算距離
            distances = np.sqrt(np.sum((candidate_coords[:, :2] - target_coords)**2, axis=1))

            # 找出最近的點
            nearest_index = np.argmin(distances)

            result_dia = candidate_rows.iloc[nearest_index]['Extracted_Rebar_diameter']

            return result_dia

        def sh_rebar_find_rebar_dia(x:float, y: float, df: pd.DataFrame)-> float:
            # 選擇有效的候選行（非空值）
            candidate_rows = df.reset_index()

            # 解析候選行的坐標
            candidate_coords = np.array([parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

            # 創建目標坐標
            target_coords = np.array([x, y])

            # 計算距離
            distances = np.sqrt(np.sum((candidate_coords[:, :2] - target_coords)**2, axis=1))

            # 找出最近的點
            nearest_index = np.argmin(distances)

            result_dia = candidate_rows.iloc[nearest_index]['Extracted_Rebar_diameter']

            return result_dia

        def sh_rebar_find_rebar_spac(x:float, y: float, df: pd.DataFrame)-> float:
            # 選擇有效的候選行（非空值）
            candidate_rows = df.reset_index()

            # 解析候選行的坐標
            candidate_coords = np.array([parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

            # 創建目標坐標
            target_coords = np.array([x, y])

            # 計算距離
            distances = np.sqrt(np.sum((candidate_coords[:, :2] - target_coords)**2, axis=1))

            # 找出最近的點
            nearest_index = np.argmin(distances)

            result_spac = candidate_rows.iloc[nearest_index]['Extracted_Rebar_spacing']

            return result_spac

        def v_rebar_find_rebar_spac(x:float, y: float, df: pd.DataFrame)-> float:
            # 選擇有效的候選行（非空值）
            candidate_rows = df.reset_index()

            # 解析候選行的坐標
            candidate_coords = np.array([parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

            # 篩選出 y 坐標大於目標 y 坐標的行
            valid_indices = candidate_coords[:, 1] > y
            candidate_coords = candidate_coords[valid_indices]
            candidate_rows = candidate_rows[valid_indices].reset_index(drop=True)

            # 創建目標坐標
            target_coords = np.array([x, y])

            # 計算距離
            distances = np.sqrt(np.sum((candidate_coords[:, :2] - target_coords)**2, axis=1))

            # 找出最近的點
            nearest_index = np.argmin(distances)

            result_spac = candidate_rows.iloc[nearest_index]['Extracted_Rebar_spacing']

            return result_spac
        
        # 讀取csv檔案
        rows = custom_csv_parser(self.rebar_path)
        columns = ["FileName", "EntityName", "ObjectType", "RotationAngle", "CentreCoor", "Height", "Width", "Text"]
        df = pd.DataFrame(rows[1:], columns=columns)
        print(self.v_helper_path)
        df_helper = pd.read_csv(self.v_helper_path, encoding='Big5')
        df_vertical = pd.read_csv(self.vertical_path, encoding='Big5')
        df_sh_helper = pd.read_csv(self.sh_helper_path, encoding='Big5')

        

        # helper 預處理
        helper_group = df_helper.groupby('FileName')
        matched_helper = []
        for name, file_helper in helper_group:
            # fileter out the vertical
            file_vertical:pd.DataFrame = df_vertical[df_vertical['FileName'] == name]
            # parse vertical's start and end coordinate
            file_vertical.loc[:, 'StartCoor'] = file_vertical['StartCoor'].apply(lambda x: parse_coordinate(x))
            file_vertical.loc[:, 'EndCoor'] = file_vertical['EndCoor'].apply(lambda x: parse_coordinate(x))
            
            # parse helper's base point
            file_helper.loc[:, 'BasePoint'] = file_helper['BasePoint'].apply(lambda x: parse_coordinate(x))
            # check all the line in vertical is really vertical, delete the line which is not vertical
            file_vertical:pd.DataFrame = file_vertical.assign(is_vertical=file_vertical.apply(lambda row: row['StartCoor'][0] == row['EndCoor'][0], axis=1))
            file_vertical = file_vertical[file_vertical['is_vertical']].drop(columns=['is_vertical'])

            file_vertical[['StartCoor', 'EndCoor']] = file_vertical.apply(transform_vertical_coords, axis=1, result_type='expand')
            # 新增兩個欄位以儲存對應的垂直線段的 StartCoor 和 EndCoor
            file_helper['MatchedStartCoor'] = None
            file_helper['MatchedEndCoor'] = None

            # 檢查每個 helper 的基準點是否有通過一條 vertical 線段
            for index, helper_row in file_helper.iterrows():
                base_x, base_y, _ = helper_row['BasePoint']
                
                # 找到與該基準點 x 座標一致且 y 座標範圍包含基準點的所有線段
                for line_index, line_row in file_vertical.iterrows():
                    start_x, start_y, _ = line_row['StartCoor']
                    end_y = line_row['EndCoor'][1]

                    if base_x == start_x and min(start_y, end_y) <= base_y <= max(start_y, end_y):
                        file_helper.at[index, 'MatchedStartCoor'] = line_row['StartCoor']
                        file_helper.at[index, 'MatchedEndCoor'] = line_row['EndCoor']
                        # 將匹配的線段從 file_vertical 中移除
                        file_vertical = file_vertical.drop(index=line_index)
                        break  # 假設一個 helper 只會對應到一條線段，找到後直接跳出
            
            # 刪除 MatchedStartCoor 為 None 的行
            file_helper = file_helper.dropna(subset=['MatchedStartCoor'])

            # 檢查每個 helper 的 MatchedStartCoor 和 MatchedEndCoor 是否需要更新
            for index, helper_row in file_helper.iterrows():
                matched_start_x, matched_start_y, _ = helper_row['MatchedStartCoor']
                matched_end_x, matched_end_y, _ = helper_row['MatchedEndCoor']

                matched_line_length = abs(matched_start_y - matched_end_y)
                
                # 檢查是否有需要連接的線段
                for _, line_row in file_vertical.iterrows():
                    line_start_x, line_start_y, _ = line_row['StartCoor']
                    line_end_x, line_end_y, _ = line_row['EndCoor']
                    
                    if matched_start_x == line_end_x:
                        distatnce = abs(matched_start_y - line_end_y)
                        if distatnce < matched_line_length*0.1:
                            # 更新 MatchedStartCoor
                            # print('update start')
                            file_helper.at[index, 'MatchedStartCoor'] = line_row['StartCoor']
                            break
                    elif matched_end_x == line_start_x:
                        distatnce = abs(matched_end_y - line_start_y)
                        if distatnce < matched_line_length*0.1:
                            # 更新 MatchedEndCoor
                            # print('update end')
                            file_helper.at[index, 'MatchedEndCoor'] = line_row['EndCoor']
                            break
            
            # 輸出結果
            # print(file_helper[['BasePoint', 'MatchedStartCoor', 'MatchedEndCoor']])
            matched_helper.append(file_helper)

        # 將匹配的 helper 結果合併
        combined_helpers  = pd.concat(matched_helper, ignore_index=True)
        combined_helpers['top_y'] = combined_helpers['MatchedEndCoor'].apply(lambda x: x[1])
        combined_helpers['top_x'] = combined_helpers['MatchedEndCoor'].apply(lambda x: x[0])
        combined_helpers['down_y'] = combined_helpers['MatchedStartCoor'].apply(lambda x: x[1])
        combined_helpers['down_x'] = combined_helpers['MatchedStartCoor'].apply(lambda x: x[0])
        combined_helpers['x'] = combined_helpers['BasePoint'].apply(lambda x: x[0])
        combined_helpers['y'] = combined_helpers['BasePoint'].apply(lambda x: x[1])

        # 主循環
        response_dic = {}
        grouped = df.groupby('FileName')
        for name, group in grouped:
            print(f"組名: {name}")

            # 初始化儲存連續壁形式的列表
            type_name: list = []
            # 初始化每種類型連續壁的資料
            type_data: dict = {'Depth': 0, 
                            'Type': 'Unkown',
                            'Thickness': 0, 
                            'Protection': 0, 
                            'H_rebar':{'Retained_Side':{'Diameter':0, 'Spacing':0}, 'Extracted_Side':{'Diameter':0, 'Spacing':0}}, 
                            'V_rebar':{},
                            'S_rebar':{},
                            'Empty_depth': 0.0,
                            'Real_depth': 0.0}

            ''' 0. 一些預抓取資料'''
            # EXCAVATED SIDE
            pattern: str = r'\(EXCAVATED\s+SIDE\)'
            group['Extracted_Side'] = group['Text'].str.contains(pattern, regex=True)
            # RETAINED SIDE
            pattern: str = r'\(RETAINED\s+SIDE\)'
            group['Retained_Side'] = group['Text'].str.contains(pattern, regex=True)
            # ELEVATION
            pattern: str = r'^ELEVATION'
            group['Extracted_Elevation'] = group['Text'].str.contains(pattern, regex=True)
            # GL
            GL_pattern:str = r'GL\s*(\d+\.\d+)\s*%%P'
            group['Extracted_GL'] = group['Text'].str.extract(GL_pattern)
            group['Extracted_GL'] = group['Extracted_GL'].astype(float)
            GL: float = group['Extracted_GL'].dropna().iloc[0]
            # EL
            EL_pattern = r'^EL\s*(\d+\.\d+)'
            group['Extracted_EL'] = group['Text'].str.extract(EL_pattern)
            group['Extracted_EL'] = group['Extracted_EL'].astype(float)
            EL: float = group['Extracted_EL'].dropna().min()
            # int numbers
            int_pattern = r'^(\d+)$'
            group['Extracted_Int'] = group['Text'].str.extract(int_pattern)
            group['Extracted_Int'] = group['Extracted_Int'].astype(float)
            # 空打
            knockout_pattern: str = r'1000\s*%%P'
            contains_knockout: pd.Series = group['Text'].str.contains(knockout_pattern, regex=True)
            knockout_exists: bool = contains_knockout.any()
            # print(f"是否包含空打: {knockout_exists}")
            # 鋼筋
            rebar_pattern:str = r'^\d?D(\d+)@(\d+)\*?$'
            group['Extracted_Rebar_diameter'], group['Extracted_Rebar_spacing'] = zip(*group['Text'].str.extract(rebar_pattern).values)
            group['Extracted_Rebar_diameter'] = pd.to_numeric(group['Extracted_Rebar_diameter'], errors='coerce')
            group['Extracted_Rebar_spacing'] = pd.to_numeric(group['Extracted_Rebar_spacing'], errors='coerce')
            group['Extracted_Rebar_diameter'] = group['Extracted_Rebar_diameter'].astype('Int64')
            group['Extracted_Rebar_spacing'] = group['Extracted_Rebar_spacing'].astype('Int64')
            # print(group[group['Extracted_Rebar_diameter'].notna()]['Text'])

            
            ''' 1. 萃取型號 '''
            # 定義連續壁型號的正則表達式
            type_pattern: str = r'^DIAPHRAGM\s+WALL\s+TYPE\s+'
            group['Extracted_Types'] = group['Text'].str.contains(type_pattern, regex=True)
            type_rows: pd.DataFrame = group[group['Extracted_Types']==True].copy()
            type_rows['Types_list'] = type_rows['Text'].apply(extract_types)
            # 將提取的型號添加到列表中
            for i in range(len(type_rows)):
                type_name.extend(type_rows.iloc[i]['Types_list'])
                type_name: list = list(set(type_name))
            
            if len(type_name) == 0:
                print(f"{name}，找不到連續壁型號")
            else:
                print(f"連續壁型號: {type_name}")
                type_data['Type'] = type_name[0]

            ''' 2. 萃取厚度 '''
            # 獲取 X 最小的'EXCAVATED SIDE'列,回傳一個Series
            excavated_rows: pd.DataFrame = group[group['Extracted_Side']==True].copy()
            excavated_rows['X'] = excavated_rows['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
            excavated_rows['Y'] = excavated_rows['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
            excavated_rows = excavated_rows.sort_values('X')
            excavated_row: pd.Series = excavated_rows.iloc[0]
            most_left_excavated_x: float = excavated_row['X']
            most_left_excavated_y: float = excavated_row['Y']
            # print(f"最左邊的'EXCAVATED SIDE'列的X座標: {most_left_excavated_x}, Y座標: {most_left_excavated_y}")
            # 獲取 X 最小的'RETAINED SIDE'列,回傳一個Series
            retained_rows: pd.DataFrame = group[group['Retained_Side']==True].copy()
            retained_rows['X'] = retained_rows['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
            retained_rows['Y'] = retained_rows['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
            retained_rows = retained_rows.sort_values('X')
            retained_row = retained_rows.iloc[0]
            most_left_retained_x = retained_row['X']
            most_left_retained_y = retained_row['Y']
            # print(f"最左邊的'RETAINED SIDE'列的X座標: {most_left_retained_y}, Y座標: {most_left_retained_y}")
            # 尋找int number中 X 座標與 Y 座標介於兩者之間的列
            int_rows: pd.DataFrame = group.dropna(subset=['Extracted_Int']).copy()
            int_rows['X'] = int_rows['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
            int_rows['Y'] = int_rows['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
            int_rows = int_rows[(int_rows['X'] > most_left_excavated_x) & (int_rows['X'] < most_left_retained_x) & (int_rows['Y'] >= most_left_retained_y - 2) & (int_rows['Y'] <= most_left_excavated_y + 2)]
            int_row: pd.Series = int_rows.sort_values('X').iloc[0]
            type_data['Thickness'] = int_row['Extracted_Int']

            ''' 3. 萃取深度 '''
            if GL and EL:
                type_data['Depth'] = round((GL - EL), 2)

            ''' 4. 萃取保護層 '''
            protection_pattern: str = r'^(\d+)\s+CL'
            group['Extracted_Protection'] = group['Text'].str.extract(protection_pattern)
            group['Extracted_Protection'] = group['Extracted_Protection'].astype(float)
            type_data['Protection'] = group['Extracted_Protection'].dropna().iloc[0]

            ''' 5. 萃取水平鋼筋 '''
            # 尋找 X 最小的'ELEVATION'列,回傳一個Series
            elevation_rows: pd.DataFrame = group[group['Extracted_Elevation']==True].copy()
            elevation_rows['X'] = elevation_rows['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
            elevation_rows['Y'] = elevation_rows['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
            elevation_rows = elevation_rows.sort_values('X')
            elevation_row: pd.Series = elevation_rows.iloc[0]
            # print(f"最左邊的'ELEVATION'列的X座標: {elevation_row['X']}, Y座標: {elevation_row['Y']}")
            elevation_x: float = elevation_row['X']
            elevation_y: float = elevation_row['Y']
            # 尋找距離'ELEVATION'最近的'EXCAVATED SIDE'列
            nearest_excavated_index: int = find_nearest('Extracted_Side', elevation_x, elevation_y, excavated_rows)
            nearest_excavated_row: pd.Series = excavated_rows.iloc[nearest_excavated_index]
            nearest_excavated_x: float = nearest_excavated_row['X']
            nearest_excavated_y: float = nearest_excavated_row['Y']
            # print(f"距離'ELEVATION'最近的'EXCAVATED SIDE'列的X座標: {nearest_excavated_row['X']}, Y座標: {nearest_excavated_row['Y']}")
            # 尋找距離'ELEVATION'最近的'RETAINED SIDE'列
            nearest_retained_index: int = find_nearest('Retained_Side', elevation_x, elevation_y, retained_rows)
            nearest_retained_row: pd.Series = retained_rows.iloc[nearest_retained_index]
            nearest_retained_x: float = nearest_retained_row['X']
            nearest_retained_y: float = nearest_retained_row['Y']
            # print(f"距離'ELEVATION'最近的'RETAINED SIDE'列的X座標: {nearest_retained_row['X']}, Y座標: {nearest_retained_row['Y']}")
            # 尋找距離'excavated'最近的 'Extracted_Rebar_diameter'列
            rebar_rows: pd.DataFrame = group.dropna(subset=['Extracted_Rebar_diameter']).copy()
            nearest_excavated_rebar_index: int = find_nearest('Extracted_Rebar_diameter', nearest_excavated_x, nearest_excavated_y, rebar_rows)
            nearest_excavated_rebar_row: pd.Series = rebar_rows.iloc[nearest_excavated_rebar_index]
            # print(f"距離'excavated'最近的 'Extracted_Rebar_diameter'列的X座標: {nearest_excavated_rebar_row['CentreCoor']}, {nearest_excavated_rebar_row['Extracted_Rebar_diameter']}, {nearest_excavated_rebar_row['Extracted_Rebar_spacing']}")
            # 尋找距離'retained'最近的 'Extracted_Rebar_diameter'列
            nearest_retained_rebar_index: int = find_nearest('Extracted_Rebar_diameter', nearest_retained_x, nearest_retained_y, rebar_rows)
            nearest_retained_rebar_row: pd.Series = rebar_rows.iloc[nearest_retained_rebar_index]
            # print(f"距離'retained'最近的 'Extracted_Rebar_diameter'列的X座標: {nearest_retained_rebar_row['CentreCoor']}, {nearest_retained_rebar_row['Extracted_Rebar_diameter']}, {nearest_retained_rebar_row['Extracted_Rebar_spacing']}")
            type_data['H_rebar']['Retained_Side']['Diameter'] = nearest_retained_rebar_row['Extracted_Rebar_diameter']
            type_data['H_rebar']['Retained_Side']['Spacing'] = nearest_retained_rebar_row['Extracted_Rebar_spacing']
            type_data['H_rebar']['Extracted_Side']['Diameter'] = nearest_excavated_rebar_row['Extracted_Rebar_diameter']
            type_data['H_rebar']['Extracted_Side']['Spacing'] = nearest_excavated_rebar_row['Extracted_Rebar_spacing']

            ''' 6. 萃取剪力鋼筋(Sv, Sh)、空打深度、實打深度 '''
            Depth: float = type_data['Depth']
            if Depth == 0:
                print(f'深度為0, 請檢查')
                # 彈跳錯誤
                continue

            S_rebar: dict = {}
            # 獲取 'Extracted_Int' 非 na 且 'RotationAngle' 非 0 的
            rotated_int_rows:pd.DataFrame = group.dropna(subset=['Extracted_Int']).copy()
            rotated_int_rows = rotated_int_rows[rotated_int_rows['RotationAngle'] != '0.0']
            rotated_int_rows['X'] = rotated_int_rows['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
            rotated_int_rows['Y'] = rotated_int_rows['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
            rotated_int_rows = rotated_int_rows.sort_values('X')
            min_rotated_int_row: pd.Series = rotated_int_rows.iloc[0]
            # 尋找所有 rotated_int_rows 中與 min_rotated_int_row 的 X 座標相差不超過1的行
            rotated_int_rows = rotated_int_rows[(rotated_int_rows['X'] >= min_rotated_int_row['X'] - 0.1) & (rotated_int_rows['X'] <= min_rotated_int_row['X'] + 0.1)]
            rotated_int_rows = rotated_int_rows.sort_values('Y')
            # 將 rotated_int_rows 的 'Extracted_Int' 轉換為 list
            # print(rotated_int_rows[['CentreCoor', 'Text']])
            rotated_int_list: list = rotated_int_rows['Extracted_Int'].tolist() # 順序為由深到淺

            # 判斷是否有空打
            if knockout_exists:
                # 獲取空打深度
                type_data['Empty_depth'] = Depth - (sum(rotated_int_list)/1000 + 1)
                # 獲取實打深度
                type_data['Real_depth'] = Depth - type_data['Empty_depth']
            # print(f"空打深度: {type_data['Empty_depth']}, 實打深度: {type_data['Real_depth']}")

            # Sv 鋼筋
                # 獲取 'Extracted_Rebar_diameter' 非 na 且 'RotationAngle' 非 0 的
            rotated_rebar_rows: pd.DataFrame = group.dropna(subset=['Extracted_Rebar_diameter']).copy()
            rotated_rebar_rows = rotated_rebar_rows[rotated_rebar_rows['RotationAngle'] != '0.0']
            rotated_rebar_rows['X'] = rotated_rebar_rows['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
            rotated_rebar_rows['Y'] = rotated_rebar_rows['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
                # 獲取 rotated_rebar_rows 中與 int_row 的 X 座標相差不超過 0.5 的行
            rotated_rebar_rows = rotated_rebar_rows[(rotated_rebar_rows['X'] >= int_row['X'] - 0.5) & (rotated_rebar_rows['X'] <= int_row['X'] + 0.5)]
            rotated_rebar_rows = rotated_rebar_rows.sort_values('Y') # 由深到淺
            # print(rotated_int_list)
            # print(rotated_rebar_rows[['Text','Y']])

            # Sh 鋼筋
                # 符號處理
                    # 找純字母
            section_df = pd.DataFrame()
                    # 初始化字母序列，從 'B' 開始
            letters = list(string.ascii_uppercase)[1:]  # ['B', 'C', 'D', ..., 'Z']

                    # 遍歷字母序列並依次篩選
            for letter in letters:
                temp_df = group[group['Text'] == letter].copy()  # 精確匹配
                if not temp_df.empty:
                    section_df = pd.concat([section_df, temp_df], ignore_index=True)
                else:
                    break  # 當找不到下一個字母時，停止搜尋
            
                    # 將同一個字母(應為兩個)的行依照座標左右分為Symbol(left)跟 Section(right)   
            group_section_df = section_df[['Text', 'CentreCoor']].copy().groupby('Text')
            processed_section_df = pd.DataFrame()
            for temp_name, temp_section_df in group_section_df:
                # check the length of the gruop is 2
                if len(temp_section_df) != 2:
                    print(f"字母{temp_name}的行數不為2")
                    continue
                temp_section_df['X'] = temp_section_df['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
                temp_section_df['Y'] = temp_section_df['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
                temp_section_df = temp_section_df.sort_values('X')
                temp_section_df.loc[temp_section_df.index[0], 'label'] = 'Symbol'
                temp_section_df.loc[temp_section_df.index[1], 'label'] = 'Section'
                processed_section_df = pd.concat([processed_section_df, temp_section_df], ignore_index=True)

            # 尋找 Section 的鋼筋編號
            processed_section_section_df = processed_section_df[processed_section_df['label'] == 'Section'][['X', 'Y', 'Text']].copy()
            processed_section_section_df = processed_section_section_df.sort_values('Y', ascending=False)

            group_sh_helper = df_sh_helper[df_sh_helper['FileName'] == name].copy()
            group_sh_helper['X'] = group_sh_helper['UpLeftPoint'].apply(parse_coordinate2).apply(lambda x: x[0])
            group_sh_helper['Y'] = group_sh_helper['UpLeftPoint'].apply(parse_coordinate2).apply(lambda y: y[1])
            group_sh_helper['section'] = pd.NA

            for i, row in processed_section_section_df.iterrows():
                section_y: float = row['Y']
                section_text: str = row['Text']
                # 如果 group_sh_helper 中的 section 非 Na 且 Y 大於 section_y 則將 section_text 賦值給 group_sh_helper 的 section
                group_sh_helper.loc[(group_sh_helper['section'].isna()) & (group_sh_helper['Y'] > section_y), 'section'] = section_text

            group_sh_helper = group_sh_helper.dropna(subset=['section'])

            # 計算同一個 section 的平均 X, Y 座標
            group_sh_helper = group_sh_helper.groupby('section').agg({'X': 'mean', 'Y': 'mean'}).reset_index()
            group_sh_helper['rebar_dia'] = None
            group_sh_helper['rebar_spac'] = None

            rebar_rows = group.dropna(subset=['Extracted_Rebar_diameter'])[['Extracted_Rebar_diameter', 'Extracted_Rebar_spacing', 'CentreCoor', 'Text']].copy()

            for i, row in group_sh_helper.iterrows():
                x, y = row['X'], row['Y']
                group_sh_helper.at[i, 'rebar_dia'] = sh_rebar_find_rebar_dia(x, y, rebar_rows)
                group_sh_helper.at[i, 'rebar_spac'] = sh_rebar_find_rebar_spac(x, y, rebar_rows)

            # print(group_sh_helper[['section', 'rebar_dia', 'rebar_spac']])

            # 將 group_sh_helper 的 rebar_dia, rebar_spac 依照 section 貼到 processed_section_df 的相應行
            processed_section_df['rebar_dia'] = None
            processed_section_df['rebar_spac'] = None
            for i, row in group_sh_helper.iterrows():
                section = row['section']
                rebar_dia = row['rebar_dia']
                rebar_spac = row['rebar_spac']
                processed_section_df.loc[processed_section_df['Text'] == section, 'rebar_dia'] = rebar_dia
                processed_section_df.loc[processed_section_df['Text'] == section, 'rebar_spac'] = rebar_spac
            


            # 獲取 EL 分布
            EL_rows = group.dropna(subset=['Extracted_EL']).copy().reset_index()
            EL_rows['X'] = EL_rows['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
            EL_rows['Y'] = EL_rows['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
            EL_rows = EL_rows.sort_values('X')
            EL_bottom: pd.DataFrame = EL_rows[EL_rows['Extracted_EL']==EL].loc[EL_rows[EL_rows['Extracted_EL']==EL]['X'].idxmin()]
            EL_bottom_x: float = EL_bottom['X']

            # 獲取 EL_rows 中與 EL_bottom 的 X 座標相差不超過 0.1 的行
            EL_rows = EL_rows[(EL_rows['X'] >= EL_bottom_x - 0.1) & (EL_rows['X'] <= EL_bottom_x + 0.1)]
            Deep_rows = EL_rows[['Extracted_EL', 'Text', 'X', 'Y']].sort_values('Y').copy().reset_index()
            # 如果非空打，將 GL 接到 Deep_rows 的最後一行
            if knockout_exists != True:
                GL_row: pd.DataFrame = group.dropna(subset=['Extracted_GL']).copy().reset_index()
                GL_row['X'] = GL_row['CentreCoor'].apply(parse_coordinate).apply(lambda x: x[0])
                GL_row['Y'] = GL_row['CentreCoor'].apply(parse_coordinate).apply(lambda y: y[1])
                GL_row = GL_row.loc[0, ['Text', 'Extracted_GL', 'X', 'Y']].to_frame().T
                GL_row.rename(columns={'Extracted_GL': 'Extracted_EL'}, inplace=True)
                Deep_rows = pd.concat([Deep_rows, GL_row], ignore_index=True)
            
            Deep_rows['Standardize_EL'] = Deep_rows['Extracted_EL'].apply(lambda x: abs(x - GL))

            Deep_rows['Start_depth'] = Deep_rows['Standardize_EL'].shift(-1)
            Deep_rows['End_depth'] = Deep_rows['Standardize_EL']

            Deep_rows['Start_y'] = Deep_rows['Y']
            Deep_rows['End_y'] = Deep_rows['Y'].shift(-1)

            Deep_rows = Deep_rows.dropna().reset_index(drop=True)

            Deep_rows['Sv_Dia'] = None
            Deep_rows['Sv_Spac'] = None

            # 按照順序將 rotated_rebar_rows 填入 Sv 欄位，若遇到不夠的 rebar 則用上一個 rebar 補充
            # 由大到小排序
            rotated_rebar_rows = rotated_rebar_rows.sort_values('Y', ascending=False)
            copy_time_count = len(Deep_rows) - len(rotated_rebar_rows)
            if copy_time_count > 0:
                additional_rows = pd.concat([rotated_rebar_rows.iloc[[0]]] * copy_time_count, ignore_index=True)
                rotated_rebar_rows_expanded = pd.concat([rotated_rebar_rows, additional_rows], ignore_index=True)
            else:
                rotated_rebar_rows_expanded = rotated_rebar_rows

            rotated_rebar_rows_expanded.reset_index(drop=True, inplace=True)
            Deep_rows['Sv_Dia'] = rotated_rebar_rows_expanded['Extracted_Rebar_diameter']
            Deep_rows['Sv_Spac'] = rotated_rebar_rows_expanded['Extracted_Rebar_spacing']

            Deep_rows['Sh_Dia'] = None
            Deep_rows['Sh_Spac'] = None

            # 根據 Y 值匹配，填入 Sh 欄位
            for i, row in Deep_rows.iterrows():
                matched_text = processed_section_df[(processed_section_df['Y'] >= row['Start_y']) & (processed_section_df['Y'] <= row['End_y']) & (processed_section_df['label'] == 'Symbol')]
                if not matched_text.empty:
                    # 去除重複的 rebar_dia 和 rebar_spac 值
                    unique_dia = ','.join(sorted(set(matched_text['rebar_dia'].astype(str))))
                    unique_spac = ','.join(sorted(set(matched_text['rebar_spac'].astype(str))))
                    
                    # 將唯一值賦值給 Deep_rows
                    Deep_rows.at[i, 'Sh_Dia'] = unique_dia
                    Deep_rows.at[i, 'Sh_Spac'] = unique_spac

            print(Deep_rows[['Start_depth', 'End_depth', 'Sv_Dia', 'Sv_Spac', 'Sh_Dia', 'Sh_Spac']])
            
            
            # 存儲 Sv 鋼筋
            for i, row in Deep_rows.iterrows():
                if row['Sh_Dia'] is not None:
                    Sh_value = f'D{row["Sh_Dia"]}@{row["Sh_Spac"]}'
                else:
                    Sh_value = '-'
                if row['Sv_Dia'] is not None:
                    Sv_value = f'D{row["Sv_Dia"]}@{row["Sv_Spac"]}'
                else:
                    Sv_value = '-'

                S_rebar[i] = {'Sv_Dia': row['Sv_Dia'],
                            'Sv_Spac': row['Sv_Spac'],
                            'Sv_value': Sv_value,
                            'Sh_Spac': row['Sh_Spac'],
                            'Sh_Dia': row['Sh_Dia'],
                            'Sh_value': Sh_value,
                            'Start_depth': round(row['Start_depth'], 2),
                            'End_depth': round(row['End_depth'],2)}

            # 獲取 num_
            type_data['S_rebar'] = S_rebar

            ''' 7.  萃取垂直鋼筋'''
            V_rebar = {}
            # 將 combined_helpers fileter by group name
            group_helpers = combined_helpers[combined_helpers['FileName'] == name].copy()

            # 對每個 helper 的 top_y 跟 down_y ，從 Extracted_EL 列中找到 y 最接近的 EL
                # 將 Extracted_EL 和 Extracted_GL 非 na 的行選出來
            EL_GL_rows  = group.dropna(subset=['Extracted_EL', 'Extracted_GL'], how='all')[['Extracted_EL', 'Extracted_GL', 'CentreCoor']].copy()
                # merge EL and GL
            EL_GL_rows['EL_GL'] = EL_GL_rows['Extracted_EL'].fillna(EL_GL_rows['Extracted_GL'])
                # 對每個 helper ，用 top_x, top_y  利用 find_nearest 找到最接近的 EL_GL (利用 EL_GL_rows 的 CentreCoor)
            group_helpers['top_value'] = group_helpers.apply(lambda x: v_rebar_find_el('CentreCoor', x['top_y'], EL_GL_rows), axis=1)
            group_helpers['down_value'] = group_helpers.apply(lambda x: v_rebar_find_el('CentreCoor', x['down_y'], EL_GL_rows), axis=1)

            # 確定每個 helper 屬於開挖側還是擋土側
            Ex_Re_rows = group[(group['Extracted_Side'] == True) | (group['Retained_Side'] == True)][['Extracted_Side', 'Retained_Side', 'CentreCoor', 'Text']].copy()
            group_helpers['Side'] = group_helpers.apply(lambda x: v_rebar_find_side(x['x'], x['y'], Ex_Re_rows), axis=1)

            # 確定每個 helper 的鋼筋直徑和間距
            rebar_rows = group.dropna(subset=['Extracted_Rebar_diameter'])[['Extracted_Rebar_diameter', 'Extracted_Rebar_spacing', 'CentreCoor', 'Text']].copy()
            group_helpers['Diameter'] = group_helpers.apply(lambda x: v_rebar_find_rebar_dia(x['x'], x['y'], rebar_rows), axis=1)
            group_helpers['Spacing'] = group_helpers.apply(lambda x: v_rebar_find_rebar_spac(x['x'], x['y'], rebar_rows), axis=1)

            # 計算每個 helper 的起始深度和結束深度
            group_helpers['start_depth'] = group_helpers.apply(lambda x: GL - x['top_value'], axis=1)
            group_helpers['end_depth'] = group_helpers.apply(lambda x: GL - x['down_value'], axis=1)
            # print(group_helpers[['y', 'Side', 'Diameter', 'Spacing', 'top_value', 'down_value', 'start_depth', 'end_depth']])

            # 將資料整理成字典
            for i in range(len(group_helpers)):
                V_rebar_str: str = f'D{group_helpers.iloc[i]["Diameter"]}@{group_helpers.iloc[i]["Spacing"]}'
                V_rebar[i] = {'Side': group_helpers.iloc[i]['Side'], 
                            'Value': V_rebar_str,
                            'Diameter': group_helpers.iloc[i]['Diameter'], 
                            'Spacing': group_helpers.iloc[i]['Spacing'], 
                            'Start_depth': round(group_helpers.iloc[i]['start_depth'],2), 
                            'End_depth': round(group_helpers.iloc[i]['end_depth'], 2)}
                
            type_data['V_rebar'] = V_rebar

            response_dic[name] = type_data

        self.output_path = self.call_ui(response_dic)

        self.save_to_xml(response_dic)

        os.remove(self.rebar_path)
        os.remove(self.vertical_path)
        os.remove(self.v_helper_path)
        os.remove(self.sh_helper_path)

        print("完成")

    def save_to_xml(self, response_dic):
        print("已將資料寫入xml檔案: ", self.output_path)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有rebars子節點，若無則創建，若有則刪除
        rebars = root.find(".//Drawing[@description='配筋圖']")
        if rebars is None:
            rebars = ET.SubElement(root, "Drawing", description="配筋圖")

        for filename, data_dic in response_dic.items():
            if check_attribute_exists(rebars, 'description', "TYPE "+str(data_dic['Type'])):
                continue

            WorkItemType = ET.SubElement(rebars, 'WorkItemType', description="TYPE "+str(data_dic['Type']))

            DiaphragmWall = ET.SubElement(WorkItemType, "DiaphragmWall", description="連續壁")
            
            Depth = ET.SubElement(DiaphragmWall, "Depth", description="設計深度")
            Depth_value = ET.SubElement(Depth, "Value", unit="m")
            Depth_value.text = str(data_dic['Depth'])

            Thickness = ET.SubElement(DiaphragmWall, "Thickness", description="厚度")
            Thickness_value = ET.SubElement(Thickness, "Value", unit="mm")
            Thickness_value.text = str(data_dic['Thickness'])

            RebarGroup = ET.SubElement(WorkItemType, "RebarGroup", description="鋼筋") 

            Protection = ET.SubElement(RebarGroup, "Protection", description="保護層")
            Protection_value = ET.SubElement(Protection, "Value", unit="mm")
            Protection_value.text = str(data_dic['Protection'])

            HorznRebar = ET.SubElement(RebarGroup, "HorznRebar", description="水平鋼筋")
            for side_info in data_dic['H_rebar']:
                Diameter = data_dic['H_rebar'][side_info]['Diameter']
                Spacing = data_dic['H_rebar'][side_info]['Spacing']
                rebar_type = f"D{Diameter}@{Spacing}"
                Rebar = ET.SubElement(HorznRebar, "Rebar", description="鋼筋資訊")
                Type = ET.SubElement(Rebar, "Type", description="水平筋設計")
                Type_value = ET.SubElement(Type, "Value", unit="mm")
                Type_value.text = rebar_type

            VertRebar = ET.SubElement(RebarGroup, "VertRebar", description="垂直筋")
            Retaining = ET.SubElement(VertRebar, "Retaining")
            Excavation = ET.SubElement(VertRebar, "Excavation")

            for i, rebar_info in data_dic['V_rebar'].items():
                if 'RETAINED' in rebar_info['Side'][1:-1].upper():
                    Rebar = ET.SubElement(Retaining, "Rebar", description="鋼筋資訊")

                    Type = ET.SubElement(Rebar, "Type", description="垂直筋設計")
                    Type_value = ET.SubElement(Type, "Value", unit="mm")
                    Type_value.text = rebar_info['Value']

                    StartDepth = ET.SubElement(Rebar, "StartDepth", description="開起深度")
                    StartDepth_value = ET.SubElement(StartDepth, "Value", unit="m")
                    StartDepth_value.text = str(rebar_info['Start_depth'])
                            # create a new EndDepth element
                    EndDepth = ET.SubElement(Rebar, "EndDepth", description="結束深度")
                    EndDepth_value = ET.SubElement(EndDepth, "Value", unit="m")
                    EndDepth_value.text = str(rebar_info['End_depth'])
                else:
                    Rebar = ET.SubElement(Excavation, "Rebar", description="鋼筋資訊")

                    Type = ET.SubElement(Rebar, "Type", description="垂直筋設計")
                    Type_value = ET.SubElement(Type, "Value", unit="mm")
                    Type_value.text = rebar_info['Value']

                    StartDepth = ET.SubElement(Rebar, "StartDepth", description="開起深度")
                    StartDepth_value = ET.SubElement(StartDepth, "Value", unit="m")
                    StartDepth_value.text = str(rebar_info['Start_depth'])
                            # create a new EndDepth element
                    EndDepth = ET.SubElement(Rebar, "EndDepth", description="結束深度")
                    EndDepth_value = ET.SubElement(EndDepth, "Value", unit="m")
                    EndDepth_value.text = str(rebar_info['End_depth'])

            ShearRebar = ET.SubElement(RebarGroup, "ShearRebar", description="剪力筋")
            for i, rebar_info in data_dic['S_rebar'].items():
                Rebar = ET.SubElement(ShearRebar, "Rebar", description="鋼筋資訊")
                Type = ET.SubElement(Rebar, "Type", description="剪力筋設計")
                Type_value = ET.SubElement(Type, "Value", unit="mm")

                if rebar_info['Sh_Spac'] == None:
                    Type_value.text = f"{rebar_info['Sv_Dia']}Sv {rebar_info['Sv_Spac']}"
                else:
                    Type_value.text = f"{rebar_info['Sh_Dia']}Sh {rebar_info['Sh_Spac']}Sv {rebar_info['Sv_Spac']}"

                StartDepth = ET.SubElement(Rebar, "StartDepth", description="開起深度")
                StartDepth_value = ET.SubElement(StartDepth, "Value", unit="m")
                StartDepth_value.text = str(rebar_info['Start_depth'])
                        # create a new EndDepth element
                EndDepth = ET.SubElement(Rebar, "EndDepth", description="結束深度")
                EndDepth_value = ET.SubElement(EndDepth, "Value", unit="m")
                EndDepth_value.text = str(rebar_info['End_depth'])
                
                
        # 寫入xml檔案，utf-8編碼
        tree.write(self.output_path, encoding="utf-8")
        return

    def call_ui(self, response_dic):

        dwgfname: list = list(response_dic.keys())
        first_dwgfilename: str = dwgfname[0]
        first_dwgfile_data: dict = response_dic[first_dwgfilename]

        def save_to_new_file():
            file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
            if file_path:
                window.selected_output_path = file_path
                window.quit()
                window.destroy()

        def save_to_existing_file():
            file_path = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
            if file_path:
                window.selected_output_path = file_path
                window.quit()
                window.destroy()

        def show_dwg_file(event):
            selected_file: str = select_dwg_combobox.get()
            selected_data: dict = response_dic[selected_file]

            # Modify Label
            wall_type_label.config(text="Wall Type = "+str(selected_data['Type']))
            wall_depth_label.config(text="Wall Depth = "+str(selected_data['Depth'])+" m")
            wall_real_depth_label.config(text="Real Depth = "+str(selected_data['Real_depth'])+" m")
            wall_empty_depth_label.config(text="Empty Depth = "+str(selected_data['Empty_depth'])+" m")
            wall_thickness_label.config(text="Wall Thickness = "+str(selected_data['Thickness'])+" mm")
            rebar_protection_label.config(text="Rebar Protection = "+str(selected_data['Protection'])+" mm")

            # Modify Listbox
            hori_rebar_listbox.delete(0, tk.END)
            table_data = "| {:^81s} |".format("Rebar Type")
            hori_rebar_listbox.insert(tk.END, table_data)
            hori_rebar_dict: dict = selected_data['H_rebar']
            for side_info in hori_rebar_dict:
                Diameter: int = hori_rebar_dict[side_info]['Diameter']
                Spacing: int = hori_rebar_dict[side_info]['Spacing']
                rebar: str = f"{side_info} - D{Diameter}@{Spacing}"
                table_data = "| {:^81s} |".format(str(rebar))
                hori_rebar_listbox.insert(tk.END, table_data)
            
            vert_rebar_listbox.delete(0, tk.END)
            table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format("Rebar Type", "Rebar Side", "Start Depth (m)", "End Depth (m)")
            vert_rebar_listbox.insert(tk.END, table_data)
            vert_rebar_dict: dict = selected_data['V_rebar']
            for i in vert_rebar_dict:
                rebar_type: str = vert_rebar_dict[i]['Value']
                rebar_side: str = vert_rebar_dict[i]['Side']
                rebar_start_depth: str = str(vert_rebar_dict[i]['Start_depth'])
                rebar_end_depth: str = str(vert_rebar_dict[i]['End_depth'])
                table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format(rebar_type, rebar_side, rebar_start_depth, rebar_end_depth)
                vert_rebar_listbox.insert(tk.END, table_data)

            shear_rebar_listbox.delete(0, tk.END)
            table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format("Rebar Type (Hor.)","Rebar Type (Vert.)", "Start Depth (m)", "End Depth (m)")
            shear_rebar_listbox.insert(tk.END, table_data)
            shear_rebar_dict: dict = selected_data['S_rebar']
            for i in shear_rebar_dict:
                rebar_type_hor: str = shear_rebar_dict[i]['Sh_value']
                rebar_type_vert: str = shear_rebar_dict[i]['Sv_value']
                rebar_start_depth: str = str(shear_rebar_dict[i]['Start_depth'])
                rebar_end_depth: str = str(shear_rebar_dict[i]['End_depth'])
                table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format(rebar_type_hor, rebar_type_vert, rebar_start_depth, rebar_end_depth)
                shear_rebar_listbox.insert(tk.END, table_data)

        window = tk.Tk()
        window.title("Reading Results")
        window.selected_output_path = None

        menu_frame = tk.Frame(window)
        menu_frame.pack(side=tk.TOP, padx=(10,20), pady=20)

        # Create a frame for select dwg
        select_dwg_frame = tk.Frame(menu_frame)
        select_dwg_frame.pack()

        # Create a label for displaying "Select DWG File"
        select_dwg_label = tk.Label(select_dwg_frame, text="Select DWG :", font=("Arial", 14))
        select_dwg_label.pack(side=tk.LEFT,pady=0)

        # Create a combobox (dropdown menu) widget
        select_dwg_combobox = ttk.Combobox(select_dwg_frame, values=[filename for f,filename in enumerate(dwgfname)])
        select_dwg_combobox.bind("<<ComboboxSelected>>", show_dwg_file)
        select_dwg_combobox.pack(side=tk.LEFT,pady=0, padx=(0, 0))

        # Create a label for displaying "Plan/Elevation Drawing"
        drawing_type_label = tk.Label(menu_frame, text="Drawing Type : Rebar Drawings", font=("Arial", 14))
        drawing_type_label.pack(pady=0)

        # Create frame for wall type menu
        wall_type_frame = tk.Frame(menu_frame)
        wall_type_frame.pack()

        # Create a label for displaying "Wall Type"
        wall_type_label = tk.Label(wall_type_frame, text="Wall Type = "+str(first_dwgfile_data['Type']), font=("Arial", 14), fg="blue")
        wall_type_label.pack(side=tk.LEFT,pady=0)

        # Create a label for displaying "Wall Depth"
        wall_depth_label = tk.Label(menu_frame, text="Wall Depth = "+str(first_dwgfile_data['Depth'])+" m", font=("Arial", 14), fg="blue")
        wall_depth_label.pack(pady=0)

        # Create a label for displaying "Real Depth"
        wall_real_depth_label = tk.Label(menu_frame, text="Real Depth = "+str(first_dwgfile_data['Real_depth'])+" m", font=("Arial", 14), fg="blue")
        wall_real_depth_label.pack(pady=0)

        # Create a label for displaying "Empty Depth"
        wall_empty_depth_label = tk.Label(menu_frame, text="Empty Depth = "+str(first_dwgfile_data['Empty_depth'])+" m", font=("Arial", 14), fg="blue")
        wall_empty_depth_label.pack(pady=0)

        # Create a label for displaying "Wall Thickness"
        wall_thickness_label = tk.Label(menu_frame, text="Wall Thickness = "+str(first_dwgfile_data['Thickness'])+" m", font=("Arial", 14), fg="blue")
        wall_thickness_label.pack(pady=0)

        # Create a label for displaying "Rebar Protection"
        rebar_protection_label = tk.Label(menu_frame, text="Rebar Protection = "+str(first_dwgfile_data['Protection'])+" mm", font=("Arial", 14), fg="blue")
        rebar_protection_label.pack(pady=0)

        # Create a label for displaying "Horizontal Rebar "
        hori_rebar_label = tk.Label(menu_frame, text="Horizontal Rebar", font=("Arial", 14), fg="blue")
        hori_rebar_label.pack(pady=0)
        hori_rebar_listbox = tk.Listbox(menu_frame, font=('Courier New', 12), width=85, height=5,selectmode="single", activestyle="none")
        hori_rebar_listbox.pack(pady=5)

        # Create a label for displaying "Vertical Rebar "
        vert_rebar_label = tk.Label(menu_frame, text="Vertical Rebar", font=("Arial", 14), fg="blue")
        vert_rebar_label.pack(pady=0)
        vert_rebar_listbox = tk.Listbox(menu_frame, font=('Courier New', 12), width=85, height=5,selectmode="single", activestyle="none")
        vert_rebar_listbox.pack(pady=5)

        # Create a label for displaying "Shear Rebar "
        shear_rebar_label = tk.Label(menu_frame, text="Shear Rebar", font=("Arial", 14), fg="blue")
        shear_rebar_label.pack(pady=0)
        shear_rebar_listbox = tk.Listbox(menu_frame, font=('Courier New', 12), width=85, height=5,selectmode="single", activestyle="none")
        shear_rebar_listbox.pack(pady=5)

        # Create a button to select XML file directory
        new_file_button = tk.Button(menu_frame, text="存入新檔", command=save_to_new_file)
        existing_file_button = tk.Button(menu_frame, text="寫入舊檔", command=save_to_existing_file)
        new_file_button.pack(pady=5, padx=(0, 0))
        existing_file_button.pack(pady=5, padx=(0, 0))

        # Show the first dwg
        select_dwg_combobox.current(0)
        select_dwg_combobox.event_generate("<<ComboboxSelected>>")

        # Run the Tkinter event loop
        window.mainloop()

        return window.selected_output_path