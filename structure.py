from lib.utils import *
from lib.structure_utils import get_the_num, check_is_right
import keyboard
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os

class Base_structure():
    def __init__(self, **kwargs):
        self.pdf_path = kwargs.get("pdf_path")
        self.csv_path = kwargs.get("csv_path")
        self.output_path = kwargs.get("output_path")
        self.use_azure = kwargs.get("use_azure")
        self.ocr_tool = OCRTool(type="ch_tra")
        if self.use_azure:
            self.client = construct_GPT4()
    
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

    def pdf2img(self):
        """Convert a PDF file to images."""
        images = convert_from_path(self.pdf_path, dpi=300)
        img_gray = cv2.cvtColor(np.array(images[0]), cv2.COLOR_BGR2GRAY)
        return img_gray


class Diaphragm_structure(Base_structure):
    """Derived class for specific operations on Diaphragm structure drawings."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def extrct_data(self, array):
        # rules
        length = len(array)
        s_big_word = '直徑大於'
        s_big_check = True
        s_small_word = '直徑小於'
        s_small_check = True

        wall_check1 = True
        wall_check2 = True
        wall_check3 = True
        wall_check4 = True

        for i in range(length):
            # check rebar strength 1
            if array[i][1].find(s_big_word) > -1:
                j = i
                while s_big_check:
                    if (array[j][1].upper()).find('KGF') > -1:
                        rebar_strength1 = get_the_num(array[j][1])
                        s_big_check = False
                    j+=1   

            # check rebar strength 2
            if array[i][1].find(s_small_word) > -1:
                k = i
                while s_small_check:
                    if (array[k][1].upper()).find('KGF') > -1:
                        rebar_strength2 = get_the_num(array[k][1])
                        s_small_check = False
                    k+=1  

            # check wall strength1
            if array[i][1].find('最小抗壓強度') > -1:
                h = i
                while wall_check1 :
                    if array[h][1].find('連續壁') > -1 :     
                        wall_check1 = False
                        w = h
                        l = h
                        while wall_check2 :
                            if (array[w][1].upper()).find('KGF') > -1 :
                                wall_check2 = False
                                call = check_is_right(array, array[w][1], w)
                                if call == 'True':
                                    wall_strength1 = get_the_num(array[w][1])
                                else:
                                    wall_strength1 = call 
                            w+=1
                        while wall_check3 :
                            if (array[l][1].upper()).find('WALLS') > -1 :
                                wall_check3 = False
                                o = l
                                while wall_check4 :
                                    if (array[o][1].upper()).find('KGF') > -1 :
                                        call = check_is_right(array, array[o][1], o)
                                        if call == 'True':
                                            wall_strength2 = get_the_num(array[o][1])
                                        else:
                                            wall_strength2 = call 
                                        wall_check4 = False
                                    o+=1
                            l+=1
                    h+=1
        return rebar_strength1, rebar_strength2, wall_strength1, wall_strength2
    
    def call_ui(self, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2):
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

        save_xml_button = tk.Button(self.window, text="Save XML File", command = lambda: self.save_xml_file(wall_strength1, wall_strength2, rebar_strength1, rebar_strength2))
        save_xml_button.pack(pady=(0,15), padx=(0, 0))

        # Run the Tkinter event loop
        self.window.mainloop()

    def save_xml_file(self, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2):
        downloads_path = str(Path.home() / "Downloads")
        file_path = filedialog.askdirectory( title='Please choose the save location for the XML file.',initialdir=downloads_path)

        try:
            downloads_path = file_path
            xmlfname = os.path.join(downloads_path, "Result.xml")
            print("The XML file has been saved at : " + str(xmlfname))
        except Exception as e:
            print(f"Error: {e}")
            downloads_path = str(Path.home() / "Downloads")
            xmlfname = os.path.join(downloads_path, "Result.xml")
            print("The XML file will be saved at the default location : " + str(xmlfname))

        #Export to XML
        xml_out_DD = open(xmlfname, 'ab')
        xml_out_DD.write(bytes('<WorkItem><File Description="設計圖說">', 'utf-8'))
        xml_out_DD.write(bytes('<Drawing Description="結構一般説明">', 'utf-8'))
        xml_out_DD.write(bytes("""
        <Concrete Description="混凝土" >
        <Strength1 Description="强度1" >
        <Value unit="kgf/cm2" >"""+str(wall_strength1)+"""</Value>
        </Strength1>
        <Strength2 Description="强度2" >
        <Value unit="kgf/cm2" >"""+str(wall_strength2)+"""</Value>
        </Strength2>
        </Concrete>
        <Rebar Description="鋼筋" >
        <Strength1 Description="强度1" >
        <Value unit="kgf/cm2" >"""+str(rebar_strength1)+"""</Value>
        </Strength1>
        <Strength2 Description="强度2" >
        <Value unit="kgf/cm2" >"""+str(rebar_strength2)+"""</Value>
        </Strength2>
        </Rebar>""", 'utf-8'))
        xml_out_DD.write(bytes('</Drawing></File></WorkItem>', 'utf-8'))
        xml_out_DD.close()  

        with open(xmlfname, 'rb') as f:
            lines = f.readlines()
            target=bytes('</File></WorkItem><WorkItem><File Description="設計圖說">', 'utf-8')
            repget_head=bytes('<Drawing Description="結構一般説明">', 'utf-8')
            repget_tail=bytes('</Drawing>', 'utf-8')
            repget_count=[]
            for i,iitem in enumerate(lines):
                target_pos=[]
                target_pos=iitem.find(target)
                if repget_tail in iitem and len(repget_count)>0:
                    repget_count[-1].append(i)
                if repget_head in iitem:
                    repget_count.append([i])
                if target_pos!=-1:
                    lines[i]=lines[i][:target_pos]+lines[i][target_pos+len(target):]
            for i,iitem in enumerate(repget_count[:-1]):
                head_pos=lines[iitem[0]].find(repget_head)
                tail_pos=lines[iitem[1]].find(repget_tail)
                lines[iitem[0]]=lines[iitem[0]][:head_pos]
                lines[iitem[1]]=lines[iitem[1]][tail_pos+len(repget_tail):]
                del lines[iitem[0]+1:iitem[1]]

        xml_out_DDD = open(xmlfname, 'wb')
        for i,iitem in enumerate(lines):
            xml_out_DDD.write(iitem)
        xml_out_DDD.close()  

        self.window.destroy()

    def run(self):
        try:
            super().wait_pdf()

            img_gray = super().pdf2img()
            if self.use_azure:
                pass
            else:
                array = self.ocr_tool.ocr(img_gray)
                rebar_strength1, rebar_strength2, wall_strength1, wall_strength2 = self.extrct_data(array)

        except Exception as e:
            print(f"An error occurred: {e}")
            wall_strength1 = 0
            wall_strength2 = 0
            rebar_strength1 = 0
            rebar_strength2 = 0

        self.call_ui(wall_strength1, wall_strength2, rebar_strength1, rebar_strength2)

        return
    
class BoredPile_structure(Base_structure):
    """Derived class for specific operations on BoredPile structure drawings."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def re_match(self, string):
        pattern = r'(\d+)\s*kgf/cm2'
        match = re.search(pattern, string)
        if match:
            return int(match.group(1))
        else:
            return None

    def extrct_data(self, bounds):

        s_big_word = '直徑大於'
        s_small_word = '直徑小於'
        result_dic = {'Concrete':{'Strength1':0, 'Strength2':0},
                          'Rebar':{'Strength1':0, 'Strength2':0}}

        lengths_of_bounds = len(bounds)
        
        for i in range(lengths_of_bounds):
            # check rebar strength 2
            if bounds[i][1].find(s_big_word) > -1:
                s_big_start = i
                while True:
                    if (bounds[s_big_start][1].upper()).find('KGF') > -1:
                        result_dic["Rebar"]['Strength2'] = get_the_num(bounds[s_big_start][1])
                        break  
                    s_big_start += 1

            # check rebar strength 1
            if bounds[i][1].find(s_small_word) > -1:
                s_small_start = i
                while True:
                    if (bounds[s_small_start][1].upper()).find('KGF') > -1:
                        result_dic["Rebar"]['Strength1'] = get_the_num(bounds[s_small_start][1])
                        break
                    s_small_start += 1

            # check wall strength1
            if bounds[i][1].find('最小抗壓強度') > -1:
                search_index = i
                while True:
                    if bounds[search_index][1].find('連續壁') > -1:
                        check = self.re_match(bounds[search_index+1][1])
                        if check:
                            result_dic["Concrete"]['Strength1'] = check
                            print(f'wall strength1: {result_dic["Concrete"]["Strength1"]}')
                    if bounds[search_index][1].find('WALLS') > -1:
                        check = self.re_match(bounds[search_index+1][1])
                        if check:
                            result_dic["Concrete"]['Strength2'] = check
                            print(f'wall strength2: {result_dic["Concrete"]["Strength2"]}')
                        break
                    search_index += 1

        return result_dic
    
    def save_xml_file(self, result_dic):
        print("The XML file has been saved at : " + str(self.output_path))
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        structure = root.find(".//Drawing[@description='結構一般説明']")
        if structure is None:
            structure = ET.SubElement(root, "Drawing", description='結構一般説明')
        else:
            # 移除plans的所有子節點
            for child in list(structure):
                structure.remove(child)
        # 將result_dic的資料寫入xml檔案
        for strength_key, value in result_dic.items():
            if strength_key == 'Concrete':
                strength_type = ET.SubElement(structure, strength_key, description='混凝土')
            else:
                strength_type = ET.SubElement(structure, strength_key, description='鋼筋')
            for k, v in value.items():
                if k == 'Strength1':
                    strength = ET.SubElement(strength_type, k, description='强度1')
                    value = ET.SubElement(strength, 'Value', unit='kgf/cm2')
                    value.text = str(v)
                else:
                    strength = ET.SubElement(strength_type, k, description='强度2')
                    value = ET.SubElement(strength, 'Value', unit='kgf/cm2')
                    value.text = str(v)
        
        # 將xml檔案寫入指定路徑
        tree.write(self.output_path, encoding='utf-8', xml_declaration=True)

        return
    
    def run(self):
        try:
            super().wait_pdf()

            result_dic = {'Concrete Strength':{'strength1':0, 'strength2':0},
                          'Rebar Strength':{'strength1':0, 'strength2':0}}

            img_gray = super().pdf2img()

            bounds = self.ocr_tool.ocr(img_gray)

            result_dic = self.extrct_data(bounds)

            self.output_path = create_gui(result_dic, 'BoredPile_structure')

            self.save_xml_file(result_dic)

            os.remove(self.pdf_path)

        except Exception as e:
            print(f"An error occurred: {e}")

        return