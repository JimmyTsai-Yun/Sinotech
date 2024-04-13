from lib.utils import *
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
    """Base class for handling PDF to image conversion and OCR processing."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    """Derived class for specific operations on Diaphragm structure drawings."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def check_is_right(array, string, count):
        return array[count-1][1] if string.find('f\'c') == -1 else 'True'

    @staticmethod
    def get_the_num(string):
        indices = [j for j, k in enumerate(string) if k in [' ', '=']]
        if len(indices) < 2:
            indices.append(indices[0])
            for c, char in enumerate(string):
                if char == '2':
                    indices[0] = c
                    break
        return string[indices[0]+1 : indices[1]]
    
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
                        rebar_strength1 = self.get_the_num(array[j][1])
                        s_big_check = False
                    j+=1   

            # check rebar strength 2
            if array[i][1].find(s_small_word) > -1:
                k = i
                while s_small_check:
                    if (array[k][1].upper()).find('KGF') > -1:
                        rebar_strength2 = self.get_the_num(array[k][1])
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
                                call = self.check_is_right(array, array[w][1], w)
                                if call == 'True':
                                    wall_strength1 = self.get_the_num(array[w][1])
                                else:
                                    wall_strength1 = call 
                                count3 = w
                            w+=1
                        while wall_check3 :
                            if (array[l][1].upper()).find('DIAPHRAGM WALLS') > -1 :
                                wall_check3 = False
                                o = l
                                while wall_check4 :
                                    if (array[o][1].upper()).find('KGF') > -1 :
                                        call = self.check_is_right(array, array[o][1], o)
                                        if call == 'True':
                                            wall_strength2 = self.get_the_num(array[o][1])
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