# %% [markdown]
# ### **Import Module, Define Class, & Define Function**

# %%
#Import Module
import os
import sys
import keyboard
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
import csv
import math
import numpy as np
import copy as copy
from operator import itemgetter
from itertools import chain
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


#Define Wall claas
class wall_elev:
  def __init__(self,line):
    length=[]
    thickness=[]
    gradient=[]
    x_coor=[]
    y_coor=[]
    for i in line:
      for j in line:
        rounded_thickness=round(l2l_CD(np.array(i[4][:2]+i[3][:2]),np.array(j[4][:2]+j[3][:2])),1)
        if i!=j and rounded_thickness!=0.0:thickness.append(rounded_thickness)
      length.append(i[2])
      gradient.append(i[5])
      x_coor.append([i[3][0],i[3][1]])
      x_coor.append([i[4][0],i[4][1]])
      y_coor.append([i[3][0],i[3][1]])
      y_coor.append([i[4][0],i[4][1]])
    self.length=max(length)
    self.thickness=list(set(thickness))
    self.gradient=sum(gradient)/len(gradient)
    self.side_number=len(line)
    self.line_member=line
    x_coor.sort(key=itemgetter(0),reverse=False)
    y_coor.sort(key=itemgetter(1),reverse=False)
    self.coor=[x_coor[0][0],y_coor[-1][1],x_coor[-1][0],y_coor[0][1]]
    self.type=None
  def __str__(self):
    return f"wall_elev with length={self.length}, thickness={self.thickness}, type={self.type}, gradient={self.gradient} , and {self.side_number} sides"
  def setType(self,type):
    self.type=type
  def addLine(self,addedline):
    line=self.line_member
    line.append(addedline)
    length=[]
    thickness=[]
    gradient=[]
    x_coor=[]
    y_coor=[]
    for i in line:
      for j in line:
        rounded_thickness=round(l2l_CD(np.array(i[4][:2]+i[3][:2]),np.array(j[4][:2]+j[3][:2])),1)
        if i!=j and rounded_thickness!=0.0:thickness.append(rounded_thickness)
      length.append(i[2])
      gradient.append(i[5])
      x_coor.append([i[3][0],i[3][1]])
      x_coor.append([i[4][0],i[4][1]])
      y_coor.append([i[3][0],i[3][1]])
      y_coor.append([i[4][0],i[4][1]])
    self.length=max(length)
    self.thickness=list(set(thickness))
    self.gradient=sum(gradient)/len(gradient)
    self.side_number=len(line)
    self.line_member=line
    x_coor.sort(key=itemgetter(0),reverse=False)
    y_coor.sort(key=itemgetter(1),reverse=False)
    self.coor=[x_coor[0][0],y_coor[-1][1],x_coor[-1][0],y_coor[0][1]]
  def removeLine(self,removedline):
    line=self.line_member
    line.remove(removedline)
    length=[]
    thickness=[]
    gradient=[]
    x_coor=[]
    y_coor=[]
    for i in line:
      for j in line:
        rounded_thickness=round(l2l_CD(np.array(i[4][:2]+i[3][:2]),np.array(j[4][:2]+j[3][:2])),1)
        if i!=j and rounded_thickness!=0.0:thickness.append(rounded_thickness)
      length.append(i[2])
      gradient.append(i[5])
      x_coor.append([i[3][0],i[3][1]])
      x_coor.append([i[4][0],i[4][1]])
      y_coor.append([i[3][0],i[3][1]])
      y_coor.append([i[4][0],i[4][1]])
    self.length=max(length)
    self.thickness=list(set(thickness))
    self.gradient=sum(gradient)/len(gradient)
    self.side_number=len(line)
    self.line_member=line
    x_coor.sort(key=itemgetter(0),reverse=False)
    y_coor.sort(key=itemgetter(1),reverse=False)
    self.coor=[x_coor[0][0],y_coor[-1][1],x_coor[-1][0],y_coor[0][1]]

# %%
#define Function
def rotate_coor(x0,y0,angle): #angle in degree
    angle1=math.radians(angle)
    x1=x0*math.cos(angle1)-y0*math.sin(angle1)
    y1=x0*math.sin(angle1)+y0*math.cos(angle1)
    return [x1,y1]

def check_mergeable(raw_line1, raw_line2):
    #rotate all line to be m=0
    tetha1,tetha2=0,0
    if (raw_line1[0]-raw_line1[2])!=0:
        tetha1=math.atan((raw_line1[1]-raw_line1[3])/(raw_line1[0]-raw_line1[2]))*180/math.pi
    else: tetha1=90
    if (raw_line2[0]-raw_line2[2])!=0:
        tetha2=math.atan((raw_line2[1]-raw_line2[3])/(raw_line2[0]-raw_line2[2]))*180/math.pi
    else: tetha2=90
    line1=rotate_coor(raw_line1[0],raw_line1[1],-tetha1)+rotate_coor(raw_line1[2],raw_line1[3],-tetha1)
    line2=rotate_coor(raw_line2[0],raw_line2[1],-tetha2)+rotate_coor(raw_line2[2],raw_line2[3],-tetha2)

    if line1[1]==line2[1] or line1[3]==line2[3] or line1[1]==line2[3] or line1[3]==line2[1]:
        combination = np.array([line1,line2,
                         [line1[0], 0, line2[0], 0],
                         [line1[0], 0, line2[2], 0],
                         [line1[2], 0, line2[0], 0],
                         [line1[2], 0, line2[2], 0]])
        distance = np.sqrt((combination[:,0] - combination[:,2])**2 + (combination[:,1] - combination[:,3])**2)
        max = np.amax(distance)
        overlap = distance[0] + distance[1] - max
        endpoint = combination[np.argmax(distance)]
        return (overlap >= 0)#True or false
    else: return False

def check_overlap(raw_line1, raw_line2):
    #rotate all line to be m=0
    tetha1,tetha2=0,0
    if (raw_line1[0]-raw_line1[2])!=0:
        tetha1=math.atan((raw_line1[1]-raw_line1[3])/(raw_line1[0]-raw_line1[2]))*180/math.pi
    else: tetha1=90
    if (raw_line2[0]-raw_line2[2])!=0:
        tetha2=math.atan((raw_line2[1]-raw_line2[3])/(raw_line2[0]-raw_line2[2]))*180/math.pi
    else: tetha2=90
    line1=rotate_coor(raw_line1[0],raw_line1[1],-tetha1)+rotate_coor(raw_line1[2],raw_line1[3],-tetha1)
    line2=rotate_coor(raw_line2[0],raw_line2[1],-tetha2)+rotate_coor(raw_line2[2],raw_line2[3],-tetha2)

    combination = np.array([line1,line2,
                         [line1[0], 0, line2[0], 0],
                         [line1[0], 0, line2[2], 0],
                         [line1[2], 0, line2[0], 0],
                         [line1[2], 0, line2[2], 0]])
    distance = np.sqrt((combination[:,0] - combination[:,2])**2 + (combination[:,1] - combination[:,3])**2)
    max = np.amax(distance)
    overlap = distance[0] + distance[1] - max
    endpoint = combination[np.argmax(distance)]
    return (overlap > 0), endpoint

def l2l_CD(line1, line2):
    if (line1[0]-line1[2])!=0:
        m1=(line1[1]-line1[3])/(line1[0]-line1[2])
        m2=(line2[1]-line2[3])/(line2[0]-line2[2])
        b1=line1[1]-m1*line1[0]
        b2=line2[1]-m2*line2[0]
        return abs(b2-b1)/math.sqrt(m1*m1+1)
    else: return abs(line1[0]-line2[0])
    
def CheckRectangleOverlap(R1, R2):
    if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]>=R2[1]) or (R1[1]<=R2[3]):
        return False
    else:
        return True

# %% [markdown]
# ### **PDF OCR**

# %%
#Read PDF
import cv2
import numpy as np
from pdf2image import convert_from_path
# import PIL
# from PIL import ImageDraw, Image
import easyocr
# import os 
from tqdm import tqdm

# some functions

def FLD(image,drawimage):
    # Create default Fast Line Detector class
    fld = cv2.ximgproc.createFastLineDetector()
    # Get line vectors from the image
    lines = fld.detect(image)
    # Draw lines on the image
    line_on_image = fld.drawSegments(drawimage, lines)

    return lines

def check_line(lines):
  dist = 1000000000000000
  record = 0
  for i in range(len(lines)):
    line = lines[i]
    head_x = line[0,0]
    head_y = line[0,1]
    end_x = line[0,2]
    end_y = line[0,3]
    if (end_x - head_x)**2 < (end_y - head_y)**2: #### here
      if (head_x-0)**2 + (head_y)**2 < dist and abs(head_y - end_y) > 300:
        dist = (head_x-0)**2 + (head_y)**2
        record = i
  return record

dirpath=" ".join(sys.argv[1:])
pdfname="-Layout1.pdf"
pdfpath = dirpath+"\\"+pdfname

# read pdf and convert pdf to image
imgs = convert_from_path(pdfpath,dpi=300,fmt='jpeg') # for type detection
# img_REF = convert_from_path('/content/drive/MyDrive/Lab/中興/測試圖檔/pdf/1440.pdf',dpi=220,fmt='jpeg') # for refernce line

# setup ocr reader
reader = easyocr.Reader(['ch_tra','en'])

# the list for final_output
final_ls = []

# just for temporary data storing
REF_ls = []
Wall_type_ls=[]

# # get REF 
# for i in range(len(img_REF)):
#   img = cv2.cvtColor(np.asarray(img_REF[i]),cv2.COLOR_RGB2BGR)
#   # Gray Scaling
#   img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#   # Multilevel Thresholding -- OTSU method
#   ret, th = cv2.threshold(img_gray , 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#   # Morphological Operation -- Black Hat
#   filterSize =(6,6) 
#   kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)
#   img_bhat = cv2.morphologyEx(th, cv2.MORPH_BLACKHAT, kernel)
#   # line thinning
#   thinned = cv2.ximgproc.thinning(img_bhat)
#   # get all the lines in the image
#   lines = FLD(thinned, thinned)

#   REF_line = lines[check_line(lines)]
#   ls = [float(REF_line[0,0]), float(REF_line[0,1]), float(REF_line[0,2]), float(REF_line[0,3])]

#   REF_ls.append(ls)

# for wall type
for i in tqdm(range(len(imgs))):

  img = cv2.cvtColor(np.asarray(imgs[i]),cv2.COLOR_RGB2BGR)

  # Gray Scaling
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  # Multilevel Thresholding -- OTSU method
  ret, th = cv2.threshold(img_gray , 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
  
  # Morphological Operation -- Black Hat                             #####  1. start here
  filterSize =(4,4)
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)
  img_bhat = cv2.morphologyEx(th, cv2.MORPH_BLACKHAT, kernel)

  # Substract Origin
  img_invers = cv2.bitwise_not(th)
  img_sub = img_invers - img_bhat

  # Additional Morphological Operations -- Erosion, Dilation 
  kernel2 = np.ones((4, 4))  
  kernel3 = np.ones((5, 5))  

  img_erode = cv2.erode(img_sub, kernel2, iterations=1)

  img_dilate = cv2.dilate(img_erode, kernel3, iterations=1)

  contours_b, hierarchy_b = cv2.findContours(img_dilate, cv2.RETR_LIST , cv2.CHAIN_APPROX_NONE)  #####  1. end here

  # ocr
  bounds = reader.readtext(imgs[i], detail=1)
#   array = np.array(bounds)

  for bound in bounds:
    try:
      p0, p1, p2, p3 = bound[0] # get coordinates
      white = cv2.rectangle(th, p0, p2, color=(255,255,255), thickness =-1)
      white_wall = cv2.rectangle(img, p0, p2, color=(255,255,255), thickness = -1)
    except:pass

  # Gray Scaling
  img_gray = cv2.cvtColor(white_wall, cv2.COLOR_BGR2GRAY)

  # Multilevel Thresholding -- OTSU method
  ret, th = cv2.threshold(img_gray , 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

  # Morphological Operation -- Black Hat
  filterSize =(6,6) # (4,4)for dpi = 300, (2,2) for dpi = 200 (6,6) for filter dpi=300
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)

  img_bhat = cv2.morphologyEx(th, cv2.MORPH_BLACKHAT, kernel)

  # line thinning
  thinned = cv2.ximgproc.thinning(img_bhat)
  # get all the lines in the image
  lines = FLD(thinned, thinned)

  # get the most top and left (will return the line index)
  REF_line = lines[check_line(lines)]
  ls = [float(REF_line[0,0]), float(REF_line[0,1]), float(REF_line[0,2]), float(REF_line[0,3])]

  REF_ls.append(ls)

  contours_a, hierarchy_a = cv2.findContours(white, cv2.RETR_LIST , cv2.CHAIN_APPROX_NONE)

  check_arrow = []                                          ####  2. and start here
  for i in range(len(contours_b)):
    x, y, w, h = cv2.boundingRect(contours_b[i])
    for w in range(len(contours_a)-1):
      x1, y1, w1, h1 = cv2.boundingRect(contours_a[w])
      if x1 < x and (x1+w1) > x and  y1 < y and (y1+h1)> y1:
        check_arrow.append(w)                                  #### 2. end here

  # pairing arrow and word
  check = []
#   for j in range(len(bounds[:,1])): 原本的code
  for j in range(len(bounds)):
    if (bounds[j][1].upper()).find('PE') > -1:
      check.append(j)
  pair = np.zeros((len(check),2))

  for count,i in enumerate(check):
    p0, p1, p2, p3 = bounds[i][0]
    dis = 10000000000
    for k in check_arrow:                                   #### 3. and this line 
      x,y,w,h = cv2.boundingRect(contours_a[k])                 
      if (p0[0]-x)**2 + (p0[1]-y)**2 < dis:
        dis = (p0[0]-x)**2 + (p0[1]-y)**2
        pair[count,0] = i
        pair[count,1] = k

  # store wall type
  wall_type = []
  for i in check:
    string = bounds[i][1]
    for j,k in enumerate(string):
      if k == ' ' :
        want_string = string[j+1:len(string)]
    wall_type.append(want_string)

  ls = []
  for index,i in enumerate(pair):

    word = int(i[0])
    arrow  = int(i[1])
    p0, p1, p2, p3 = bounds[word][0]
    x,y,w,h = cv2.boundingRect(contours_a[arrow])

    lss = [x, y, x+w, y+h, p0[0], p0[1], p2[0], p2[1], wall_type[index]]
    ls.append(lss)

  Wall_type_ls.append(ls)

# set final output
for i in range(len(imgs)):
  REF_wall_type = [REF_ls[i], Wall_type_ls[i]]
  final_ls.append(REF_wall_type)


# %% [markdown]
# ### **Import CSV**

# %%
#import CSV
csvpath=dirpath +"\\"+ "Line Info.csv"
linfo=[]
with open(csvpath, newline='') as f:
    linfo = list(csv.reader(f))
    del linfo[0]
    for i in linfo:
      i[1]=i[1][14:-1]
      i[3]=float(i[3])
      i[4]=i[4][1:-1].split()
      for j in range(3): i[4][j]=float(i[4][j])
      i[5]=i[5][1:-1].split()
      for j in range(3): i[5][j]=float(i[5][j])
      if i[5][0]-i[4][0]!=0:
        i[6]=math.atan((i[5][1]-i[4][1])/(i[5][0]-i[4][0]))*180/math.pi
      else:i[6]=90
print("linfo: [0] File Name, [1] Entity Name, [2] Layer Name, [3] Line Length, [4] Start Coor, [5] End Coord, [6] Line Gradient")

# %% [markdown]
# ### **Data Pre-Process**

# %%
#Data Pre-Process
dwgfname= sorted(list(set(i[0] for i in linfo)))
dwgftype=[]
dwgfline=[]
for i in dwgfname:
    dwgfline.append([])
    for j in linfo:
        if i == j[0]:
            dwgfline[-1].append(j[1:])
    dwgftype.append("Elevation Drawings")
print("dwgfline[file name]: [0] Entity Name, [1] Layer Name, [2] Line Length, [3] Start Coor, [4] End Coord, [5] Line Gradient")
if len(dwgfline)!= len(imgs):
    raise Exception("Inconsistent DWG file number in CSV and PDF")

# %%
#check mergeable
import matplotlib.pyplot as plt
import numpy as np
colormap=['b-','g-','r-','c-','m-','b-.','g-.','c-.','r-.','m-.','b--','g--','r--','c--','m--']
mergeable_line=[]
for i in range(1,len(dwgfline)):
    for j in range(0,len(dwgfline[i])):
        for k in range(j+1,len(dwgfline[i])):
            line1=dwgfline[i][j][4][:2]+dwgfline[i][j][3][:2]
            line2=dwgfline[i][k][4][:2]+dwgfline[i][k][3][:2]
            if check_mergeable(line1,line2):
                mergeable_line.append(line1)
                mergeable_line.append(line2)
                x_values1 = [line1[0],line1[2]]
                x_values2 = [line2[0],line2[2]]
                y_values1 = [line1[1],line1[3]]
                y_values2 = [line2[1],line2[3]]
                plt.plot(x_values1,y_values1,colormap[k%len(colormap)])
                plt.plot(x_values2,y_values2,colormap[k%len(colormap)])
                print(j,dwgfline[i][j][0],dwgfline[i][k][0])
#plt.show() 

# %% [markdown]
# ### **Line Grouping Algorithm**

# %%
#Line Grouping Algorithm
dwgfile=[]
for i in range(0,len(dwgfline)):
    dwgfile.append([dwgfname[i],dwgftype[i]]) #set the dwg file name and drawing type as the first 2 elements
    recorded_line=[] #record the line that has find their couple(s) in the file
    dwgfline[i].sort(key=itemgetter(2),reverse=True)
    i=dwgfline[i]
    for j in range(len(i)):
        gradient_tolerance=10 #give some tolerance when comparing gradient
        comparison_list=[]
        shortest_distance=0
        shortest_group=[i[j]] #add the line that is nearest to j
        for k in range(len(i)):
            if j!=k and i[j][0] not in recorded_line and i[k][0] not in recorded_line:
                if i[k][5]-gradient_tolerance<=i[j][5]<=i[k][5]+gradient_tolerance: #check gradient
                    line1=i[j][4][:2]+i[j][3][:2]
                    line2=i[k][4][:2]+i[k][3][:2]
                    ep2ep_dist=[]
                    for m in range(3,5):
                        for n in range(3,5):
                            ep2ep_dist.append(math.sqrt(math.pow((i[j][m][0]-i[k][n][0]),2)+math.pow((i[j][m][1]-i[k][n][1]),2)))
                    if i[j][2]<i[k][2] and round(min(ep2ep_dist),2)==0:
                        continue
                    if check_overlap(line1,line2)[0]: #check overlap
                        comparison_list.append([i[j],i[k],l2l_CD(line1,line2)]) #calculate distance 
        for k in comparison_list:
            if  k[2]!=None:
                if  shortest_distance==0 or k[2]<shortest_distance:
                    shortest_distance=k[2]
        for k in comparison_list:
            if k[2]==shortest_distance:
                shortest_group.append(k[1])
                recorded_line.append(k[1][0])
        if len(shortest_group)>1: #check_shortest distance
            recorded_line.append(i[j][0])
            if dwgftype[dwgfline.index(i)]=="Elevation Drawings":
                wall=wall_elev(shortest_group) 
                dwgfile[-1].append(wall)

# %%
#Search for ungrouped line
all_grouped_line=[]
no_group_line=[]
for i in range(0,len(dwgfile)):
    all_grouped_line.append([])
    no_group_line.append([])
    for j in (dwgfile[i][2:]):
        for line in j.line_member:
            all_grouped_line[i].append(line)
    for k in dwgfline[i]:
        if k in all_grouped_line[i]:
            continue
        else:
            no_group_line[i].append(k)
            print(k)
    if len(no_group_line[i])>0:
        print(len(no_group_line[i]))
    else:print("All wall grouped")

#Add the Ungrouped Line
gradient_tolerance=10
dist_tolerance=0.01
for i in range(0,len(dwgfile)):
    for j in dwgfile[i][2:]:
        for k in j.line_member:
            for l in no_group_line[i]:
                if l[5]-gradient_tolerance<=k[5]<=l[5]+gradient_tolerance:
                    line1=k[4][:2]+k[3][:2]
                    line2=l[4][:2]+l[3][:2]
                    ep2ep_dist=[]
                    for m in range(3,5):
                        for n in range(3,5):
                            ep2ep_dist.append(math.sqrt(math.pow((k[m][0]-l[n][0]),2)+math.pow((k[m][1]-l[n][1]),2)))
                    if round(min(ep2ep_dist),2)<=round(max(j.thickness),2):
                        j.addLine(l)
                        print(l[0],j,ep2ep_dist,max(j.thickness))
                        no_group_line[i].remove(l)
                        continue


# %% [markdown]
# ### **Line and Text Coordinate Adjustment**

# %%
#import pdf coor
pdf_coor,arrowtype,wall_type=[],[],[]

#check ocr
for i,iitem in enumerate(final_ls):
  for j,jitem in enumerate(iitem[1]):
      if final_ls[i][1][j][8][0]=="5":
          temp_ls=list(final_ls[i][1][j][8])
          temp_ls[0]="S"
          final_ls[i][1][j][8]="".join(temp_ls)
      if final_ls[i][1][j][8][1]=="l" or final_ls[i][1][j][8][1]=="_":
          temp_ls=list(final_ls[i][1][j][8])
          temp_ls[1]="1"
          final_ls[i][1][j][8]="".join(temp_ls)

#coordinate import
for i,iitem in enumerate(final_ls):
    pdf_coor.append(iitem[0])
    arrowtype.append(iitem[1])
    wall_type.append([])
    for j,jitem in enumerate(pdf_coor[-1]):
      if j%2==0:
        pdf_coor[-1][j]=float(pdf_coor[-1][j]) 
      elif j%2==1:
        pdf_coor[-1][j]=3509-float(pdf_coor[-1][j]) #3509 == number of pixely axis when converting pdf to png
    for j,jitem in enumerate(arrowtype[-1]):
      for k,kitem in enumerate(jitem[:-1]):
        if k%2==0:
          jitem[k]=float(jitem[k]) 
        elif k%2==1:
          jitem[k]=3509-float(jitem[k]) #3509 == number of pixely axis when converting pdf to png
      wall_type[-1].append(jitem[-1].upper())
    wall_type[-1]=sorted(list(set(wall_type[-1])))

# %%
#import dwg coor
dwg_coor=[]
for i in range(0,len(dwgfline)):
    dwgfline[i].sort(key=itemgetter(4,3),reverse=False)
    max_height=[0,max(dwgfline[i][0][3][1],dwgfline[i][0][4][1])]
    for j in range(len(dwgfline[i])):
        if min(dwgfline[i][j][3][0],dwgfline[i][j][4][0]) == min(dwgfline[i][0][3][0],dwgfline[i][0][4][0]):
            if dwgfline[i][j][3][1] > max_height[1] or dwgfline[i][j][4][1] > max_height[1]:
                max_height=[j,max(dwgfline[i][j][3][1],dwgfline[i][j][4][1])]
        else : break
    ref_line=dwgfline[i][max_height[0]]
    dwg_coor.append([ref_line[3][0],ref_line[3][1],ref_line[4][0],ref_line[4][1]])

# %%
#coordinate adjustment equation
scale=[]
x_const=[]
y_const=[]
pdf_ncoor=[]
narrowtype=[]

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
for i in range(0,len(arrowtype)):
    narrowtype.append([])
    for j in range(len(arrowtype[i])):
        narrowtype[-1].append([])
        narrowtype[-1][-1].append(arrowtype[i][j][0]*scale[i]+x_const[i])
        narrowtype[-1][-1].append(arrowtype[i][j][1]*scale[i]+y_const[i])
        narrowtype[-1][-1].append(arrowtype[i][j][2]*scale[i]+x_const[i])
        narrowtype[-1][-1].append(arrowtype[i][j][3]*scale[i]+y_const[i])
        narrowtype[-1][-1].append(arrowtype[i][j][8].upper())

#assign type to line group
for i in range(0,len(dwgfile)): 
    for j in dwgfile[i][2:]:
        for k in narrowtype[i]:
            if CheckRectangleOverlap(j.coor,k[:-1]):
                j.setType(k[-1])
                continue
            else: pass

# %% [markdown]
# ### **Calculate Depth and Thickness**

# %%
#Calculate and print result
all_wall_thickness={}
all_wall_height={}
def calc_result():
    global dwgfile,all_wall_thickness,all_wall_height
    all_wall_thickness={}
    all_wall_height={}
    for f in dwgfile:
        if f[1] == "Elevation Drawings":
            for wall in f[2:]:
                if 80 < wall.gradient < 100:
                    try:all_wall_height[wall.type].append(wall.length)
                    except:all_wall_height[wall.type]=[wall.length]
                    try:all_wall_thickness[wall.type].extend(wall.thickness)
                    except:all_wall_thickness[wall.type]=copy.copy(wall.thickness)
    print("Wall depth for each type :")
    for type in all_wall_height:
        all_wall_height[type] = [round(x, 2) for x in all_wall_height[type] if x != 0]  # Round to 2 decimal places and remove zero values
        all_wall_height[type] = list(set(all_wall_height[type])) # Remove duplicate elements
        print("wall_type "+str(type)+" / "+"wall_depth="+str(all_wall_height[type])[1:-1])
        if len(all_wall_height[type])>1:print("There is an inconsistency in the depth of wall type "+str(type)+", please check it on the window")
    print("Wall thickness for each type :")
    for type in all_wall_thickness:
        all_wall_thickness[type] = [round(x, 2) for x in all_wall_thickness[type] if x != 0]  # Round to 2 decimal places and remove zero values
        all_wall_thickness[type] = list(set(all_wall_thickness[type])) # Remove duplicate elements
        print("wall_type "+str(type)+" / "+"wall_thickness="+str(all_wall_thickness[type])[1:-1])
        if len(all_wall_thickness[type])>1:print("There is an inconsistency in the thickness of wall type "+str(type)+", please check it on the window")
    return all_wall_thickness, all_wall_height
all_wall_thickness, all_wall_height = calc_result()

#%%
# Check Final Reading Results Part 1

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from pathlib import Path
import os
from matplotlib.path import Path as Polygon
from scipy.spatial import ConvexHull

downloads_path = str(Path.home() / "Downloads")
xmlfname = os.path.join(downloads_path, "Result.xml")
jpglayout = os.path.join(downloads_path, "Elevation_Layout.jpg")

drawing_number = 0
dwgfname = [f[0] for f in dwgfile]
box_color = ["black", "red", "green", "blue", "purple", "orange", "dimgrey", "olive", "magenta", "mediumslateblue", "brown", "darkturquoise", "violet"]
selected_wall=[]

wall_type_color_check=[None]
for drawings_number in range(0,len(dwgfile)):
    fsource=dwgfile[drawings_number]
    for i in fsource[2:]:
        for j in i.line_member:
            x_values = [j[4][0],j[3][0]]
            y_values = [j[4][1],j[3][1]]
            if i.type == None:
               pass
            elif i.type not in wall_type_color_check:
                wall_type_color_check.append(i.type)
            elif i.type in wall_type_color_check:
                pass
wall_type_color_check.sort(key=lambda x: (x is not None, str(x) if x is not None else ""))

import xml.etree.ElementTree as ET
from lib.utils import create_or_read_xml, check_attribute_exists
def save_xml_file(file_path):
    global all_wall_thickness, all_wall_height

    tree, root = create_or_read_xml(file_path)

    # 檢查是否有plans子節點，若無則創建，若有則刪除
    evals = root.find(".//Drawing[@description='立面圖']")
    if evals is None:
        evals = ET.SubElement(root, "Drawing", description="立面圖")

    all_wall_type= list(set(all_wall_thickness.keys()) | set(all_wall_height.keys()))
    all_wall_type=sorted(all_wall_type, key=lambda x: (x is None, x or float('inf')))

    for type in all_wall_type:
        try:
            depth = all_wall_height[type]
        except:
            depth=[0]
        try:
            thickness = all_wall_thickness[type]
        except:
            thickness=[0]
        if depth==[0] and thickness==[0]:
            continue

        if check_attribute_exists(evals, "description", "TYPE "+str(type)):
            continue

        # create a new WorkItemType element
        WorkItemType = ET.SubElement(evals, "WorkItemType", description="TYPE "+str(type))
            # Create a new DiaphragmWall element
        DiaphragmWall = ET.SubElement(WorkItemType, "DiaphragmWall", description="連續壁")
            # Create a new Concrete element
        concrete = ET.SubElement(DiaphragmWall, "Concrete")
                    # Create a new Strength element
        strength = ET.SubElement(concrete, "Strength", description="混凝土強度")
        strength_value = ET.SubElement(strength, "Value", unit="kgf/cm^2")
                    # Create a new Total element
        total = ET.SubElement(concrete, "Total", description="數量")
        total_value = ET.SubElement(total, "Value", unit="m2")
                # Create a new Length element
        length_element = ET.SubElement(DiaphragmWall, "Length", description="行進米")
        length_value = ET.SubElement(length_element, "Value", unit="m")
                # Create a new Depth element
        depth_element = ET.SubElement(DiaphragmWall, "Depth", description="設計深度")
        depth_value = ET.SubElement(depth_element, "Value", unit="m")
        depth_value.text = str(depth)[1:-1]
                # Create a new Thickness element
        thickness_element = ET.SubElement(DiaphragmWall, "Thickness", description="厚度")
        thickness_value = ET.SubElement(thickness_element, "Value", unit="m")
        thickness_value.text = str(thickness)[1:-1]

    # 將xml檔案寫入
    tree.write(file_path, encoding="utf-8")

    print("The XML file has been saved at : " + str(file_path))

    return

def save_jpg_layout():
    global downloads_path, jpglayout, drawings_number, dwgfile, narrowtype

    file_path = filedialog.askdirectory( title='Please choose the save location for the JPG layout image.',initialdir=downloads_path)

    try:
        downloads_path = file_path
        jpglayout = os.path.join(downloads_path, "Elevation_Layout.jpg")
        print("The JPG image has been saved at : " + str(jpglayout)[:-4]+"_X.jpg")
    except Exception as e:
        print(f"Error: {e}")
        downloads_path = str(Path.home() / "Downloads")
        jpglayout = os.path.join(downloads_path, "Elevation_Layout.jpg")
        print("The JPG image will be saved at the default location : " + str(jpglayout)[:-4]+"_X.jpg")
    
    # ### **Export to JPG** 
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    box_color = ["black", "red", "green", "blue", "purple", "orange", "dimgrey", "olive", "magenta", "mediumslateblue", "brown", "darkturquoise", "violet"]
    wall_type_color_check=[None]
    for drawings_number in range(0,len(dwgfile)):
        fsource=dwgfile[drawings_number]
        for i in fsource[2:]:
            for j in i.line_member:
                x_values = [j[4][0],j[3][0]]
                y_values = [j[4][1],j[3][1]]
                if i.type == None:
                    pass
                elif i.type not in wall_type_color_check:
                    wall_type_color_check.append(i.type)
                elif i.type in wall_type_color_check:
                    pass
    wall_type_color_check.sort(key=lambda x: (x is not None, str(x) if x is not None else ""))

    for drawings_number in range(0,len(dwgfile)):
        fig, ax = plt.subplots()
        fsource=dwgfile[drawings_number]
        for i in fsource[2:]:
            for j in i.line_member:
                x_values = [j[4][0],j[3][0]]
                y_values = [j[4][1],j[3][1]]
                ax.plot(x_values,y_values,box_color[wall_type_color_check.index(i.type)%len(box_color)])
        for i in narrowtype[drawings_number]:
            try:
                ax.add_patch(Rectangle((i[0], i[3]), i[2]-i[0], i[1]-i[3],facecolor=box_color[wall_type_color_check.index(i[-1])%len(box_color)]))
            except:
                wall_type_color_check.append(i[-1])
                ax.add_patch(Rectangle((i[0], i[3]), i[2]-i[0], i[1]-i[3],facecolor=box_color[wall_type_color_check.index(i[-1])%len(box_color)]))
        #plt.plot([pdf_ncoor[drawings_number][0],pdf_ncoor[drawings_number][2]],[pdf_ncoor[drawings_number][1],pdf_ncoor[drawings_number][3]],"k")
        #plt.plot([dwg_coor[drawings_number][0],dwg_coor[drawings_number][2]],[dwg_coor[drawings_number][1],dwg_coor[drawings_number][3]],"k-")
        #plt.show() #output shown in figure
        jpgfname=jpglayout[:-4] + "_" + str(drawings_number) + ".jpg"
        plt.savefig(jpgfname, format="jpg")

#%%
# Check Final Reading Results Part 2

def canvas_click(event):
    global line_on_canvas, selected_wall, dwgfile, narrowtype, drawing_number
    selected_wall=[]

    # Iterate over the lines
    lines_to_remove = []
    for line in line_on_canvas:
        if canvas.itemcget(line, "width") != "2.0":
            canvas.delete(line)
            lines_to_remove.append(line)

    # Remove the lines from line_on_canvas
    for line in lines_to_remove:
        line_on_canvas.remove(line)
        
    # Check if a wall was clicked
    x_coords1 = [coord for wall in dwgfile[drawing_number][2:] for line in wall.line_member for coord in [line[3][0], line[4][0]]]
    y_coords1 = [coord for wall in dwgfile[drawing_number][2:] for line in wall.line_member for coord in [line[3][1], line[4][1]]]
    x_coords2 = [coord for arrow in narrowtype[drawing_number] for coord in [arrow[0], arrow[2]]]
    y_coords2 = [coord for arrow in narrowtype[drawing_number] for coord in [arrow[1], arrow[3]]]
    x_coords=x_coords1+x_coords2
    y_coords=y_coords1+y_coords2
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    for wall in dwgfile[drawing_number][2:]:
        point_list=[]
        for line in wall.line_member:
            x0, y0 = line[3][:2]
            x1, y1 = line[4][:2]
            norm_x0 = (x0 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
            norm_y0 = (y0 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
            norm_y0 = canvas_height - norm_y0
            norm_x1 = (x1 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
            norm_y1 = (y1 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
            norm_y1 = canvas_height - norm_y1
            point_list.append([norm_x0, norm_y0])
            point_list.append([norm_x1, norm_y1])
        points = np.array(point_list)
        hull = ConvexHull(points)
        convex_hull_vertices = points[hull.vertices]
        polygon = Polygon(convex_hull_vertices)
        if polygon.contains_point(np.array([event.x, event.y])):
            for line in wall.line_member:
                x0, y0 = line[3][:2]
                x1, y1 = line[4][:2]
                norm_x0 = (x0 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
                norm_y0 = (y0 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
                norm_y0 = canvas_height - norm_y0
                norm_x1 = (x1 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
                norm_y1 = (y1 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
                norm_y1 = canvas_height - norm_y1
                line_on_canvas.append(canvas.create_line(norm_x0, norm_y0, norm_x1, norm_y1, fill=box_color[wall_type_color_check.index(wall.type)%len(box_color)], width=4))
            selected_wall.append(wall)
            if 80<=wall.gradient<=100:
                wall_label.config(text="A Wall Has Been Chosen")
                wall_type_label.config(text="Wall Type = "+str(wall.type))
                wall_depth_label.config(text="Wall Depth = "+str(round(wall.length,2))+" m")
                wall_thickness_label.config(text="Wall Thickness = "+str([round(x, 2) for x in wall.thickness if x != 0])[1:-1]+" m")
    if selected_wall==[]:   # No wall was clicked
        wall_label.config(text="No Wall Chosen")
        wall_type_label.config(text="Wall Type = None")
        wall_depth_label.config(text="Wall Depth = 0 m")
        wall_thickness_label.config(text="Wall Thickness = 0 m")

def on_type_select(event):
    global wall_type_color_check
    selected_index = color_legend_listbox.curselection()
    if selected_index[0] in range(0,len(wall_type_color_check)):
        color_legend_listbox.selection_clear(selected_index)

def change_type():
    global drawing_number, selected_wall, wall_type_color_check, dwgfile, all_wall_thickness, all_wall_height
    if selected_wall==[]:return

    def select_type():
        selected_index = listbox.curselection()
        new_type = entry.get()
        if selected_index:
            selected_type = wall_type_color_check[selected_index[0]]
            for wall in selected_wall:
                wall.setType(selected_type)
            dialog.destroy()
        elif new_type:
            for wall in selected_wall:
                wall.setType(new_type)
            if new_type not in wall_type_color_check: wall_type_color_check.append(new_type)
            dialog.destroy()
        all_wall_thickness, all_wall_height = calc_result()
        color_legend_listbox.delete(0, tk.END)  # Delete all items in the listbox
        table_data = "| {:^16s} | {:^12s} | {:^12s} |".format("Color Legend", "Depth (m)", "Thickness (m)")
        color_legend_listbox.insert(tk.END, table_data)
        for type in wall_type_color_check:
            try:
                depth = all_wall_height[type]
            except:
                depth=[0]
            try:
                thickness = all_wall_thickness[type]
            except:
                thickness=[0]
            if depth==[0] and thickness==[0]:continue
            table_data = "|  ———— {:^10s} | {:^12s} | {:^12s} |".format("Type "+str(type), str(depth)[1:-1], str(thickness)[1:-1])
            color_legend_listbox.insert(tk.END, table_data)
            color_legend_listbox.itemconfig(tk.END, fg=box_color[wall_type_color_check.index(type)%len(box_color)])  # Set the color for each item
        select_dwg_combobox.current(drawing_number)
        select_dwg_combobox.event_generate("<<ComboboxSelected>>")

    def clear_listbox_selection(event):
        listbox.selection_clear(0, tk.END)
    
    def clear_entry(event):
        entry.delete(0, tk.END)

    def add_new_type(event):
        new_type = entry.get()
        if new_type:
            wall.setType(new_type)
            entry.delete(0, tk.END)
            entry.focus_set()
        select_dwg_combobox.current(drawing_number)
        select_dwg_combobox.event_generate("<<ComboboxSelected>>")
    
    # Create a pop-up dialog
    dialog = tk.Toplevel(window)
    dialog.title("Change Wall Type")
    
    # Create a label for the dialog
    label = tk.Label(dialog, text="Select wall type:")
    label.pack(pady=10)
    
    # Create a listbox to display wall types
    listbox = tk.Listbox(dialog,selectmode="single", activestyle="none")
    listbox.bind("<<ListboxSelect>>", clear_entry)
    listbox.pack(padx=20, pady=5)
    
    # Add wall types to the listbox
    for type in wall_type_color_check:
        listbox.insert(tk.END, "   ———— "+str(type))
        listbox.itemconfig(tk.END, fg=box_color[wall_type_color_check.index(type)%len(box_color)])  # Set the color for each item

    # Create a text and a textbox for adding a new type
    add_text = tk.Label(dialog, text="or add a new wall type:")
    add_text.pack(pady=5)
    
    entry = tk.Entry(dialog)
    entry.bind("<Button-1>", clear_listbox_selection)
    entry.bind("<Return>", add_new_type)
    entry.pack(padx=20, pady=5)

    # Create a frame for buttons
    ok_cancel_frame = tk.Frame(dialog)
    ok_cancel_frame.pack()

    # Create an "OK" button to confirm the selection
    ok_button = tk.Button(ok_cancel_frame, text="OK", command=select_type)
    ok_button.pack(side=tk.LEFT, padx=5, pady=10)

    # Create a "Cancel" button to cancel the selection
    cancel_button = tk.Button(ok_cancel_frame, text="Cancel", command=dialog.destroy)
    cancel_button.pack(side=tk.LEFT, padx=5, pady=10)
    
    # Run the dialog window
    dialog.mainloop()
    
    
def show_dwg_file(event):
    global drawing_number, line_on_canvas, selected_wall, dwgfile, narrowtype
    selected_file = select_dwg_combobox.get()
    drawing_number = dwgfname.index(selected_file)

    # Clear the canvas
    canvas.delete("all")
    line_on_canvas=[]

    # Draw the lines on the canvas
    x_coords1 = [coord for wall in dwgfile[drawing_number][2:] for line in wall.line_member for coord in [line[3][0], line[4][0]]]
    y_coords1 = [coord for wall in dwgfile[drawing_number][2:] for line in wall.line_member for coord in [line[3][1], line[4][1]]]
    x_coords2 = [coord for arrow in narrowtype[drawing_number] for coord in [arrow[0], arrow[2]]]
    y_coords2 = [coord for arrow in narrowtype[drawing_number] for coord in [arrow[1], arrow[3]]]
    x_coords=x_coords1+x_coords2
    y_coords=y_coords1+y_coords2
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    for wall in dwgfile[drawing_number][2:]:
        for line in wall.line_member:
            x0, y0 = line[3][:2]
            x1, y1 = line[4][:2]
            norm_x0 = (x0 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
            norm_y0 = (y0 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
            norm_y0 = canvas_height - norm_y0
            norm_x1 = (x1 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
            norm_y1 = (y1 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
            norm_y1 = canvas_height - norm_y1
            line_on_canvas.append(canvas.create_line(norm_x0, norm_y0, norm_x1, norm_y1, fill=box_color[wall_type_color_check.index(wall.type)%len(box_color)], width=2))

    for arrow in narrowtype[drawing_number]:
        x0, y0, x1, y1, arrow_type = arrow
        norm_x0 = (x0 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
        norm_y0 = (y0 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
        norm_y0 = canvas_height - norm_y0
        norm_x1 = (x1 - min_x) / (max_x - min_x) * (canvas_width-50) + 25
        norm_y1 = (y1 - min_y) / (max_y - min_y) * (canvas_height-50) + 25
        norm_y1 = canvas_height - norm_y1
        try:
            color=box_color[wall_type_color_check.index(arrow_type)%len(box_color)]
        except:
            wall_type_color_check.append(arrow_type)
            color=box_color[wall_type_color_check.index(arrow_type)%len(box_color)]
        canvas.create_rectangle(norm_x0, norm_y0, norm_x1, norm_y1, outline=color, fill=color)
    
    # Update the label
    selected_wall=[]
    wall_label.config(text="No Wall Chosen")
    wall_type_label.config(text="Wall Type = None")
    wall_depth_label.config(text="Wall Depth = 0 m")
    wall_thickness_label.config(text="Wall Thickness = 0 m")

def save_to_new_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
    if file_path:
        save_xml_file(file_path)
        window.quit()
        window.destroy()

def save_to_existing_file():
    file_path = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
    if file_path:
        save_xml_file(file_path)
        window.quit()
        window.destroy()

# Create the Tkinter window
window = tk.Tk()
window.title("Reading Results")

# Create a frame for the canvas
canvas_frame = tk.Frame(window)
canvas_frame.pack(side=tk.LEFT, expand=False,padx=(20,10), pady=20)

# Create a canvas to draw the line
line_on_canvas=[]
canvas_width,canvas_height=(702,496)
canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height, background="white")
canvas.pack()

# Create a frame for the button
menu_frame = tk.Frame(window)
menu_frame.pack(side=tk.TOP, padx=(10,20), pady=20)

# Create a label for displaying "Color Legend"
color_legend_label = tk.Label(menu_frame, text="Reading Results from All Drawings", font=("Arial", 14))
color_legend_label.pack(pady=0)

# Create a listbox to show the color legend
color_legend_listbox = tk.Listbox(menu_frame, font=('Courier New', 12), width=50, selectmode="single", activestyle="none")
color_legend_listbox.pack(pady=5)
table_data = "| {:^16s} | {:^12s} | {:^12s} |".format("Color Legend", "Depth (m)", "Thickness (m)")
color_legend_listbox.insert(tk.END, table_data)
for type in wall_type_color_check:
    try:
        depth = all_wall_height[type]
    except:
        depth=[0]
    try:
        thickness = all_wall_thickness[type]
    except:
        thickness=[0]
    if depth==[0] and thickness==[0]:continue
    table_data = "|  ———— {:^10s} | {:^12s} | {:^12s} |".format("Type "+str(type), str(depth)[1:-1], str(thickness)[1:-1])
    color_legend_listbox.insert(tk.END, table_data)
    color_legend_listbox.itemconfig(tk.END, fg=box_color[wall_type_color_check.index(type)%len(box_color)])  # Set the color for each item
color_legend_listbox.bind("<<ListboxSelect>>", on_type_select)
separator = tk.Frame(menu_frame, height=2, bd=3, relief=tk.SUNKEN)
separator.pack(fill=tk.X, padx=10, pady=(5,10))

# Create a frame for select dwg
select_dwg_frame = tk.Frame(menu_frame)
select_dwg_frame.pack()

# Create a label for displaying "Select DWG File"
select_dwg_label = tk.Label(select_dwg_frame, text="Select DWG :", font=("Arial", 14))
select_dwg_label.pack(side=tk.LEFT,pady=0)

# Create a combobox (dropdown menu) widget
select_dwg_combobox = ttk.Combobox(select_dwg_frame, values=dwgfname)
select_dwg_combobox.bind("<<ComboboxSelected>>", show_dwg_file)
select_dwg_combobox.pack(side=tk.LEFT,pady=0, padx=(0, 0))

# Create a label for displaying "Plan/Elevation Drawing"
drawing_type_label = tk.Label(menu_frame, text="Drawing Type : " + str(dwgfile[0][1]), font=("Arial", 14))
drawing_type_label.pack(pady=0)

# Create a label for displaying "You chose a wall"
wall_label = tk.Label(menu_frame, text="No Wall Chosen", font=("Arial", 14), fg="blue")
wall_label.pack(pady=0)

# Create frame for wall type menu
wall_type_frame = tk.Frame(menu_frame)
wall_type_frame.pack()

# Create a label for displaying "Wall Type"
wall_type_label = tk.Label(wall_type_frame, text="Wall Type = None", font=("Arial", 14), fg="blue")
wall_type_label.pack(side=tk.LEFT,pady=0)

# Create a button to select the file
change_type_button = tk.Button(wall_type_frame, text="Change", command=change_type)
change_type_button.pack(side=tk.LEFT,pady=0, padx=(5, 0))

# Create a label for displaying "Wall Depth"
wall_depth_label = tk.Label(menu_frame, text="Wall Depth = 0 m", font=("Arial", 14), fg="blue")
wall_depth_label.pack(pady=0)

# Create a label for displaying "Wall Thickness"
wall_thickness_label = tk.Label(menu_frame, text="Wall Thickness = 0 m", font=("Arial", 14), fg="blue")
wall_thickness_label.pack(pady=0)

# Create a button to select XML file directory
new_file_button = tk.Button(menu_frame, text="存入新檔", command=save_to_new_file)
existing_file_button = tk.Button(menu_frame, text="寫入舊檔", command=save_to_existing_file)
new_file_button.pack(pady=5, padx=(0, 0))
existing_file_button.pack(pady=5, padx=(0, 0))

# Create a button to select JPG layout directory
save_jpg_button = tk.Button(menu_frame, text="Save JPG Layout", command=save_jpg_layout)
save_jpg_button.pack(pady=5, padx=(0, 0))

# Show the first dwg
select_dwg_combobox.current(0)
select_dwg_combobox.event_generate("<<ComboboxSelected>>")

# Bind the canvas click event
canvas.bind("<Button-1>", canvas_click)

# Run the Tkinter event loop
window.mainloop()


# %%
# Remove redundant files

os.remove(dirpath +"\\"+ "PUBLIST.dsd")
os.remove(dirpath +"\\"+ "Text Info.csv")
os.remove(pdfpath)
os.remove(csvpath)

# %% [markdown]
# ### **Export to EXE** 

# %%
"""
1. Type : >Export to Python Script in search bar
2. Open CMD in the file folder
3. Type :
pip install pyinstaller
pyinstaller --onefile "Data Process - Elevation Drawings.py" -w
pyinstaller -F "Data Process - Elevation Drawings.py" --collect-all easyocr
pyinstaller "Data Process - Elevation Drawings.py" --add-data "C:/Users/Ricardo/.EasyOCR/model/*;models" --hidden-import easyocr --collect-all easyocr --noconfirm
"""


