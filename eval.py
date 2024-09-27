from lib.utils import *
import keyboard
import re
import pandas as pd
import numpy as np
import os
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk

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

    def run(self):
         # 檢查 CSV 檔案是否存在
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"The specified file does not exist: {self.csv_path}")

        # 使用自訂的 CSV 解析器
        try:
            rows = custom_csv_parser(self.csv_path)
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {e}")

        # 檢查解析結果是否有內容
        if not rows or len(rows) < 2:
            raise ValueError(f"The parsed data is empty or missing rows: {rows}")

        # 定義資料框的欄位
        columns: list = ["FileName", "EntityName", "ObjectType", "RotationAngle", "CentreCoor", "Height", "Width", "Text"]

        # 將結果轉換為 DataFrame，並進行基本檢查
        try:
            df: pd.DataFrame = pd.DataFrame(rows[1:], columns=columns)
        except ValueError as ve:
            raise ValueError(f"DataFrame creation failed: {ve}")

        # 檢查 DataFrame 是否為空
        if df.empty:
            raise ValueError("DataFrame is empty after creation.")

        # 對 FileName 進行群組化處理
        grouped = df.groupby('FileName')

        # 初始化集合和字典
        sheet_pile_text: set = set()  # 未經處理的鋼板樁文字
        sheet_pile_text_dict: dict = {}  # 經過處理的鋼板樁文字

        # 正則表達式 pattern 檢查
        pattern: str = r"(\S+)\s+SHEET\s+PILE\s+\(L=(\d+)m\)"

        # 對每個群組進行處理
        for name, group in grouped:
            print(f'Processing File Name: {name}')
            try:
                # 使用正則表達式進行文字提取
                try:
                    extracted_values = group['Text'].str.extract(pattern).values
                    group['Type_name'], group['Length'] = zip(*extracted_values)
                except ValueError as ve:
                    raise ValueError(f"Error extracting text with pattern in group {name}: {ve}")
                except Exception as re:
                    raise RuntimeError(f"Unexpected error during regex extraction in group {name}: {re}")

                # 轉換長度為數值型別
                try:
                    group['Length'] = pd.to_numeric(group['Length'], errors='coerce')
                    group['Length'] = group['Length'].astype('Int64')
                except ValueError as ve:
                    raise ValueError(f"Error converting Length to numeric in group {name}: {ve}")

                # 處理含有 Type_name 和 Length 的有效行
                try:
                    sheet_pile_rows: pd.DataFrame = group.dropna(subset=['Type_name', 'Length']).copy()
                except KeyError as ke:
                    raise KeyError(f"KeyError in filtering non-null rows in group {name}: {ke}")

                # 組合 Type_name 和 Length 為 Full_name
                try:
                    sheet_pile_rows['Full_name'] = sheet_pile_rows['Type_name'] + ' ' + sheet_pile_rows['Length'].astype(str) + 'm'
                    sheet_pile_text.update(sheet_pile_rows['Full_name'])
                except Exception as e:
                    raise RuntimeError(f"Error updating sheet_pile_text set in group {name}: {e}")

            except KeyError as ke:
                print(f"KeyError encountered: {ke}")
            except ValueError as ve:
                print(f"ValueError encountered: {ve}")
            except RuntimeError as re:
                print(f"RuntimeError encountered: {re}")
            except Exception as e:
                print(f"An unexpected error occurred while processing group {name}: {e}")

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
        rebars = root.find(".//Drawing[@description='立面圖']")
        if rebars is None:
            rebars = ET.SubElement(root, "Drawing", description="立面圖")

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


class Diaphragm_eval(Base_eval):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def run(self):
        
        def calculate_distance(x1, y1, x2, y2):
            return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        # initialize the dataframe
        df:pd.DataFrame = pd.read_csv(self.csv_path, delimiter=',')
        # drop the last column
        df = df.iloc[:, :-1]

        thickness_results = []
        height_results = []
        # Group the data by 'Layer' and 'ID' to find continuous walls
        grouped_data = df.groupby(['Layer', 'ID'])

        for (layer, wall_id), group in grouped_data:
            # Keep the points in the original order (no sorting)
            group_original = group.reset_index(drop=True)
            
            # Check if there are more than 4 points (indicating a duplicate)
            if len(group_original) > 4:
                # Remove the last point (assumed to be a duplicate of the first point)
                group_original = group_original.iloc[:-1]

            # Ensure we still have exactly 4 points to form the boundary of the wall
            if len(group_original) == 4:
                # Extract the first four points (X, Y)
                x_coords = group_original['X'].values
                y_coords = group_original['Y'].values
                
                # Calculate distances between consecutive points
                edge1 = calculate_distance(x_coords[0], y_coords[0], x_coords[1], y_coords[1])
                edge2 = calculate_distance(x_coords[1], y_coords[1], x_coords[2], y_coords[2])
                edge3 = calculate_distance(x_coords[2], y_coords[2], x_coords[3], y_coords[3])
                edge4 = calculate_distance(x_coords[3], y_coords[3], x_coords[0], y_coords[0])
                
                # Get the smallest edge as the wall thickness
                thickness = min(edge1, edge2, edge3, edge4)
                thickness = round(thickness, 3)
                
                # Get the largest edge as the wall height
                height = max(edge1, edge2, edge3, edge4)
                height = round(height, 3)

                print(f"Layer: {layer}, ID: {wall_id}, Thickness: {thickness}, Height: {height}")
                
                # Append the result for this wall
                thickness_results.append({'Layer': layer, 'ID': wall_id, 'Thickness': thickness})
                height_results.append({'Layer': layer, 'ID': wall_id, 'Height': height})

        # Convert results to DataFrames
        thickness_df = pd.DataFrame(thickness_results)
        height_df = pd.DataFrame(height_results)

        # Final thickness and height results
        final_thickness_results = []
        final_height_results = []

        def handle_inconsistent_layers(layer, values, value_type):
            """Display a Tkinter window for the user to select the correct thickness or height"""
            root = tk.Tk()
            root.title(f"Select correct {value_type} - {layer}")

            label = tk.Label(root, text=f"Layer {layer} has inconsistent {value_type}: {values}")
            label.pack(pady=10)

            selected_value = tk.DoubleVar()

            for value in values:
                cleaned_value = float(str(value).replace('[','').replace(']',''))
                ttk.Radiobutton(root, text=str(cleaned_value), variable=selected_value, value=cleaned_value).pack(anchor='w')

            def confirm_selection():
                if value_type == 'thickness':
                    final_thickness_results.append({'Layer': layer, 'Thickness': selected_value.get()})
                elif value_type == 'height':
                    final_height_results.append({'Layer': layer, 'Height': selected_value.get()})
                root.destroy()

            confirm_button = ttk.Button(root, text="Confirm", command=confirm_selection)
            confirm_button.pack(pady=10)

            root.mainloop()

        # Check thickness consistency
        grouped_by_layer_thickness = thickness_df.groupby('Layer')
        for layer, group in grouped_by_layer_thickness:
            unique_thicknesses = group['Thickness'].unique()
            if np.all(np.isclose(unique_thicknesses, unique_thicknesses[0])):
                final_thickness_results.append({'Layer': layer, 'Thickness': group['Thickness'].iloc[0]})
            else:
                handle_inconsistent_layers(layer, unique_thicknesses, 'thickness')

        # Check height consistency
        grouped_by_layer_height = height_df.groupby('Layer')
        for layer, group in grouped_by_layer_height:
            unique_heights = group['Height'].unique()
            if np.all(np.isclose(unique_heights, unique_heights[0])):
                final_height_results.append({'Layer': layer, 'Height': group['Height'].iloc[0]})
            else:
                handle_inconsistent_layers(layer, unique_heights, 'height')

        # Convert the final results into DataFrames for display
        final_thickness_df = pd.DataFrame(final_thickness_results)
        final_height_df = pd.DataFrame(final_height_results)

        # turn the dataframe into a dictionary
        result_dir = {}
        for index, row in final_thickness_df.iterrows():
            result_dir[row['Layer']] = {'Thickness': row['Thickness']}   
        for index, row in final_height_df.iterrows():
            result_dir[row['Layer']]['Height'] = row['Height'] 

        # gui
        self.output_path = create_gui(result_dir, "Diaphragm Wall Eval")

        # write the response to xml file
        self.save_to_xml(result_dir)

        # remove the csv
        os.remove(self.csv_path)

    def save_to_xml(self, response_dic):
        print("已將資料寫入xml檔案: ", self.output_path)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有evals子節點，若無則創建，若有則刪除
        evals = root.find(".//Drawing[@description='立面圖']")
        if evals is None:
            evals = ET.SubElement(root, "Drawing", description="立面圖")

        # 將response_list寫入配筋圖子節點
        for wall_type, wall_info in response_dic.items():
            wall_thickness = wall_info['Thickness']
            wall_height = wall_info['Height']
            if check_attribute_exists(evals, 'description', "TYPE "+str(wall_type[5:])):
                continue
            else:
                WorkItemType = ET.SubElement(evals, 'WorkItemType', description="TYPE "+str(wall_type[5:]))
                DiaphragmWall = ET.SubElement(WorkItemType, "DiaphragmWall", description="連續壁")

                Thickness = ET.SubElement(DiaphragmWall, 'Thickness', description="厚度")
                Thickness_value = ET.SubElement(Thickness, 'Value', unit="m")
                Thickness_value.text = str(wall_thickness)

                Depth = ET.SubElement(DiaphragmWall, 'Depth', description="設計深度")
                Depth_value = ET.SubElement(Depth, 'Value', unit="m")
                Depth_value.text = str(wall_height)
        
        # 寫入xml檔案，utf-8編碼
        tree.write(self.output_path, encoding="utf-8")
    
