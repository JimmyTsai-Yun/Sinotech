# %% [markdown]
# ### Main code

# %%
import sys
import keyboard
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
import cv2
import numpy as np
from pdf2image import convert_from_path
import easyocr
from pathlib import Path
import os
import tkinter as tk
from tkinter import filedialog
import re

class Loader:
    def __init__(self, desc="Loading...", end="Done!", timeout=0.1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{self.end}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()


# functions
def get_the_num(string):
  x = []
  for j,k in enumerate(string):
    if k == ' ' or k == '=' :
      x.append(j)
  if len(x) < 2:
    x.append(x[0])
    for c,w in enumerate(string):
      if w == '2':
        x[0] = c
        break
  return string[x[0]+1 : x[1]]

def check_is_right(string):
    pattern = r'(\d+)\s*kgf/cm2'
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))
    else:
        return None

# convert pdf to image
dirpath=" ".join(sys.argv[1:])
pdfname="-Layout1.pdf"
pdfpath = dirpath+"\\"+pdfname
loader = Loader(pdfname+" is being created. Please wait..", "PDF File has been created!", 0.05).start()

image = convert_from_path(pdfpath, dpi =300)

try:
    while not os.path.exists(pdfpath):
        if keyboard.is_pressed("esc"):
            break
    loader.stop()

    image = convert_from_path(pdfpath, dpi =300)
    img = np.asarray(image[0])
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  
    # ocr
    reader = easyocr.Reader(['ch_tra','en'])

    bounds = reader.readtext(img_gray, detail=1)

    s_big_word = '直徑大於'
    s_small_word = '直徑小於'
    rebar_protection_exposed = None
    rebar_protection_diaphragm = None
    rebar_protection_candidate_list = []

    lengths_of_bounds = len(bounds)

    for i in range(lengths_of_bounds):
        if bounds[i][1].find('CONCRETE CAST AGAINST AND PERMANENTLY EXPOSED') > -1:
            rebar_protection_exposed = bounds[i][0]

        if bounds[i][1].find('DIAPHRAGM WALLS (BOTH FACES)') > -1:
            rebar_protection_diaphragm = bounds[i][0]

        pattern = r'(\d+)\s*mm'
        match = re.search(pattern, bounds[i][1])
        if match:
            rebar_protection_candidate_list.append([int(match.group(1)), bounds[i][0]])

        # check rebar strength 1
        if bounds[i][1].find(s_big_word) > -1:
            s_big_start = i
            while True:
                if (bounds[s_big_start][1].upper()).find('KGF') > -1:
                    rebar_strength1 = get_the_num(bounds[s_big_start][1])
                    print(f'rebar strength 1: {rebar_strength1}')
                    break  
                s_big_start += 1
            

        # check rebar strength 2
        if bounds[i][1].find(s_small_word) > -1:
            s_small_start = i
            while True:
                if (bounds[s_small_start][1].upper()).find('KGF') > -1:
                    rebar_strength2 = get_the_num(bounds[s_small_start][1])
                    print(f'rebar strength 2: {rebar_strength2}')
                    break
                s_small_start += 1
            

        # check wall strength1
        if bounds[i][1].find('最小抗壓強度') > -1:
            search_index = i
            while True:
                if bounds[search_index][1].find('連續壁') > -1: 
                    print(bounds[search_index+1][1])
                    check = check_is_right(bounds[search_index+1][1])
                    if check:
                        wall_strength1 = check
                        print(f'wall strength1: {wall_strength1}')
                if bounds[search_index][1].find('WALLS') > -1:
                    print(bounds[search_index+1][1])
                    check = check_is_right(bounds[search_index+1][1])
                    if check:
                        wall_strength2 = check
                        print(f'wall strength2: {wall_strength2}')
                    break
                search_index += 1

    # match rebar protection with the closest rebar protection candidate
    if rebar_protection_exposed:
        # format of easyocr output: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        # we want the second point (x2, y2) 
        exposed_x, exposed_y = rebar_protection_exposed[1]
        # find the closest candidate
        min_dist = float('inf')
        closest_candidate = None
        for candidate in rebar_protection_candidate_list:
            candidate_x, candidate_y = candidate[1][1]
            dist = (exposed_x - candidate_x) ** 2 + (exposed_y - candidate_y) ** 2
            if dist < min_dist:
                min_dist = dist
                closest_candidate = candidate
        rebar_protection_exposed = closest_candidate[0]

    if rebar_protection_diaphragm:
        diaphragm_x, diaphragm_y = rebar_protection_diaphragm[1]
        min_dist = float('inf')
        closest_candidate = None
        for candidate in rebar_protection_candidate_list:
            candidate_x, candidate_y = candidate[1][1]
            dist = (diaphragm_x - candidate_x) ** 2 + (diaphragm_y - candidate_y) ** 2
            if dist < min_dist:
                min_dist = dist
                closest_candidate = candidate
        rebar_protection_diaphragm = closest_candidate[0]

except:
   wall_strength1=0
   wall_strength2=0
   rebar_strength1=0
   rebar_strength2=0
   rebar_protection_exposed=0
   rebar_protection_diaphragm=0

print(wall_strength1)
print(wall_strength2)
print(rebar_strength1)
print(rebar_strength2)
print(rebar_protection_exposed)
print(rebar_protection_diaphragm)


# %%
# Check Final Reading Results

def save_xml_file():
    global downloads_path, xmlfname, wall_strength1, wall_strength2, rebar_strength1, rebar_strength2

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
    </Rebar>
    <Protection Description="保護層" >
    <Exposed Description="暴露部分" >
    <Value unit="mm" >"""+str(rebar_protection_exposed)+"""</Value>
    </Exposed>
    <Diaphragm Description="雙面" >
    <Value unit="mm" >"""+str(rebar_protection_diaphragm)+"""</Value>
    </Diaphragm>
    </Protection>
    """, 'utf-8'))
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

downloads_path = str(Path.home() / "Downloads")
xmlfname = os.path.join(downloads_path, "Result.xml")

window = tk.Tk()
window.title("Reading Results")

# Create a label for displaying "Plan/Elevation Drawing"
drawing_type_label = tk.Label(window, text="Drawing Type : Structural Descriptions", font=("Arial", 14))
drawing_type_label.pack(pady=(10,0))

# Create labels for the variables with unit
label_frame = tk.Frame(window)
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
rebar_protection_exposed_value = tk.Label(label_frame, text=str(rebar_protection_exposed) + " mm", font=("Arial", 14), fg="blue")
rebar_protection_diaphragm_value = tk.Label(label_frame, text=str(rebar_protection_diaphragm) + " mm", font=("Arial", 14), fg="blue")

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

save_xml_button = tk.Button(window, text="Save XML File", command=save_xml_file)
save_xml_button.pack(pady=(0,15), padx=(0, 0))

# Run the Tkinter event loop
window.mainloop()

# %%
# Remove redundant files

os.remove(pdfpath)
os.remove(dirpath +"\\"+ "PUBLIST.dsd")
# %% [markdown]
# ### **Export to EXE** 

# %%
"""
1. Type : >Export to Python Script in search bar
2. Open CMD in the file folder
3. Type ：
pip install pyinstaller
pyinstaller --onefile "Data Process - Structural Descriptions.py" -w
pyinstaller -F "Data Process - Structural Descriptions.py" --collect-all easyocr
pyinstaller "Data Process - Structural Descriptions.py" --add-data "C:/Users/Ricardo/.EasyOCR/model/*;models" --hidden-import easyocr --collect-all easyocr --noconfirm
"""