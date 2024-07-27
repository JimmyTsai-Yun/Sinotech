from lib.utils import *
import pandas as pd
import numpy as np
import re
import csv
import keyboard
import tkinter as tk
from tkinter import filedialog
import os

class Base_structure():
    def __init__(self, **kwargs):
        self.pdf_path = kwargs.get("pdf_path")
        self.csv_path = kwargs.get("csv_path")
        self.output_path = kwargs.get("output_path")
        self.use_azure = kwargs.get("use_azure")
        if self.use_azure:
            self.client = construct_GPT4()

    def custom_csv_parser(self, file_path, encoding='ISO-8859-1'):
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
    
    def parse_coordinate(self, coord_str):
        # 使用正則表達式提取坐標值
        match = re.match(r'\(([\d.]+)\s+([\d.]+)\s+([\d.]+)\)', coord_str)
        if match:
            return [float(match.group(1)), float(match.group(2)), float(match.group(3))]
        else:
            raise ValueError(f"無法解析坐標: {coord_str}")
        
    def find_nearest_two(self, target_column: str, candidate_columns: str, df: pd.DataFrame):

        target_rows = df[df[target_column]].iloc[0]
        candidate_rows = df[df[candidate_columns].notna()]

        target_coords = np.array(self.parse_coordinate(target_rows['CentreCoor']))
        candidate_coords = np.array([self.parse_coordinate(coord) for coord in candidate_rows['CentreCoor']])

        # 計算 x 坐標差異和總距離
        x_diff = candidate_coords[:, 0] - target_coords[0]
        distances = np.sqrt(np.sum((candidate_coords[:, :2] - target_coords[:2])**2, axis=1))

        # 只考慮 x 坐標大於的點
        valid_indices = x_diff > 0
        valid_distances = distances[valid_indices]
        valid_candidate_rows = candidate_rows[valid_indices]

        # 找出最近的兩個點
        nearest_indices = np.argsort(valid_distances)[:2]

        result = []
        for idx in nearest_indices:
            nearest_candidate_row = valid_candidate_rows.iloc[idx]
            result.append(nearest_candidate_row[candidate_columns])

        return result
    
    def run():
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


class Diaphragm_structure(Base_structure):
    """Derived class for specific operations on Diaphragm structure drawings."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def call_ui(self, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2, protection1, protection2):
        def save_to_new_file():
            file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
            if file_path:
                self.save_xml_file(file_path, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2, protection1, protection2)
                self.window.quit()
                self.window.destroy()

        def save_to_existing_file():
            file_path = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
            if file_path:
                self.save_xml_file(file_path, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2, protection1, protection2)
                self.window.quit()
                self.window.destroy()

        self.window = tk.Tk()
        self.window.title("Reading Results")

        # Create a label for displaying "Plan/Elevation Drawing"
        drawing_type_label = tk.Label(self.window, text="Drawing Type : Structural Descriptions", font=("Arial", 14))
        drawing_type_label.pack(pady=(10,0))

        # Create labels for the variables with unit
        label_frame = tk.Frame(self.window)
        label_frame.pack(side=tk.TOP,padx=(30,30), pady=(0,5))
        wall_strength1_label = tk.Label(label_frame, text="wall_strength1", font=("Arial", 14), fg="blue")
        wall_strength2_label = tk.Label(label_frame, text="wall_strength2", font=("Arial", 14), fg="blue")
        rebar_strength1_label = tk.Label(label_frame, text="rebar_strength1", font=("Arial", 14), fg="blue")
        rebar_strength2_label = tk.Label(label_frame, text="rebar_strength2", font=("Arial", 14), fg="blue")
        rebar_protection_exposed_label = tk.Label(label_frame, text="rebar_protection_exposed", font=("Arial", 14), fg="blue")
        rebar_protection_diaphragm_label = tk.Label(label_frame, text="rebar_protection_diaphragm", font=("Arial", 14), fg="blue")
        
        # Create labels for the ":" character
        colon_label1 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label2 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label3 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label4 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label5 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label6 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")

        # Create labels for the variable values with unit
        wall_strength1_value = tk.Label(label_frame, text=str(wall_strength1) + " kgf/cm2", font=("Arial", 14), fg="blue")
        wall_strength2_value = tk.Label(label_frame, text=str(wall_strength2) + " kgf/cm2", font=("Arial", 14), fg="blue")
        rebar_strength1_value = tk.Label(label_frame, text=str(rebar_strength1) + " kgf/cm2", font=("Arial", 14), fg="blue")
        rebar_strength2_value = tk.Label(label_frame, text=str(rebar_strength2) + " kgf/cm2", font=("Arial", 14), fg="blue")
        rebar_protection_exposed_value = tk.Label(label_frame, text=str(protection1) + " mm", font=("Arial", 14), fg="blue")
        rebar_protection_diaphragm_value = tk.Label(label_frame, text=str(protection2) + " mm", font=("Arial", 14), fg="blue")
       
        # Place the labels in a grid
        wall_strength1_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label1.grid(row=0, column=1, padx=2, pady=5)
        wall_strength1_value.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

        wall_strength2_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label2.grid(row=1, column=1, padx=2, pady=5)
        wall_strength2_value.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)

        rebar_strength1_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label3.grid(row=2, column=1, padx=2, pady=5)
        rebar_strength1_value.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)

        rebar_strength2_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label4.grid(row=3, column=1, padx=2, pady=5)
        rebar_strength2_value.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)

        rebar_protection_exposed_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label5.grid(row=4, column=1, padx=2, pady=5)
        rebar_protection_exposed_value.grid(row=4, column=2, padx=10, pady=5, sticky=tk.W)

        rebar_protection_diaphragm_label.grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label6.grid(row=5, column=1, padx=2, pady=5)
        rebar_protection_diaphragm_value.grid(row=5, column=2, padx=10, pady=5, sticky=tk.W)

        # Create button frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=(10,15))
        # Create buttons
        new_file_button = tk.Button(button_frame, text="存入新檔", command=save_to_new_file)
        existing_file_button = tk.Button(button_frame, text="寫入舊檔", command=save_to_existing_file)
        # Place buttons in the frame
        new_file_button.pack(side=tk.RIGHT, padx=5)
        existing_file_button.pack(side=tk.RIGHT, padx=5)

        # Run the Tkinter event loop
        self.window.mainloop()

    def save_xml_file(self, file_path, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2, protection1, protection2):
        tree, root = create_or_read_xml(file_path)

        # 檢查是否有plans子節點，若無則創建，若有則刪除
        structure = root.find(".//Drawing[@description='結構一般説明']")
        if structure is None:
            structure = ET.SubElement(root, "Drawing", description='結構一般説明')
        else:
            # 移除plans的所有子節點
            for child in list(structure):
                structure.remove(child)

        # Add Concrete info
        concrete = ET.SubElement(structure, "Concrete", Description="混凝土")
        for i, strength in enumerate([wall_strength1, wall_strength2], 1):
            strength_elem = ET.SubElement(concrete, f"Strength{i}", Description=f"强度{i}")
            ET.SubElement(strength_elem, "Value", unit="kgf/cm2").text = str(strength)

        # Add Rebar info
        rebar = ET.SubElement(structure, "Rebar", Description="鋼筋")
        for i, strength in enumerate([rebar_strength1, rebar_strength2], 1):
            strength_elem = ET.SubElement(rebar, f"Strength{i}", Description=f"强度{i}")
            ET.SubElement(strength_elem, "Value", unit="kgf/cm2").text = str(strength)

        # Add Protection info
        protection = ET.SubElement(structure, "Protection", Description="保護層")
        ET.SubElement(ET.SubElement(protection, "Exposed", Description="暴露部分"), 
                    "Value", unit="mm").text = str(protection1)
        ET.SubElement(ET.SubElement(protection, "Diaphragm", Description="雙面"), 
                    "Value", unit="mm").text = str(protection2)
        
        # 將xml檔案寫入指定路徑
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

        return

    def run(self):
        fy_pattern = r'^fy\s+(\d+)\s+kgf/cm'
        mm_pattern = r'^(\d+)\s+mm'
        fc_pattern = r'^f\'c ¡Ù (\d+) kgf/cm'
        protection_pattern2 = r'DIAPHRAGM\s+WALLS\s+\(BOTH\s+FACES\)'
        protection_pattern1 = r'CONCRETE\s+CAST\s+AGAINST\s+AND\s+PERMANENTLY\s+EXPOSED\s+TO\s+WATER,\s+SOIL,\s+BLINDING'
        rebar_strength_pattern2 = r'REINFORCEMENT\s+OF\s+10\s+mm\s+OR\s+SMALLER\s+IN\s+DIAMETER\s+SHALL\s+CONFORM\s+TO\s+CNS\s+560'
        rebar_strength_pattern1 = r'REINFORCEMENT\s+OF\s+13\s+mm\s+OR\s+LARGER\s+IN\s+DIAMETER\s+SHALL\s+CONFORM\s+TO\s+CNS\s+560'
        concrete_strength_pattern = r'^DIAPHRAGM\s+WALLS$'

        # 使用自定義解析器讀取文件
        rows = self.custom_csv_parser(self.csv_path)

        # 定義標題列
        columns = ["FileName", "EntityName", "ObjectType", "RotationAngle", "CentreCoor", "Height", "Width", "Text"]

        # 將結果轉換為 DataFrame
        df = pd.DataFrame(rows[1:], columns=columns)

        # 創建一個新的列來存儲提取的數字
        df['fy_number'] = df['Text'].str.extract(fy_pattern)
        df['mm_number'] = df['Text'].str.extract(mm_pattern)
        df['fc_number'] = df['Text'].str.extract(fc_pattern)
        df['rebar_protection2'] = df['Text'].str.contains(protection_pattern2, regex=True)
        df['rebar_protection1'] = df['Text'].str.contains(protection_pattern1, regex=True)
        df['rebar_strength1'] = df['Text'].str.contains(rebar_strength_pattern1, regex=True)
        df['rebar_strength2'] = df['Text'].str.contains(rebar_strength_pattern2, regex=True)
        df['concrete_strength'] = df['Text'].str.contains(concrete_strength_pattern, regex=True)

        # 如果您想將提取的數字轉換為整數
        df['fy_number'] = df['fy_number'].astype(float)
        df['mm_number'] = df['mm_number'].astype(float)
        df['fc_number'] = df['fc_number'].astype(float)

        # 找到 rebar_protection1 最近的兩個 mm_number
        protection1 = self.find_nearest_two('rebar_protection1', 'mm_number', df)
        print(f'The protection1 :{protection1[0]}')

        # 找到 rebar_protection2 最近的兩個 mm_number
        protection2 = self.find_nearest_two('rebar_protection2', 'mm_number', df)
        print(f'The protection2 :{protection2[0]}')

        # 找到 rebar_strength1 最近的兩個 fy_number
        rebar_strength1 = self.find_nearest_two('rebar_strength1', 'fy_number', df)
        print(f'The rebar_strength1 :{rebar_strength1[0]}')

        # 找到 rebar_strength2 最近的兩個 fy_number
        rebar_strength2 = self.find_nearest_two('rebar_strength2', 'fy_number', df)
        print(f'The rebar_strength2 :{rebar_strength2[0]}')

        # 找到 concrete_strength 最近的兩個 fc_number
        concrete_strength = self.find_nearest_two('concrete_strength', 'fc_number', df)
        print(f'The concrete_strength :{concrete_strength}')

        self.call_ui(concrete_strength[0], concrete_strength[1], rebar_strength1[0], rebar_strength2[0], protection1[0], protection2[0])

        os.remove(self.csv_path)

        return
    
class BoredPile_structure(Base_structure):
    """Derived class for specific operations on BoredPile structure drawings."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def call_ui(self, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2):
        def save_to_new_file():
            file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
            if file_path:
                self.save_xml_file(file_path, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2)
                self.window.quit()
                self.window.destroy()

        def save_to_existing_file():
            file_path = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
            if file_path:
                self.save_xml_file(file_path, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2)
                self.window.quit()
                self.window.destroy()

        self.window = tk.Tk()
        self.window.title("Reading Results")

        # Create a label for displaying "Plan/Elevation Drawing"
        drawing_type_label = tk.Label(self.window, text="Drawing Type : Structural Descriptions", font=("Arial", 14))
        drawing_type_label.pack(pady=(10,0))

        # Create labels for the variables with unit
        label_frame = tk.Frame(self.window)
        label_frame.pack(side=tk.TOP,padx=(30,30), pady=(0,5))
        wall_strength1_label = tk.Label(label_frame, text="wall_strength1", font=("Arial", 14), fg="blue")
        wall_strength2_label = tk.Label(label_frame, text="wall_strength2", font=("Arial", 14), fg="blue")
        rebar_strength1_label = tk.Label(label_frame, text="rebar_strength1", font=("Arial", 14), fg="blue")
        rebar_strength2_label = tk.Label(label_frame, text="rebar_strength2", font=("Arial", 14), fg="blue")
        
        # Create labels for the ":" character
        colon_label1 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label2 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label3 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")
        colon_label4 = tk.Label(label_frame, text="=", font=("Arial", 14), fg="blue")

        # Create labels for the variable values with unit
        wall_strength1_value = tk.Label(label_frame, text=str(wall_strength1) + " kgf/cm2", font=("Arial", 14), fg="blue")
        wall_strength2_value = tk.Label(label_frame, text=str(wall_strength2) + " kgf/cm2", font=("Arial", 14), fg="blue")
        rebar_strength1_value = tk.Label(label_frame, text=str(rebar_strength1) + " kgf/cm2", font=("Arial", 14), fg="blue")
        rebar_strength2_value = tk.Label(label_frame, text=str(rebar_strength2) + " kgf/cm2", font=("Arial", 14), fg="blue")
       
        # Place the labels in a grid
        wall_strength1_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label1.grid(row=0, column=1, padx=2, pady=5)
        wall_strength1_value.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

        wall_strength2_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label2.grid(row=1, column=1, padx=2, pady=5)
        wall_strength2_value.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)

        rebar_strength1_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label3.grid(row=2, column=1, padx=2, pady=5)
        rebar_strength1_value.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)

        rebar_strength2_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        colon_label4.grid(row=3, column=1, padx=2, pady=5)
        rebar_strength2_value.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)

        # Create button frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=(10,15))
        # Create buttons
        new_file_button = tk.Button(button_frame, text="存入新檔", command=save_to_new_file)
        existing_file_button = tk.Button(button_frame, text="寫入舊檔", command=save_to_existing_file)
        # Place buttons in the frame
        new_file_button.pack(side=tk.RIGHT, padx=5)
        existing_file_button.pack(side=tk.RIGHT, padx=5)

        # Run the Tkinter event loop
        self.window.mainloop()

    def save_xml_file(self, file_path, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2):
        tree, root = create_or_read_xml(file_path)

        # 檢查是否有plans子節點，若無則創建，若有則刪除
        structure = root.find(".//Drawing[@description='結構一般説明']")
        if structure is None:
            structure = ET.SubElement(root, "Drawing", description='結構一般説明')
        else:
            # 移除plans的所有子節點
            for child in list(structure):
                structure.remove(child)

        # Add Concrete info
        concrete = ET.SubElement(structure, "Concrete", Description="混凝土")
        for i, strength in enumerate([wall_strength1, wall_strength2], 1):
            strength_elem = ET.SubElement(concrete, f"Strength{i}", Description=f"强度{i}")
            ET.SubElement(strength_elem, "Value", unit="kgf/cm2").text = str(strength)

        # Add Rebar info
        rebar = ET.SubElement(structure, "Rebar", Description="鋼筋")
        for i, strength in enumerate([rebar_strength1, rebar_strength2], 1):
            strength_elem = ET.SubElement(rebar, f"Strength{i}", Description=f"强度{i}")
            ET.SubElement(strength_elem, "Value", unit="kgf/cm2").text = str(strength)
        
        # 將xml檔案寫入指定路徑
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

        return

    def run(self):
        fy_pattern = r'^fy\s+(\d+)\s+kgf/cm'
        fc_pattern = r'^f\'c ¡Ù (\d+) kgf/cm'

        rebar_strength_pattern2 = r'REINFORCEMENT\s+OF\s+10\s+mm\s+OR\s+SMALLER\s+IN\s+DIAMETER\s+SHALL\s+CONFORM\s+TO\s+CNS\s+560'
        rebar_strength_pattern1 = r'REINFORCEMENT\s+OF\s+13\s+mm\s+OR\s+LARGER\s+IN\s+DIAMETER\s+SHALL\s+CONFORM\s+TO\s+CNS\s+560'
        concrete_strength_pattern = r'^DIAPHRAGM\s+WALLS$'

        # 使用自定義解析器讀取文件
        rows = self.custom_csv_parser(self.csv_path)

        # 定義標題列
        columns = ["FileName", "EntityName", "ObjectType", "RotationAngle", "CentreCoor", "Height", "Width", "Text"]

        # 將結果轉換為 DataFrame
        df = pd.DataFrame(rows[1:], columns=columns)

        # 創建一個新的列來存儲提取的數字
        df['fy_number'] = df['Text'].str.extract(fy_pattern)
        df['fc_number'] = df['Text'].str.extract(fc_pattern)
        df['rebar_strength1'] = df['Text'].str.contains(rebar_strength_pattern1, regex=True)
        df['rebar_strength2'] = df['Text'].str.contains(rebar_strength_pattern2, regex=True)
        df['concrete_strength'] = df['Text'].str.contains(concrete_strength_pattern, regex=True)

        # 如果您想將提取的數字轉換為整數
        df['fy_number'] = df['fy_number'].astype(float)
        df['fc_number'] = df['fc_number'].astype(float)

        # 找到 rebar_strength1 最近的兩個 fy_number
        rebar_strength1 = self.find_nearest_two('rebar_strength1', 'fy_number', df)
        print(f'The rebar_strength1 :{rebar_strength1[0]}')

        # 找到 rebar_strength2 最近的兩個 fy_number
        rebar_strength2 = self.find_nearest_two('rebar_strength2', 'fy_number', df)
        print(f'The rebar_strength2 :{rebar_strength2[0]}')

        # 找到 concrete_strength 最近的兩個 fc_number
        concrete_strength = self.find_nearest_two('concrete_strength', 'fc_number', df)
        print(f'The concrete_strength :{concrete_strength}')

        self.call_ui(concrete_strength[0], concrete_strength[1], rebar_strength1[0], rebar_strength2[0])

        os.remove(self.csv_path)
        
        return