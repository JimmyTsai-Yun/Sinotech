# %% [markdown]
# ### **Import Module, Define Class, & Define Function**

# %%
import re
import os
import sys
import csv
import math
import numpy as np
from operator import itemgetter
from itertools import chain
from pathlib import Path
import copy
import tkinter as tk
from tkinter import filedialog

#define Function
###########################################################################################
def get_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

def check_line_intersect(line1, line2):
    """Return True if line segment line1 intersects line segment line2."""
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]
    # Compute the slopes and y-intercepts of the lines
    m1 = (y2 - y1) / (x2 - x1) if x1 != x2 else float('inf')
    b1 = y1 - m1 * x1 if x1 != x2 else None
    m2 = (y4 - y3) / (x4 - x3) if x3 != x4 else float('inf')
    b2 = y3 - m2 * x3 if x3 != x4 else None
    # Handle special cases of vertical lines
    if x1 == x2:
        if x3 == x4:
            return x1 == x3 and (min(y1, y2) <= max(y3, y4) and min(y3, y4) <= max(y1, y2))
        else:
            y = m2 * x1 + b2
            return (min(x3, x4) <= x1 <= max(x3, x4)) and (min(y1, y2) <= y <= max(y1, y2))
    elif x3 == x4:
        y = m1 * x3 + b1
        return (min(x1, x2) <= x3 <= max(x1, x2)) and (min(y3, y4) <= y <= max(y3, y4))
    # Compute the intersection point (if any)
    if m1 == m2:
        return False
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    if (min(x1, x2) <= x <= max(x1, x2)) and (min(x3, x4) <= x <= max(x3, x4)) and \
            (min(y1, y2) <= y <= max(y1, y2)) and (min(y3, y4) <= y <= max(y3, y4)):
        return True
    else:
        return False

def line_overlaps_box(point1, point2, boxpoint1, boxpoint2):
    x1, y1 = point1
    x2, y2 = point2
    bx1, by1 = boxpoint1
    bx2, by2 = boxpoint2
    # Determine the min and max x and y coordinates of the box
    min_x, max_x = min(bx1, bx2), max(bx1, bx2)
    min_y, max_y = min(by1, by2), max(by1, by2)
    # Check if either point of the line is inside the box
    if min_x <= x1 <= max_x and min_y <= y1 <= max_y:
        return True
    if min_x <= x2 <= max_x and min_y <= y2 <= max_y:
        return True
    # Decompose the box into four line segments and check if the input line intersects any of them
    if check_line_intersect((point1, point2), ((bx1, by1), (bx2, by1))):
        return True
    if check_line_intersect((point1, point2), ((bx2, by1), (bx2, by2))):
        return True
    if check_line_intersect((point1, point2), ((bx2, by2), (bx1, by2))):
        return True
    if check_line_intersect((point1, point2), ((bx1, by2), (bx1, by1))):
        return True
    return False

def rotate_coor(x0, y0, angle, cx=0, cy=0):
    # Convert the angle to radians
    angle_rad = math.radians(angle)

    # Translate the point to the origin
    x0 -= cx
    y0 -= cy

    # Rotate the point around the origin
    x1 = x0 * math.cos(angle_rad) - y0 * math.sin(angle_rad)
    y1 = x0 * math.sin(angle_rad) + y0 * math.cos(angle_rad)

    # Translate the point back to the original position
    x1 += cx
    y1 += cy

    return [x1, y1]


def p2l_CD(point, line):
    x_point, y_point = point
    x1, y1, x2, y2 = line
    # Compute the distance between the point and the line
    # using the formula:
    # distance = abs((y2 - y1) * x_point - (x2 - x1) * y_point + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    numerator = abs((y2 - y1) * x_point - (x2 - x1) * y_point + x2 * y1 - y2 * x1)
    denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    distance = numerator / denominator
    return distance

# %%
#Define Rebar class
class vert_rebar:
  def __init__(self,rebar_type_textbox,rebar_side_textbox,vert_line, pointer, gl_line):
    self.rebar_type_textbox=rebar_type_textbox
    self.rebar_side_textbox=rebar_side_textbox
    self.vert_line=vert_line
    self.pointer=pointer
    self.gl_line=gl_line

    self.rebar_type=rebar_type_textbox[-1]
    self.rebar_side=rebar_side_textbox[-1]
    self.datum_level0=(gl_line[3][1]+gl_line[4][1])/2
    self.depth_level1= round(self.datum_level0 - max(vert_line[3][1],vert_line[4][1]),1)
    self.depth_level2= round(self.datum_level0 - min(vert_line[3][1],vert_line[4][1]),1)

  def __str__(self):
    return str(self.rebar_side)+" vertical rebar "+str(self.rebar_type)+" from "+str(self.depth_level1)+"m to "+str(self.depth_level2)+"m"
  
  def set_depth_level1(self,depth):
    self.depth_level1= round(depth,1)

  def set_depth_level2(self,depth):
    self.depth_level2= round(depth,1)

# %% [markdown]
# ### **OCR**

# %%
#OCR
import PIL
from PIL import Image, ImageDraw, ImageFont
import pdf2image
import cv2
import easyocr
import numpy as np
import pandas as pd
from tqdm import tqdm

def FLD(image,drawimage):
    # Create default Fast Line Detector class
    fld = cv2.ximgproc.createFastLineDetector()
    # Get line vectors from the image
    lines = fld.detect(image)

    # Draw lines on the image
    line_on_image = fld.drawSegments(drawimage, lines)
    
    return lines

def draw_text(img, bounds, size):
    ah = img
    draw = ImageDraw.Draw(ah)
    font = ImageFont.truetype('./msjh.ttc', size)
    for bound in bounds:
        conf= (int)(bound[2]*100)
        text = bound[1] + f" {conf}%"
        top_left = tuple(bound[0][0])
        bottom_right = tuple(bound[0][2]) 
        top_top = tuple([bound[0][0][0], bound[0][0][1]-20])
        draw.text(top_top, text, font=font, fill=(255,0,0,128))
        draw.rectangle([top_left, bottom_right],outline='red' )
    ah.show()
    return ah

# preparetion
dirpath=" ".join(sys.argv[1:])
#dirpath=f"D:\\06 Master\\003 Research Projects\\01 Sinotech\Drawings from Sinotech\8.LG09站連續壁配筋及支撐配置圖"
drawing_index       = []
drawing_to_skip     = []
wall_type_list      = []
wall_depth_list     = []
wall_depth_dis_list = []
hori_rebar_list     = []
wall_thick_list     = []
shear_rebar_list    = []
rebar_protection_list    = []
reader = easyocr.Reader(['en'])

# Read the pdf file
print('Reading pdf...')
img = pdf2image.convert_from_path(dirpath+"\\"+"-Layout1.pdf", dpi=210)

for image in tqdm(range(len(img))):
    # check the drawing is about rebar
    checking = False
    # print(f"Now proccessing page {image+1}/{len(img)}")

    # 讀水平字
    cv_img = cv2.cvtColor(np.asarray(img[image]), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, img_th = cv2.threshold (img_gray, 240, 255, 0)

    bounds_1 = reader.readtext(img_th , detail=1)
    array_1 = np.array(bounds_1, dtype=object)

    # 讀垂直字
    cv_img = cv2.cvtColor(np.asarray(img[image]), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    img_gray_ROTATE_90_CLOCKWISE = cv2.rotate(img_gray, cv2.ROTATE_90_CLOCKWISE)
    _, img_th_ROTATE_90_CLOCKWISE = cv2.threshold (img_gray_ROTATE_90_CLOCKWISE, 210, 255, 0)

    bounds_2 = reader.readtext(img_th_ROTATE_90_CLOCKWISE , detail=1)
    array_2 = np.array(bounds_2, dtype=object)

    # 0. rebar protection
    protection_check = -1
    for bound in bounds_1:
       pattern = r'(\d+)\s*CL'
       match = re.search(pattern, bound[1])
       if match:
            print(f'{image+1}頁: {match.group(1)}mm')
            rebar_protection_list.append(match.group(1))
            protection_check = 1
            break
    if protection_check == -1:
        rebar_protection_list.append("No found")
    

    # 1. wall type
    key_word = "DIAPHRAGM WALL TYPE"
    wall_type = "No found"

    for bound in bounds_1:
        if(bound[1].find(key_word) > -1):
            checking = True
            for a, b in enumerate(bound[1]):
                if b == ' ' :
                    check1 = a
                    wall_type = bound[1][a+1:len(bound[1])]

    # If keyword no found, skip this drawing
    if(checking != True):
        drawing_to_skip.append(image)
        continue

    wall_type_list.append(wall_type)

    # 2. wall depth and distribution
    depth_distribution = []
    depth_dis_index = []
    wall_depth = 0
    temp = 0

    for index_for_depth in range(30):
        x_length = bounds_2[index_for_depth][0][1][0] - bounds_2[index_for_depth][0][0][0]
        y_length = bounds_2[index_for_depth][0][3][1] - bounds_2[index_for_depth][0][0][1]
        if(x_length > y_length and bounds_2[index_for_depth][2] > 0.6):
            head_y = bounds_2[index_for_depth][0][0][1]
            strr = bounds_2[index_for_depth][1]
            if(strr.isdigit()):
                if(temp==0):
                    temp = head_y
                    depth_distribution.append((int)(bounds_2[index_for_depth][1]))
                    depth_dis_index.append(bounds_2[index_for_depth])
                else:
                    if( (head_y-20) <= temp ):
                        depth_distribution.append((int)(bounds_2[index_for_depth][1]))
                        depth_dis_index.append(bounds_2[index_for_depth])
                    else:
                        break

    wall_depth = sum(depth_distribution)
    wall_depth_list.append(wall_depth)
    wall_depth_dis_list.append(depth_distribution)

    # 4. horizontal rebar
    hori_rebar_exc_side = "No Found"
    hori_rebar_ret_side = "No Found"

    excavated = []
    retained  = []
    for bound in bounds_1:
        if(bound[1].find("EXCAVATED") > -1 and bound[1].find("SIDE") > -1):
            excavated.append(bound)
        if(bound[1].find("RETAINED") > -1 and bound[1].find("SIDE") > -1):
            retained.append(bound)


    # check out the correct one we need
    pair_side = []
    for num_1,content_1 in enumerate(excavated):
        for num_2, content_2 in enumerate(retained):
            x1, y1 = content_1[0][1][0], content_1[0][1][1] # excated 的右上角
            x2, y2 = content_2[0][0][0], content_2[0][0][1] # retained 的左上角
            if(y1-40 < y2 and y1+40 > y2 and x1+500 >  x2 and x2 > x1):
                pair_side.append([num_1, num_2])

    try:
        exc_side = excavated[pair_side[1][0]]
        ret_side = retained[pair_side[1][1]]
        for bound in bounds_1:
            if(bound[0][0][0] > exc_side[0][0][0] and bound[0][1][0] < exc_side[0][1][0] and (exc_side[0][0][1] - 50) < bound[0][2][1] and exc_side[0][2][1] > bound[0][2][1] ):
                if(bound[1].find("D")>-1):
                    hori_rebar_exc_side = bound[1]
            if(bound[0][0][0] > ret_side[0][0][0] and bound[0][1][0] < ret_side[0][1][0] and (ret_side[0][0][1] - 50) < bound[0][2][1] and ret_side[0][2][1] > bound[0][2][1] ):
                if(bound[1].find("D")>-1):
                    hori_rebar_ret_side = bound[1]
    except:
        hori_rebar_exc_side = "failed"
        hori_rebar_ret_side = "failed"
        print("failed to read hori_rebar index.")

    hori_rebar_list.append([hori_rebar_exc_side, hori_rebar_ret_side])

    # 5. thickness
    wall_thick = 0

    left  = excavated[pair_side[0][0]]
    right = retained[pair_side[0][1]]

    for bound in bounds_1:
        if(bound[0][0][0] > left[0][1][0] and bound[0][1][0] < right[0][0][0] and bound[0][0][1] + 5 > left[0][0][1] and bound[0][2][1] < left[0][2][1] + 5 and bound[2] > 0.6):
            wall_thick = bound[1]

    wall_thick_list.append(wall_thick)

    # 6. shear rebar and distribution
    shear_rebar = [None]*len(depth_dis_index)

    for shear_rebar_index, bound in enumerate(bounds_2):
        mid = (depth_dis_index[len(depth_dis_index)-1][0][0][0] + depth_dis_index[len(depth_dis_index)-1][0][1][0])/2
        head = depth_dis_index[len(depth_dis_index)-1][0][0][0]
        if(bound[2] > 0.7 and head-200 < bound[0][0][0] and head + 150 > bound[0][0][0]):
            if(depth_dis_index[len(depth_dis_index)-1][0][0][1] + 600 > bound[0][0][1] and depth_dis_index[len(depth_dis_index)-1][0][0][1] + 450 < bound[0][0][1]):
                if(bound[1].find("D") > -1):
                    shear_rebar[len(depth_dis_index)-1] = bound[1]
                    for count in range(len(depth_dis_index)-1):
                        shear_rebar[len(depth_dis_index)-2-count] = bounds_2[shear_rebar_index-1-count][1]

    end_depth = wall_depth
    start_depth = end_depth
    shear_rebar_list.append([])
    for i in range(len(depth_dis_index)):
        start_depth = start_depth - depth_distribution[i]
        shear_rebar_list[-1].append([shear_rebar[i],start_depth,end_depth])
        end_depth = start_depth

    drawing_index.append(image)

# %%
for n in range(len(drawing_index)):
    print(wall_type_list[n])
    print(wall_thick_list[n])
    print(wall_depth_list[n])
    print(hori_rebar_list[n])
    print(shear_rebar_list[n])
    print(rebar_protection_list[n])
    print("\n")

# %% [markdown]
# ## **Vertical Rebar**

# %% [markdown]
# ### **Import CSV**

# %%
#import CSV
csvpath=dirpath +"\\"+ "Vertical Line Info.csv"
vertline_info=[]
with open(csvpath, newline='') as f:
    vertline_info = list(csv.reader(f))
    del vertline_info[0]
    for i in vertline_info:
      i[1]=i[1][14:-1]
      i[3]=float(i[3])
      i[4]=i[4][1:-1].split()
      for j in range(3): i[4][j]=float(i[4][j])
      i[5]=i[5][1:-1].split()
      for j in range(3): i[5][j]=float(i[5][j])
      if i[5][0]-i[4][0]!=0:
        i[6]=math.atan((i[5][1]-i[4][1])/(i[5][0]-i[4][0]))*180/math.pi
      else:i[6]=90
print("vertline_info: [0] File Name, [1] Entity Name, [2] Layer Name, [3] Line Length, [4] Start Coor, [5] End Coor, [6] Line Gradient")

csvpath=dirpath +"\\"+ "Helper Line Info.csv"
helperline_info=[]
with open(csvpath, newline='') as f:
    helperline_info = list(csv.reader(f))
    del helperline_info[0]
    for i in helperline_info:
      i[3]=i[3][1:-1].split()
      for j in range(3): i[3][j]=float(i[3][j])
      i[4]=i[4][1:-1].split()
      for j in range(2): i[4][j]=float(i[4][j])
      i[5]=i[5][1:-1].split()
      for j in range(2): i[5][j]=float(i[5][j])
      del i[6]
print("helperline_info: [0] File Name, [1] Entity Name, [2] Object Type, [3] Base Point Coor, [4] Up Left Coor, [5] Down Right Coor")

csvpath=dirpath +"\\"+ "Text Info.csv"
tinfo=[]
with open(csvpath, newline='') as f:
    tinfo = list(csv.reader(f))
    del tinfo[0]
    for i in tinfo:
      i[1]=i[1][14:-1]
      i[3]=round(math.degrees(float(i[3])))%180
      i[4]=i[4][1:-1].split()
      for j in range(3): i[4][j]=float(i[4][j])
      x0,y0 = i[4][:2]
      width,height = float(i[6]),float(i[5])
      x1,y1 = rotate_coor(x0+width,y0+height,i[3],x0,y0)
      upper_left_x = min(x0,x1)
      upper_left_y = max(y0,y1)
      lower_right_x = max(x0,x1)
      lower_right_y = min(y0,y1)
      upper_left = [upper_left_x, upper_left_y]
      lower_right = [lower_right_x, lower_right_y]
      i[5],i[6]=upper_left,lower_right
      i[7]=" ".join(i[7].split()).upper()
      del i[8]
print("tinfo: [0] File Name, [1] Entity Name, [2] Object Type, [3] Rotation Angle, [4] Centre Coor, [5] Start Coor, [6] End Coor, [7] Text")

# %% [markdown]
# ### **Data Pre-Process**

# %%
#Data Pre-Process
#vertline_info Pre-Process
dwgfname= sorted(list(set(i[0] for i in tinfo)))
dwg_vertline=[]
for i in dwgfname:
    if dwgfname.index(i) in drawing_to_skip:continue
    dwg_vertline.append([])
    for j in vertline_info:
        if i == j[0]:
            dwg_vertline[-1].append(j[1:])
print("dwg_vertline[file name]: [0] Entity Name, [1] Layer Name, [2] Line Length, [3] Start Coor, [4] End Coord, [5] Line Gradient")

#helperline_info Pre-Process
dwg_helperline=[]
for i in dwgfname:
    if dwgfname.index(i) in drawing_to_skip:continue
    dwg_helperline.append([])
    for j in helperline_info:
        if i == j[0]:
            dwg_helperline[-1].append(j[1:])
print("dwg_helperline[file name]: [0] Entity Name, [1] Object Type, [2] Base Point Coor, [3] Up Left Coor, [4] Down Right Coor")

#tinfo Pre-Process
dwg_text=[]
dwg_dat_text=[]
for i in dwgfname:
    if dwgfname.index(i) in drawing_to_skip:continue
    dwg_text.append([])
    dwg_dat_text.append([])
    for j in tinfo:
        if i == j[0]:
            if "GL " in j[-1].upper() or "TOP EL" in j[-1].upper():
                dwg_dat_text[-1].append(j[1:])
            else:
                dwg_text[-1].append(j[1:])
print("dwg_text[file name]: [0] Entity Name, [1] Object Type, [2] Rotation Angle, [3] Centre Coor, [4] Start Coor, [5] End Coor, [6] Text")

#find the datum line
dwg_datline=[]
for n,file in enumerate(dwg_dat_text):
    for t,text in enumerate(file):
        temp_distance_list=[]
        for l,line in enumerate(dwg_vertline[n]):
            if line[5]==0 and line[4][1]<=text[4][1]: 
                temp_distance_list.append([line,(p2l_CD(text[3][:2],line[3][:2]+line[4][:2]))])
        temp_distance_list.sort(key=itemgetter(1),reverse=False)
    dwg_datline.append(temp_distance_list[0][0])

#find the vert rebar
dummy_dwg_vertline=[]
line_pointer_group=[]
x_range=[]
for n,file in enumerate(dwg_vertline):
    dummy_dwg_vertline.append([])
    line_pointer_group.append([])
    x_range.append([])
    for l,line in enumerate(file):
        for h,hline in enumerate(dwg_helperline[n]):
            if line_overlaps_box(line[3][:2],line[4][:2],hline[3],hline[4]):
                if line[5]==90: 
                    dummy_dwg_vertline[-1].append(line)
                    x_range[-1].extend([line[3][0],line[4][0]])
                    line_pointer_group[-1].append([line,hline])
    x_range[-1]=sorted(list(set(x_range[-1])))  
dwg_vertline=copy.copy(dummy_dwg_vertline)

dwg_rebar_type=[]
dwg_rebar_side=[]
for n,file in enumerate(dwg_vertline[:]):
    dwg_rebar_type.append([])
    dwg_rebar_side.append([])
    for t,text in enumerate(dwg_text[n]):
        #if "SIDE" in text[-1].upper(): print(x_range[n][0],text[3][0],x_range[n][-1])
        if x_range[n][0]<=text[3][0]<=x_range[n][-1] :
            if "@" in text[-1].upper():
                dwg_rebar_type[-1].append(text)
            if "SIDE" in text[-1].upper():
                dwg_rebar_side[-1].append(text)

# %% [markdown]
# ### **Object Grouping**
# 

# %%
#object grouping
textbox_group=[]
for n,file in enumerate(dwg_rebar_type):
    textbox_group.append([])
    for rs,side_textbox in enumerate(dwg_rebar_side[n]):
        temp_group=[]
        for rt,type_textbox in enumerate(file):
            if type_textbox[3][1]>side_textbox[3][1]:
                temp_group.append([type_textbox,side_textbox,get_distance(type_textbox[3],side_textbox[3])])
        temp_group.sort(key=itemgetter(2), reverse=False)  
        textbox_group[-1].append(temp_group[0])

dwg_vert_rebar_info=[]
for n,file in enumerate(textbox_group):
    dwg_vert_rebar_info.append([])
    for lp,line_pointer in enumerate(line_pointer_group[n]):
        best_pair= None
        nearest_pair_distance= 0
        for tb,textbox in enumerate(textbox_group[n]):
            if textbox[1][3][1]<=line_pointer[1][2][1]<=textbox[0][3][1]:
                p1 = line_pointer[1][2]
                p2 = [sum(x)/len(x) for x in zip(*[textbox[1][3], textbox[1][4], textbox[0][3], textbox[0][4]])]+[0]
                pair_distance=get_distance(p1,p2)
                if pair_distance<nearest_pair_distance or nearest_pair_distance==0:
                    best_pair=textbox
                    nearest_pair_distance= pair_distance
        vert_rebar_info=vert_rebar(best_pair[0],best_pair[1],line_pointer[0],line_pointer[1],dwg_datline[n])
        dwg_vert_rebar_info[-1].append(vert_rebar_info)
                

print("Vertical Rebar:")
for n,file in enumerate(dwg_vert_rebar_info):
    print(dwgfname[n])
    min_depth_level=0.0
    max_depth_level=wall_depth_list[n]/1000
    threshold=0.25
    for v in file:
        if abs(v.depth_level1-min_depth_level)<=threshold:v.set_depth_level1(min_depth_level)
        if abs(v.depth_level2-max_depth_level)<=threshold:v.set_depth_level2(max_depth_level)
        print(v)

# %%
#Visualization
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
# Create a new figure and axis object

# Iterate over each textbox element in tinfo and plot it
for n,file in enumerate(dwg_vert_rebar_info):
    fig, ax = plt.subplots()
    color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w', 'skyblue', 'limegreen', 'orange', 'purple']
    for v,vert_rebar_info in enumerate(file):
        # Extract the relevant information from the textbox element
        i=vert_rebar_info.pointer
        entity_name, obj_type, base_point, upleft_coor, downright_coor = i
        x0, y0 = upleft_coor
        x1, y1 = downright_coor
        width = x1 - x0
        height = y0 - y1
        # Add the Rectangle object to the axis object
        ax.add_patch(Rectangle((x0, y0), width, height, facecolor=color_list[v%len(color_list)], edgecolor=color_list[v%len(color_list)]))
        # Add the text string to the axis object
        #ax.text(x0 + width/2, y0 + height/2, text[20:], ha='center', va='center')

        j=vert_rebar_info.vert_line
        x_values = [j[4][0],j[3][0]]
        y_values = [j[4][1],j[3][1]]
        #ax.plot(x_values,y_values,colormap[fsource.index(i)%len(colormap)])
        ax.plot(x_values,y_values,color_list[v%len(color_list)])

        k=vert_rebar_info.gl_line
        x_values = [k[4][0],k[3][0]]
        y_values = [k[4][1],k[3][1]]
        #ax.plot(x_values,y_values,colormap[fsource.index(i)%len(colormap)])
        ax.plot(x_values,y_values,color_list[v%len(color_list)]) 

        i=vert_rebar_info.rebar_type_textbox
        # Extract the relevant information from the textbox element
        entity_name, obj_type, rotation,base_point, upleft_coor, downright_coor, text = i
        x0, y0 = upleft_coor
        x1, y1 = downright_coor
        width = x1 - x0
        height = y0 - y1
        # Add the Rectangle object to the axis object
        ax.add_patch(Rectangle((x0, y0), width, height, facecolor=color_list[v%len(color_list)], edgecolor=color_list[v%len(color_list)]))
        # Add the text string to the axis object
        #ax.text(x0 + width/2, y0 + height/2, text[20:], ha='center', va='center')
        i=vert_rebar_info.rebar_side_textbox

        # Extract the relevant information from the textbox element
        entity_name, obj_type, rotation,base_point, upleft_coor, downright_coor, text = i
        x0, y0 = upleft_coor
        x1, y1 = downright_coor
        width = x1 - x0
        height = y0 - y1
        # Add the Rectangle object to the axis object
        ax.add_patch(Rectangle((x0, y0), width, height, facecolor=color_list[v%len(color_list)], edgecolor=color_list[v%len(color_list)]))
        # Add the text string to the axis object
        #ax.text(x0 + width/2, y0 + height/2, text[20:], ha='center', va='center')
    # Show the plot
    #plt.show()
    for v,vert_rebar_info in enumerate(file):
        print(vert_rebar_info)
    

# %% [markdown]
# ## **Horizontal Shear Rebar**

# %% [markdown]
# ### **Import CSV**

# %%
#import CSV
csvpath=dirpath +"\\"+ "SH Text Info.csv"
sh_tinfo=[]
with open(csvpath, newline='') as f:
    sh_tinfo = list(csv.reader(f))
    del sh_tinfo[0]
    for i in sh_tinfo:
      i[1]=i[1][14:-1]
      i[3]=round(math.degrees(float(i[3])))%180
      i[4]=i[4][1:-1].split()
      for j in range(3): i[4][j]=float(i[4][j])
      x0,y0 = i[4][:2]
      width,height = float(i[6]),float(i[5])
      x1,y1 = rotate_coor(x0+width,y0+height,i[3],x0,y0)
      upper_left_x = min(x0,x1)
      upper_left_y = max(y0,y1)
      lower_right_x = max(x0,x1)
      lower_right_y = min(y0,y1)
      upper_left = [upper_left_x, upper_left_y]
      lower_right = [lower_right_x, lower_right_y]
      i[5],i[6]=upper_left,lower_right
      i[7]=" ".join(i[7].split()).upper()
      del i[8]
print("sh_tinfo: [0] File Name, [1] Entity Name, [2] Object Type, [3] Rotation Angle, [4] Centre Coor, [5] Start Coor, [6] End Coor, [7] Text")

csvpath=dirpath +"\\"+ "SH Line Info.csv"
sh_line_info=[]
with open(csvpath, newline='') as f:
    sh_line_info = list(csv.reader(f))
    del sh_line_info[0]
    for i in sh_line_info:
      i[1]=i[1][14:-1]
      i[3]=float(i[3])
      i[4]=i[4][1:-1].split()
      for j in range(3): i[4][j]=float(i[4][j])
      i[5]=i[5][1:-1].split()
      for j in range(3): i[5][j]=float(i[5][j])
      if i[5][0]-i[4][0]!=0:
        i[6]=math.atan((i[5][1]-i[4][1])/(i[5][0]-i[4][0]))*180/math.pi
      else:i[6]=90
print("sh_line_info: [0] File Name, [1] Entity Name, [2] Layer Name, [3] Line Length, [4] Start Coor, [5] End Coor, [6] Line Gradient")

csvpath=dirpath +"\\"+ "SH Helper Line Info.csv"
sh_helperline_info=[]
with open(csvpath, newline='') as f:
    sh_helperline_info = list(csv.reader(f))
    del sh_helperline_info[0]
    for i in sh_helperline_info:
      i[3]=i[3][1:-1].split()
      for j in range(3): i[3][j]=float(i[3][j])
      i[4]=i[4][1:-1].split()
      for j in range(2): i[4][j]=float(i[4][j])
      i[5]=i[5][1:-1].split()
      for j in range(2): i[5][j]=float(i[5][j])
      del i[6]
print("sh_helperline_info: [0] File Name, [1] Entity Name, [2] Object Type, [3] Base Point Coor, [4] Up Left Coor, [5] Down Right Coor")

# %% [markdown]
# ### **Data Pre-Process**

# %%
#Data Pre-Process
#vertline_info Pre-Process
dwgfname= sorted(list(set(i[0] for i in sh_tinfo)))

#tinfo Pre-Process
dwg_text_sh=[]
for i in dwgfname:
    if dwgfname.index(i) in drawing_to_skip:continue
    dwg_text_sh.append([])
    for j in sh_tinfo:
        if i == j[0]:
            if "@" in j[-1].upper():
                dwg_text_sh[-1].append(j[1:])
print("dwg_text_sh[file name]: [0] Entity Name, [1] Object Type, [2] Rotation Angle, [3] Centre Coor, [4] Start Coor, [5] End Coor, [6] Text")

dwg_line_sh=[]
for i in dwgfname:
    if dwgfname.index(i) in drawing_to_skip:continue
    dwg_line_sh.append([])
    for j in sh_line_info:
        if i == j[0]:
            dwg_line_sh[-1].append(j[1:])
print("dwg_line_sh[file name]: [0] Entity Name, [1] Layer Name, [2] Line Length, [3] Start Coor, [4] End Coord, [5] Line Gradient")

#helperline_info Pre-Process
dwg_helperline_sh=[]
for i in dwgfname:
    if dwgfname.index(i) in drawing_to_skip:continue
    dwg_helperline_sh.append([])
    for j in sh_helperline_info:
        if i == j[0]:
            dwg_helperline_sh[-1].append(j[1:])
print("dwg_helperline_sh[file name]: [0] Entity Name, [1] Object Type, [2] Base Point Coor, [3] Up Left Coor, [4] Down Right Coor")

#determine the reference line
dwg_coor=[]
skipped_no=0
for i in range(0,len(dwgfname)):
    if i in drawing_to_skip:
        skipped_no+=1
        continue
    i=i-skipped_no
    dwg_line_sh[i].sort(key=itemgetter(4),reverse=False)
    dwg_line_sh[i].sort(key=itemgetter(3),reverse=True)
    max_height=[0,max(dwg_line_sh[i][0][3][1],dwg_line_sh[i][0][4][1])]
    for j in range(len(dwg_line_sh[i])):
        if min(dwg_line_sh[i][j][3][0],dwg_line_sh[i][j][4][0]) == min(dwg_line_sh[i][0][3][0],dwg_line_sh[i][0][4][0]):
            if dwg_line_sh[i][j][3][1] > max_height[1] or dwg_line_sh[i][j][4][1] > max_height[1]:
                max_height=[j,max(dwg_line_sh[i][j][3][1],dwg_line_sh[i][j][4][1])]
        else : break
    ref_line=dwg_line_sh[i][max_height[0]]
    dwg_coor.append([ref_line[3][0],ref_line[3][1],ref_line[4][0],ref_line[4][1]])


# %% [markdown]
# ### **OCR**

# %%
#OCR
from roboflow import Roboflow
import cv2
import numpy as np
from pdf2image import convert_from_path
import PIL
from PIL import ImageDraw, ImageFont, Image
import easyocr
import os
import re
from tqdm import tqdm

# some functions
def FLD(image,drawimage):
    x_index = image.shape[1]
    # Create default Fast Line Detector class
    fld = cv2.ximgproc.createFastLineDetector()
    # Get line vectors from the image
    lines = fld.detect(image)
    # Draw lines on the image
    line_on_image = fld.drawSegments(drawimage, lines)

    return lines, x_index

def check_line(lines, x_index):
  dist = 1000000000000000
  record = 0
  for i in range(len(lines)):
    line = lines[i]
    head_x = line[0,0]
    head_y = line[0,1]
    end_x = line[0,2]
    end_y = line[0,3]
    if (end_x - head_x)**2 > (end_y - head_y)**2: #### here
      if (head_x-x_index)**2 + (head_y)**2 < dist and abs(head_x - end_x) > 300:
        dist = (head_x-x_index)**2 + (head_y)**2
        record = i
  return record

def extract_number(input_string):
    pattern = r"[-+]?\d*\.\d+|\d+"
    match = re.search(pattern, input_string)

    if match:
        extracted_number = match.group()
        return extracted_number
    else:
        return None

def get_depth(info,target):
  start_index  = (info[0][0][0][1] + info[0][0][2][1]) // 2
  end_index  = (info[1][0][0][1] + info[1][0][2][1]) // 2
  target_index = float(target['y'])
  return (info[0][1]-info[1][1])*((target_index-start_index)/(end_index-start_index))

# models
rf = Roboflow(api_key="AmMUXsxw896FwSFt1GP7")
project = rf.workspace().project("sinotech")
model = project.version(2).model
reader = easyocr.Reader(['en'])

REF_line_list = []
pair_list = []

# Read the pdf file
print('Reading pdf...')
pdfpath=dirpath +"\\"+ "-Layout1_2.pdf"
ref_pdfpath = dirpath +"\\"+ "-Layout1_2_ref.pdf"
img = convert_from_path(pdfpath, dpi=210)
ref_img = convert_from_path(ref_pdfpath, dpi=210)

for image in tqdm(range(len(ref_img))):
  if image in drawing_to_skip:continue
  # find REF line
  cv_img = cv2.cvtColor(np.asarray(ref_img[image]), cv2.COLOR_RGB2BGR)
  img_gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

  _, img_th = cv2.threshold (img_gray, 240, 255, 0)
  filterSize =(4,4)
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)
  img_bhat = cv2.morphologyEx(img_th, cv2.MORPH_BLACKHAT, kernel)
  thinned = cv2.ximgproc.thinning(img_bhat)
  lines, x_index = FLD(thinned, thinned)
  REF_line = lines[check_line(lines,x_index)]
  ls = [(int(REF_line[0,0]), int(REF_line[0,1])), (int(REF_line[0,2]), int(REF_line[0,3]))]
  REF_line_list.append(ls)

for image in tqdm(range(len(img))):
  if image in drawing_to_skip:continue
  
  # find REF line
  cv_img = cv2.cvtColor(np.asarray(img[image]), cv2.COLOR_RGB2BGR)
  img_gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

  _, img_th = cv2.threshold (img_gray, 240, 255, 0)

  # model predict section
  cv2.imwrite("input.jpg", img_th)
  result = model.predict("input.jpg", confidence=40, overlap=30).json()
  r = result['predictions']

  # OCR and check word
  height, width = img_th.shape
  word_check = []
  GL_EL_check = []
  for i in range(4):
    if i == 0:
      cut_img = img_th[0:height//2, 0:width//2]
      bounds = reader.readtext(cut_img, detail=1)
      array = np.array(bounds, dtype=object)
      for w in array:
        if len(w[1]) == 1:
          word_check.append(w)
        if w[1].find('GL') > -1:
          GL_EL_check.append(w)
        if w[1].find('EL') > -1:
          GL_EL_check.append(w)
    elif i == 1:
      cut_img = img_th[0:height//2, width//2:]
      bounds = reader.readtext(cut_img, detail=1)
      array = np.array(bounds, dtype=object)
      for w in array:
        if len(w[1]) == 1:
          w[0][0][0] += (width//2)
          w[0][1][0] += (width//2)
          w[0][2][0] += (width//2)
          w[0][3][0] += (width//2)
          word_check.append(w)

    elif i == 2:
      cut_img = img_th[height//2:, 0:width//2]
      bounds = reader.readtext(cut_img, detail=1)
      array = np.array(bounds, dtype=object)
      for w in array:
        if len(w[1]) == 1:
          w[0][0][1] += (height//2)
          w[0][1][1] += (height//2)
          w[0][2][1] += (height//2)
          w[0][3][1] += (height//2)
          word_check.append(w)
        if w[1].find('EL') > -1:
          w[0][0][1] += (height//2)
          w[0][1][1] += (height//2)
          w[0][2][1] += (height//2)
          w[0][3][1] += (height//2)
          GL_EL_check.append(w)

    else:
      cut_img = img_th[height//2:, width//2:]
      bounds = reader.readtext(cut_img, detail=1)
      array = np.array(bounds, dtype=object)
      for w in array:
        if len(w[1]) == 1:
          w[0][0][1] += (height//2)
          w[0][1][1] += (height//2)
          w[0][2][1] += (height//2)
          w[0][3][1] += (height//2)
          w[0][0][0] += (width//2)
          w[0][1][0] += (width//2)
          w[0][2][0] += (width//2)
          w[0][3][0] += (width//2)
          word_check.append(w)

  # get GL and EL number
  GL_EL_info = []
  for i in range(len(GL_EL_check)):
    if(GL_EL_check[i][1].find('GL')>-1 and len(GL_EL_check[i][1]) < 15):
      if extract_number(GL_EL_check[i][1]) != None:
        GL_num = float(extract_number(GL_EL_check[i][1]))
        GL_EL_info.append([GL_EL_check[i][0],GL_num])
        GL_EL_info.append([GL_EL_check[i][0],GL_num])
      EL_num = GL_num
    if(GL_EL_check[i][1].find('EL')>-1 and len(GL_EL_check[i][1]) < 15):
      if extract_number(GL_EL_check[i][1]) != None:
        temp_EL_num = float(extract_number(GL_EL_check[i][1]))
        if EL_num > temp_EL_num:
          EL_num = temp_EL_num
          GL_EL_info[1] = ([GL_EL_check[i][0],EL_num])

  # pair word and section and pair symbol and section
  symbol_section_pair_list = []
  temp_symbol_pair = []
  temp_section_pair = []

    # 檢查每個symbol跟list對應的文字
  for i in range(len(r)):

    cl = r[i]['class']
    x = int(r[i]['x'])
    y = int(r[i]['y'])
    width = int(r[i]['width']/2)
    height = int(r[i]['height']/2)

    if(cl == 'symbol'):
      temp_symbol_pair.append([i,-1,-1])
      depth = str(get_depth(GL_EL_info,r[i]))

      for l in range(len(word_check)):
        mid_x = (word_check[l][0][0][0] + word_check[l][0][1][0]) / 2
        mid_y = (word_check[l][0][0][1] + word_check[l][0][2][1]) / 2
        if(mid_x > x-width and mid_x < (x+width) and mid_y > y-height and mid_y < (y+height)):
          temp_symbol_pair[len(temp_symbol_pair)-1][1] = word_check[l][1]
          temp_symbol_pair[len(temp_symbol_pair)-1][2] = l

    elif(cl == 'section'):
      temp_section_pair.append([i,-1,-1])
      for l in range(len(word_check)):
        mid_x = (word_check[l][0][0][0] + word_check[l][0][1][0]) / 2
        mid_y = (word_check[l][0][0][1] + word_check[l][0][2][1]) / 2
        if(mid_x > x-width and mid_x < (x+width) and mid_y > y-height and mid_y < (y+height)):
          temp_section_pair[len(temp_section_pair)-1][1] = word_check[l][1]
          temp_section_pair[len(temp_section_pair)-1][2] = l

  try:
    count = 0
    # 先檢查 A、B.....等符號
    for i in range(len(temp_symbol_pair)):
      for k in range(len(temp_section_pair)):
        if(temp_symbol_pair[i][1] == temp_section_pair[k][1]) and temp_symbol_pair[i][1] != -1:
          if(get_depth(GL_EL_info,r[temp_symbol_pair[i][0]]) > 0 and get_depth(GL_EL_info,r[temp_symbol_pair[i][0]]) <  (GL_EL_info[0][1]-GL_EL_info[1][1])):
            x = int(r[temp_section_pair[k][0]]['x'])
            y = int(r[temp_section_pair[k][0]]['y'])
            width = int(r[temp_section_pair[k][0]]['width']/2)
            height = int(r[temp_section_pair[k][0]]['height']/2)
            bboxe = [x-width, y-height, x+width, y+height]

            symbol_section_pair_list.append([bboxe,get_depth(GL_EL_info,r[temp_symbol_pair[i][0]])])
          count+=1
    # 如果剛好剩一個沒有配對到，就預設配對成C
    if len(temp_symbol_pair)-count == 1:
      for i in range(len(temp_symbol_pair)):
        for k in range(len(temp_section_pair)):
          if(temp_symbol_pair[i][1] == -1 and temp_section_pair[k][1]== -1):
            if(get_depth(GL_EL_info,r[temp_symbol_pair[i][0]]) > 0 and get_depth(GL_EL_info,r[temp_symbol_pair[i][0]]) <  (GL_EL_info[0][1]-GL_EL_info[1][1])):
              x = int(r[temp_section_pair[k][0]]['x'])
              y = int(r[temp_section_pair[k][0]]['y'])
              width = int(r[temp_section_pair[k][0]]['width']/2)
              height = int(r[temp_section_pair[k][0]]['height']/2)
              bboxe = [x-width, y-height, x+width, y+height]

              symbol_section_pair_list.append([bboxe,get_depth(GL_EL_info,r[temp_symbol_pair[i][0]])])
              break
    else:
      print("pairing error.")

  except:
    print("pairing error")
  #print(" ")
  #print(temp_symbol_pair)
  #print(temp_section_pair)
  #print(symbol_section_pair_list)
  pair_list.append(symbol_section_pair_list)

# %% [markdown]
# ### **Coordinate Adjustment**
# 

# %%
#coordinate adjustment equation
dwg_coor=dwg_coor
pdf_coor= [[elem for tup in inner for elem in tup] for inner in REF_line_list]
section_depth_pair=pair_list
scale=[]
x_const=[]
y_const=[]
pdf_ncoor=[]
nsection_depth_pair=[]

for i in range(len(pdf_coor)):
    pdf_coor[i][1] = 4912 - pdf_coor[i][1]
    pdf_coor[i][3] = 4912 - pdf_coor[i][3]


for i in range(0,len(dwg_coor)):
    pdf_len=math.sqrt(math.pow(pdf_coor[i][0]-pdf_coor[i][2],2)+math.pow(pdf_coor[i][1]-pdf_coor[i][3],2))
    dwg_len=math.sqrt(math.pow(dwg_coor[i][0]-dwg_coor[i][2],2)+math.pow(dwg_coor[i][1]-dwg_coor[i][3],2))
    scale.append(dwg_len/pdf_len)
    x_const.append(max(dwg_coor[i][0],dwg_coor[i][2])-max(pdf_coor[i][0],pdf_coor[i][2])*scale[i])
    y_const.append(max(dwg_coor[i][1],dwg_coor[i][3])-max(pdf_coor[i][1],pdf_coor[i][3])*scale[i])
    pdf_ncoor.append([
        pdf_coor[i][0]*scale[i]+x_const[i],
        pdf_coor[i][1]*scale[i]+y_const[i],
        pdf_coor[i][2]*scale[i]+x_const[i],
        pdf_coor[i][3]*scale[i]+y_const[i]
    ])

#extract arrow with type info
for i in range(0,len(section_depth_pair)):
    nsection_depth_pair.append([])
    for j in range(len(section_depth_pair[i])):
        pair_y_avg=4912-(section_depth_pair[i][j][0][1]+section_depth_pair[i][j][0][3])/2
        nsection_depth_pair[-1].append([])
        nsection_depth_pair[-1][-1].append([])
        nsection_depth_pair[-1][-1][-1].append(section_depth_pair[i][j][0][0]*scale[i]+x_const[i])
        nsection_depth_pair[-1][-1][-1].append(pair_y_avg*scale[i]+y_const[i])
        nsection_depth_pair[-1][-1][-1].append(section_depth_pair[i][j][0][2]*scale[i]+x_const[i])
        nsection_depth_pair[-1][-1][-1].append(pair_y_avg*scale[i]+y_const[i])
        nsection_depth_pair[-1][-1].append(pair_list[i][j][1])

# %% [markdown]
# ### **Object Grouping**
# 

# %%
#Processed Data Visualization
grouped_helperline_sh=[]
hor_sh_rebar_text=[]
for n,file in enumerate(dwg_helperline_sh):
    fig, ax = plt.subplots()
    color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'skyblue', 'limegreen', 'orange', 'purple']
    hor_sh_rebar_text.append([])
    grouped_helperline_sh.append([])
    check_grouped=[]

    for div, div_line_info in enumerate(nsection_depth_pair[n]):
        grouped_helperline_sh[-1].append([])
        div_start_x, div_start_y = div_line_info[0][0],div_line_info[0][1]
        div_end_x, div_end_y = div_line_info[0][2],div_line_info[0][3]
        sum_x,sum_y=0,0
        for shh, sh_helperline_info in enumerate(file):
            helper_start_x, helper_start_y = sh_helperline_info[3][:2]
            helper_end_x, helper_end_y = sh_helperline_info[4][:2]
            if (helper_start_y+helper_end_y)/2>=(div_start_y+div_end_y)/2 and sh_helperline_info[0] not in check_grouped:
                grouped_helperline_sh[n][-1].append(dwg_helperline_sh[n][shh])
                check_grouped.append(sh_helperline_info[0])
                sum_x+=(helper_start_x+helper_end_x)/2
                sum_y+=(helper_start_y+helper_end_y)/2
        avg_x,avg_y=sum_x/len(grouped_helperline_sh[n][-1]),sum_y/len(grouped_helperline_sh[n][-1])
        ax.plot([avg_x-0.3,avg_x+0.3], [avg_y+0.3, avg_y-0.3], color_list[div%len(color_list)])
        ax.plot([avg_x-0.3,avg_x+0.3], [avg_y-0.3, avg_y+0.3], color_list[div%len(color_list)])
        textbox_distance_list=[]
        for sht,sh_text_info in enumerate(dwg_text_sh[n]):
            check_top_left, check_top_right, check_bottom_left, check_bottom_right = False, False, False, False
            text_start_x, text_start_y = sh_text_info[4][:2]
            text_end_x, text_end_y = sh_text_info[5][:2]
            distance=get_distance([avg_x,avg_y,0],[(text_start_x+text_end_x)/2,(text_start_y+text_end_y)/2,0])
            textbox_distance_list.append([dwg_text_sh[n][sht],distance])
        textbox_distance_list = sorted(textbox_distance_list, key=lambda x: x[1], reverse=False)
        hor_sh_rebar_text[-1].append(textbox_distance_list[0][0])
    
    for div,div_line_info in enumerate(nsection_depth_pair[n]):
        for sh,sh_helperline_info in enumerate(grouped_helperline_sh[n][div]):
            start_x, start_y = sh_helperline_info[3][:2]
            end_x, end_y = sh_helperline_info[4][:2]
            width = abs(start_x - end_x)
            height = abs(start_y - end_y)
            rect = Rectangle((end_x, start_y), width, height, facecolor=color_list[div % len(color_list)])
            ax.add_patch(rect)
        sh_text_info = hor_sh_rebar_text[n][div]
        start_x, start_y = sh_text_info[4][:2]
        end_x, end_y = sh_text_info[5][:2]
        width = abs(start_x - end_x)
        height = abs(start_y - end_y)
        ax.plot([start_x, end_x], [start_y, end_y], color_list[div%len(color_list)])
        ax.plot([end_x, start_x], [start_y, end_y], color_list[div%len(color_list)])
        rect = Rectangle((min(start_x,end_x), min(start_y,end_y)), width, height, facecolor=color_list[div % len(color_list)])
        ax.add_patch(rect)
        ax.plot([div_line_info[0][0], div_line_info[0][2]], [div_line_info[0][1], div_line_info[0][3]], color_list[div%len(color_list)])
    ax.plot([dwg_coor[n][0], dwg_coor[n][2]], [dwg_coor[n][1], dwg_coor[n][3]], 'k')
    ax.plot([pdf_ncoor[n][0], pdf_ncoor[n][2]], [pdf_ncoor[n][1], pdf_ncoor[n][3]], 'k')

    # Show the plot
    #plt.show()
hor_sh_rebar_text = [sorted(sublist, key=lambda x: (x[4][1] + x[5][1]) / 2, reverse=True) for sublist in hor_sh_rebar_text]

# %%
for i,item in enumerate(pair_list):
    for j,jtem in enumerate(item):
        for k,ktem in enumerate(shear_rebar_list[i]):
            if shear_rebar_list[i][k][1]<pair_list[i][j][1]*1000<shear_rebar_list[i][k][2]:
                if len(shear_rebar_list[i][k])==3:
                    shear_rebar_list[i][k].extend([hor_sh_rebar_text[i][j][6],pair_list[i][j][1]])
                elif len(shear_rebar_list[i][k])>=3 and shear_rebar_list[i][k][3]!=hor_sh_rebar_text[i][j][6]:
                    shear_rebar_list[i][k][3]=shear_rebar_list[i][k][3]+" "+hor_sh_rebar_text[i][j][6]
print(shear_rebar_list)

# %% [markdown]
# ## **Check & Save to XML**

# %% [markdown]
# ### **Export to XML** 
# 

# %%
# Check Final Reading Results
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from pathlib import Path
import os

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
    xml_out_DD.write(bytes('<Drawing Description="配筋圖">', 'utf-8'))
    for n,type in enumerate(wall_type_list):
        xml_out_DD.write(bytes("""
        <WorkItemType Description="TYPE """+str(type)+"""">
        <Concrete>
        <Strength Description="混凝土強度" >
        <Value unit="kgf/cm^2" />
        </Strength>
        <Total Description="數量" >
        <Value unit="m2" />
        </Total>
        <Length Description="設計長度" >
        <Value unit="m" />
        </Length>
        <Depth Description="設計深度" >
        <Value unit="m" >"""+str(int(wall_depth_list[n])/1000)+"""</Value>
        </Depth>
        <Thickness Description="厚度" >
        <Value unit="m" >"""+str(int(wall_thick_list[n])/1000)+"""</Value>
        </Thickness>
        </Concrete>
        <HorznRebar Description="水平筋" >""", 'utf-8'))
        for hr, hrzn_rebar_info in enumerate(hori_rebar_list[n]):
            xml_out_DD.write(bytes("""
            <Rebar Description="鋼筋資訊" >
            <Type Description="水平筋設計" >
            <Value unit="mm" >"""+str(hrzn_rebar_info)+"""</Value>
            </Type>
            </Rebar>""", 'utf-8'))
        xml_out_DD.write(bytes("""
        </HorznRebar>

        <VertRebar Description="垂直筋" >
        <Retaining>""", 'utf-8'))
        for vr, vert_rebar_info in enumerate(dwg_vert_rebar_info[n]):
            if "retain" in vert_rebar_info.rebar_side[1:-1].lower():
                xml_out_DD.write(bytes("""
                <Rebar Description="鋼筋資訊" >
                <Type Description="垂直筋設計" >
                <Value unit="mm" >"""+str(vert_rebar_info.rebar_type)+"""</Value>
                </Type>
                <StartDepth Description="開起深度" >
                <Value unit="m" >"""+str(vert_rebar_info.depth_level1)+"""</Value>
                </StartDepth>
                <EndDepth Description="結束深度" >
                <Value unit="m" >"""+str(vert_rebar_info.depth_level2)+"""</Value>
                </EndDepth>
                </Rebar>""", 'utf-8'))
        xml_out_DD.write(bytes("""
        </Retaining>
        <Excavation>""", 'utf-8'))
        for vr, vert_rebar_info in enumerate(dwg_vert_rebar_info[n]):
            if "excavat" in vert_rebar_info.rebar_side[1:-1].lower():
                xml_out_DD.write(bytes("""
                <Rebar Description="鋼筋資訊" >
                <Type Description="垂直筋設計" >
                <Value unit="mm" >"""+str(vert_rebar_info.rebar_type)+"""</Value>
                </Type>
                <StartDepth Description="開起深度" >
                <Value unit="m" >"""+str(vert_rebar_info.depth_level1)+"""</Value>
                </StartDepth>
                <EndDepth Description="結束深度" >
                <Value unit="m" >"""+str(vert_rebar_info.depth_level2)+"""</Value>
                </EndDepth>
                </Rebar>""", 'utf-8'))
        xml_out_DD.write(bytes("""
        </Excavation>
        </VertRebar>

        <ShearRebar Description="剪力筋" >""", 'utf-8'))
        for sr, shear_rebar_info in enumerate(shear_rebar_list[n]):
            if len(shear_rebar_info)>3:
                sv_size,sv_spacing=shear_rebar_info[0].split("@")
                sh_size,sh_spacing=shear_rebar_info[3].split("@")
                xml_out_DD.write(bytes("""
                <Rebar Description="鋼筋資訊" >
                <Type Description="剪力筋設計" >
                <Value unit="mm" >"""+str(sv_size+"Sh "+sh_spacing+"Sv "+sv_spacing)+"""</Value>
                </Type>
                <StartDepth Description="開起深度" >
                <Value unit="m" >"""+str(round(int(shear_rebar_info[1])/1000,1))+"""</Value>
                </StartDepth>
                <EndDepth Description="結束深度" >
                <Value unit="m" >"""+str(round(int(shear_rebar_info[2])/1000,1))+"""</Value>
                </EndDepth>
                </Rebar>""", 'utf-8'))
            else:
                sv_size,sv_spacing=shear_rebar_info[0].split("@")
                xml_out_DD.write(bytes("""
                <Rebar Description="鋼筋資訊" >
                <Type Description="剪力筋設計" >
                <Value unit="mm" >"""+str(sv_size+"Sv "+sv_spacing)+"""</Value>
                </Type>
                <StartDepth Description="開起深度" >
                <Value unit="m" >"""+str(round(int(shear_rebar_info[1])/1000,1))+"""</Value>
                </StartDepth>
                <EndDepth Description="結束深度" >
                <Value unit="m" >"""+str(round(int(shear_rebar_info[2])/1000,1))+"""</Value>
                </EndDepth>
                </Rebar>""", 'utf-8'))
        xml_out_DD.write(bytes("""
        </ShearRebar>
                               
        <RebarProtection Description="鋼筋保護層厚度" >
        <Value unit="mm" >"""+str(rebar_protection_list[n])+"""</Value>
        </RebarProtection>

        </WorkItemType>""", 'utf-8'))
    xml_out_DD.write(bytes('</Drawing></File></WorkItem>', 'utf-8'))
    xml_out_DD.close()

    #Remove Double in XML
    with open(xmlfname, 'rb') as f:
        lines = f.readlines()
        target=bytes('</File></WorkItem><WorkItem><File Description="設計圖說">', 'utf-8')
        repget_head=bytes('<Drawing Description="配筋圖">', 'utf-8')
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

def show_dwg_file(event):
    global drawing_number, wall_type_list, wall_depth_list, wall_thick_list, hori_rebar_list, dwg_vert_rebar_info, shear_rebar_list, rebar_protection_list
    selected_file = select_dwg_combobox.get()
    drawing_number = [filename for f,filename in enumerate(dwgfname) if f not in drawing_to_skip].index(selected_file)

    # Modify Label
    wall_type_label.config(text="Wall Type = "+str(wall_type_list[drawing_number]))
    wall_depth_label.config(text="Wall Depth = "+str(round(int(wall_depth_list[drawing_number])/1000,1))+" m")
    wall_thickness_label.config(text="Wall Thickness = "+str(round(int(wall_thick_list[drawing_number])/1000,1))+" m")
    rebar_protection_label.config(text="Rebar Protection = "+str(rebar_protection_list[drawing_number])+" mm")

    #Modify Listbox
    hori_rebar_listbox.delete(0, tk.END)
    table_data = "| {:^81s} |".format("Rebar Type")
    hori_rebar_listbox.insert(tk.END, table_data)
    for rebar in hori_rebar_list[drawing_number]:
        table_data = "| {:^81s} |".format(str(rebar))
        hori_rebar_listbox.insert(tk.END, table_data)
    
    vert_rebar_listbox.delete(0, tk.END)
    table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format("Rebar Type", "Rebar Side", "Start Depth (m)", "End Depth (m)")
    vert_rebar_listbox.insert(tk.END, table_data)
    for rebar in dwg_vert_rebar_info[drawing_number]:
        table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format(rebar.rebar_type, rebar.rebar_side[1:-1], str(rebar.depth_level1), str(rebar.depth_level2))
        vert_rebar_listbox.insert(tk.END, table_data)

    shear_rebar_listbox.delete(0, tk.END)
    table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format("Rebar Type (Hor.)","Rebar Type (Vert.)", "Start Depth (m)", "End Depth (m)")
    shear_rebar_listbox.insert(tk.END, table_data)
    for rebar in shear_rebar_list[drawing_number]:
        try:sh_size=str(rebar[3])
        except:sh_size="-"
        table_data = "| {:^18s} | {:^18s} | {:^18s} | {:^18s} |".format(sh_size, str(rebar[0]), str(round(int(rebar[1])/1000,1)), str(round(int(rebar[2])/1000,1)))
        shear_rebar_listbox.insert(tk.END, table_data)

downloads_path = str(Path.home() / "Downloads")
xmlfname = os.path.join(downloads_path, "Result.xml")
drawing_number = 0

window = tk.Tk()
window.title("Reading Results")

menu_frame = tk.Frame(window)
menu_frame.pack(side=tk.TOP, padx=(10,20), pady=20)

# Create a frame for select dwg
select_dwg_frame = tk.Frame(menu_frame)
select_dwg_frame.pack()

# Create a label for displaying "Select DWG File"
select_dwg_label = tk.Label(select_dwg_frame, text="Select DWG :", font=("Arial", 14))
select_dwg_label.pack(side=tk.LEFT,pady=0)

# Create a combobox (dropdown menu) widget
select_dwg_combobox = ttk.Combobox(select_dwg_frame, values=[filename for f,filename in enumerate(dwgfname) if f not in drawing_to_skip])
select_dwg_combobox.bind("<<ComboboxSelected>>", show_dwg_file)
select_dwg_combobox.pack(side=tk.LEFT,pady=0, padx=(0, 0))

# Create a label for displaying "Plan/Elevation Drawing"
drawing_type_label = tk.Label(menu_frame, text="Drawing Type : Rebar Drawings", font=("Arial", 14))
drawing_type_label.pack(pady=0)

# Create frame for wall type menu
wall_type_frame = tk.Frame(menu_frame)
wall_type_frame.pack()

# Create a label for displaying "Wall Type"
wall_type_label = tk.Label(wall_type_frame, text="Wall Type = "+str(wall_type_list[drawing_number]), font=("Arial", 14), fg="blue")
wall_type_label.pack(side=tk.LEFT,pady=0)

# Create a label for displaying "Wall Depth"
wall_depth_label = tk.Label(menu_frame, text="Wall Depth = "+str(round(int(wall_depth_list[drawing_number])/1000,1))+" m", font=("Arial", 14), fg="blue")
wall_depth_label.pack(pady=0)

# Create a label for displaying "Wall Thickness"
wall_thickness_label = tk.Label(menu_frame, text="Wall Thickness = "+str(round(int(wall_thick_list[drawing_number])/1000,1))+" m", font=("Arial", 14), fg="blue")
wall_thickness_label.pack(pady=0)

# Create a label for displaying "Rebar Protection"
rebar_protection_label = tk.Label(menu_frame, text="Rebar Protection = "+str(rebar_protection_list[drawing_number])+" mm", font=("Arial", 14), fg="blue")
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
save_xml_button = tk.Button(menu_frame, text="Save XML File", command=save_xml_file)
save_xml_button.pack(pady=(5,0), padx=(0, 0))

# Show the first dwg
select_dwg_combobox.current(0)
select_dwg_combobox.event_generate("<<ComboboxSelected>>")

# Run the Tkinter event loop
window.mainloop()

# %%
# Remove redundant files

os.remove(dirpath +"\\"+ "-Layout1.pdf")
os.remove(dirpath +"\\"+ "Vertical Line Info.csv")
os.remove(dirpath +"\\"+ "Helper Line Info.csv")
os.remove(dirpath +"\\"+ "Text Info.csv")
os.remove(dirpath +"\\"+ "PUBLIST.dsd")
os.remove(dirpath +"\\"+ "-Layout1_2.pdf")
os.remove(dirpath +"\\"+ "-Layout1_2_ref.pdf")
os.remove(dirpath +"\\"+ "SH Line Info.csv")
os.remove(dirpath +"\\"+ "SH Helper Line Info.csv")
os.remove(dirpath +"\\"+ "SH Text Info.csv")
os.remove(dirpath +"\\"+ "PUBLIST_2.dsd")
os.remove(dirpath +"\\"+ "PUBLIST_3.dsd")

# %% [markdown]
# ### **Export to EXE** 

# %%
"""
1. Type : >Export to Python Script in search bar
2. Open CMD in the file folder
3. Type ：
pip install pyinstaller
pyinstaller --onefile "Data Process - Rebar Drawings.py" -w
pyinstaller -F "Data Process - Rebar Drawings.py" --collect-all easyocr
"""


