from lib.utils import *
import sys
import keyboard
import tkinter as tk
from tkinter import filedialog
    
class Base_structure:
    """Base class for handling PDF to image conversion and OCR processing."""
    def __init__(self, **kwargs):
        self.pdf_path = kwargs.get("pdf_path")
        self.csv_path = kwargs.get("csv_path")
        self.output_path = kwargs.get("output_path")
        self.use_azure = kwargs.get("use_azure")
        if self.use_azure:
            self.client = construct_GPT4()  # assuming construct_GPT4() is properly defined

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
    
    def ocr(self, img_gray):
        """Perform OCR on the given image."""
        reader = easyocr.Reader(['ch_tra', 'en'])
        bounds = reader.readtext(img_gray, detail=1)
        return np.array(bounds)

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
    
    def run(self):
        try:
            super().wait_pdf()

            img_gray = super().pdf2img()
            array = super().ocr(img_gray)

            rebar_strength1, rebar_strength2, wall_strength1, wall_strength2 = self.extrct_data(array)

        except Exception as e:
            print(f"An error occurred: {e}")
            wall_strength1 = 0
            wall_strength2 = 0
            rebar_strength1 = 0
            rebar_strength2 = 0