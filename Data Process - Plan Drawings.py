# %% [markdown]
# ### **Import Module, Define Class, & Define Function**

# %%
#Import Module
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

def get_max_distance(lines):
    max_distance = 0
    for i in range(len(lines)):
        for j in range(i+1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            for p1 in line1[3:5]:
                for p2 in line2[3:5]:
                    distance = get_distance(p1, p2)
                    if distance > max_distance:
                        max_distance = distance
    return max_distance

def split_wall(wall,file):
    gradient=wall.gradient
    i=file.index(wall)
    del file[i]
    x_list,y_list=[],[]
    for l,line in enumerate(wall.line_member):
        ax1,ay1,ax2,ay2=line[3][0],line[3][1],line[4][0],line[4][1]
        x_list.append(ax1)
        x_list.append(ax2)
        y_list.append(ay1)
        y_list.append(ay2)
    x_list=sorted(list(set(x_list)))
    y_list=sorted(list(set(y_list)))
    xy_list1=[]
    for x,x_value in enumerate(x_list):
        for y,y_value in enumerate(y_list):
            xy_list1.append([x_value,y_value])
    xy_list2=[]
    for xy1,xy_value1 in enumerate(xy_list1):
        for xy2,xy_value2 in enumerate(xy_list1[xy1:]):
            try:test_gradient=(xy_value1[1]-xy_value2[1])/(xy_value1[0]-xy_value2[0])
            except:test_gradient=90
            if xy1!=xy2 and test_gradient==gradient:
                xy_list2.append([xy_value1[0],xy_value1[1],xy_value2[0],xy_value2[1]])
    line_list=[]
    count=0
    for i,item in enumerate(xy_list2):
        for j,jtem in enumerate(wall.line_member):
            if is_shorter_collinear_within_longer(item[0],item[1],item[2],item[3],jtem[3][0],jtem[3][1],jtem[4][0],jtem[4][1]):
                count+=1
                #print(item,jtem[3][:2]+jtem[4][:2])
                new_line=copy.deepcopy(jtem)
                new_line[0]+=str(count).zfill(2)
                new_line[3][0],new_line[3][1]=item[0],item[1]
                new_line[4][0],new_line[4][1]=item[2],item[3]
                new_line[2]=math.sqrt(math.pow((new_line[4][0]- new_line[3][0]),2)+math.pow((new_line[4][1]- new_line[3][1]),2))
                line_list.append(new_line)
    to_be_removed_line_index=[]
    for i,line in enumerate(line_list):
        for j,other_line in enumerate(line_list):
            if i==j:
                break
            if line[2]>=other_line[2]:
                if is_shorter_collinear_within_longer(other_line[3][0],other_line[3][1],other_line[4][0],other_line[4][1],line[3][0],line[3][1],line[4][0],line[4][1]):
                    to_be_removed_line_index.append(i)
                    break
    to_be_removed_line_index.sort(reverse=True)
    for i in to_be_removed_line_index:
        del line_list[i]
    additional_wall=[]
    recorded_line=[] #record the line that has find their couple(s) in the file
    line_list.sort(key=itemgetter(2),reverse=True)
    i=line_list
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
            wall=wall_plan(shortest_group) 
            if max(wall.thickness)<wall.length:
                additional_wall.append(wall)
    #add ungrouped line
    grouped_line = [line for wall in additional_wall for line in wall.line_member]
    ungrouped_line = [line for line in line_list if line not in grouped_line]

    for line in ungrouped_line:
        grouped=False
        for w,wall in enumerate(additional_wall):
            if not grouped:
                for other_line in wall.line_member:
                    if line[3]==other_line[3] or line[3]==other_line[4] or line[4]==other_line[3] or line[4]==other_line[4] : 
                        additional_wall[w].addLine(line)
                        grouped=True
                        break 
    file.extend(additional_wall)
    return file

def is_collinear(x1, y1, x2, y2, x3, y3, x4, y4):
    # Calculate the slopes of the two lines
    slope1 = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')
    slope2 = (y4 - y3) / (x4 - x3) if x4 != x3 else float('inf')
    
    # Check if the slopes are equal
    return slope1 == slope2 

def is_within_span(x1, y1, x2, y2, x3, y3, x4, y4):
    # Check if both endpoints of the shorter line lie between the endpoints of the longer line
    return (min(x1, x2) <= x3 <= max(x1, x2) and min(y1, y2) <= y3 <= max(y1, y2) and
            min(x1, x2) <= x4 <= max(x1, x2) and min(y1, y2) <= y4 <= max(y1, y2))

def is_shorter_collinear_within_longer(x1, y1, x2, y2, x3, y3, x4, y4):
    # Calculate the lengths of the two lines
    len1 = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    len2 = ((x4 - x3)**2 + (y4 - y3)**2)**0.5
    
    # Check which line is shorter
    if len1 <= len2:
        shorter_x1, shorter_y1, shorter_x2, shorter_y2 = x1, y1, x2, y2
        longer_x1, longer_y1, longer_x2, longer_y2 = x3, y3, x4, y4
    else:
        return False
    
    # Check if the shorter line is collinear and within the span of the longer line
    return is_collinear(x1, y1, x2, y2, x3, y3, x4, y4) and is_within_span(longer_x1, longer_y1, longer_x2, longer_y2,shorter_x1, shorter_y1, shorter_x2, shorter_y2) 

def categorize_lines(line_member,thickness):
  thickness = thickness[0]
  main_line=line_member[0]
  inner_lines,outer_lines=[main_line],[]
  inner_length,outer_length=0,0
  for other_line in line_member[1:]:
    line1=main_line[4][:2]+main_line[3][:2]
    line2=other_line[4][:2]+other_line[3][:2]
    if round(l2l_CD(line1,line2),2)!=round(thickness,2):
        inner_lines.append(other_line)
    else:outer_lines.append(other_line)
  if len(inner_lines)==1:inner_length=inner_lines[0][2]
  else:inner_length=get_max_distance(inner_lines)
  if len(outer_lines)==1:outer_length=outer_lines[0][2]
  else:outer_length=get_max_distance(outer_lines)
  if inner_length>outer_length:
    inner_lines,outer_lines=outer_lines,inner_lines
    inner_length,outer_length=outer_length,inner_length
  else:pass
  return inner_lines, outer_lines,inner_length,outer_length

def b2b_CD(box1, box2, gradient):
    # box1 and box2 should be tuples of the form (x1, y1, x2, y2)
    # where (x1, y1) are the coordinates of the upper left corner of the box
    # and (x2, y2) are the coordinates of the lower right corner of the box
    if gradient==0:
        if CheckRectangleOverlap(box1,box2):
            return 0
        else:
            return min([abs(box1[1]-box2[1]),abs(box1[1]-box2[3]),abs(box1[3]-box2[1]),abs(box1[3]-box2[3])])
    elif gradient==90:
        if CheckRectangleOverlap(box1,box2):
            return 0
        else:
            return min([abs(box1[0]-box2[0]),abs(box1[0]-box2[2]),abs(box1[2]-box2[0]),abs(box1[2]-box2[2])])
    else: return 0

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

    return (overlap > 0), endpoint, overlap

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

def l2l_CD(line1, line2):
    if (line1[0]-line1[2])!=0:
        m1=(line1[1]-line1[3])/(line1[0]-line1[2])
        m2=(line2[1]-line2[3])/(line2[0]-line2[2])
        b1=line1[1]-m1*line1[0]
        b2=line2[1]-m1*line2[0]
        return abs(b2-b1)/math.sqrt(m1*m1+1)
    else: return abs(line1[0]-line2[0])
    
def CheckRectangleOverlap(R1, R2):
    if (R1[0]>R2[2]) or (R1[2]<R2[0]) or (R1[3]>R2[1]) or (R1[1]<R2[3]):
        return False
    else:
        return True

# %%
#Define Wall class
class wall_plan:
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
      x_coor.extend([i[3][0],i[4][0]])
      y_coor.extend([i[3][1],i[4][1]])
    self.thickness=sorted(list(set(thickness)),reverse=True)
    self.gradient=sum(gradient)/len(gradient)
    self.line_number=len(line)
    self.line_member=line
    x_coor.sort(reverse=False)
    y_coor.sort(reverse=False)
    self.coor=[x_coor[0],y_coor[-1],x_coor[-1],y_coor[0]]
    self.type=None
    self.relation={}
    self.inner_side_lines,self.outer_side_lines,self.inner_side_length,self.outer_side_length=categorize_lines(self.line_member,self.thickness)
    self.length=(self.outer_side_length+self.inner_side_length)/2

  def __str__(self):
    return f"wall_plan with length={self.length}, thickness={self.thickness}, gradient={self.gradient} , and {self.line_number} lines"
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
      x_coor.extend([i[3][0],i[4][0]])
      y_coor.extend([i[3][1],i[4][1]])
    self.thickness=sorted(list(set(thickness)),reverse=True)
    self.gradient=sum(gradient)/len(gradient)
    self.line_number=len(line)
    self.line_member=line
    x_coor.sort(reverse=False)
    y_coor.sort(reverse=False)
    self.coor=[x_coor[0],y_coor[-1],x_coor[-1],y_coor[0]]
    self.inner_side_lines,self.outer_side_lines,self.inner_side_length,self.outer_side_length=categorize_lines(self.line_member,self.thickness)
    self.length=self.outer_side_length
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
      x_coor.extend([i[3][0],i[4][0]])
      y_coor.extend([i[3][1],i[4][1]])
    self.thickness=sorted(list(set(thickness)),reverse=True)
    self.gradient=sum(gradient)/len(gradient)
    self.line_number=len(line)
    self.line_member=line
    x_coor.sort(reverse=False)
    y_coor.sort(reverse=False)
    self.coor=[x_coor[0],y_coor[-1],x_coor[-1],y_coor[0]]
    self.inner_side_lines,self.outer_side_lines,self.inner_side_length,self.outer_side_length=categorize_lines(self.line_member,self.thickness)
    self.length=self.outer_side_length
  def add_relation(self,wall,relation):
    self.relation[wall]=relation

# %% [markdown]
# ### **Import CSV**

# %%
#import CSV
dirpath=" ".join(sys.argv[1:])
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
print("linfo: [0] File Name, [1] Entity Name, [2] Layer Name, [3] Line Length, [4] Start Coor, [5] End Coor, [6] Line Gradient")

csvpath=dirpath +"\\"+ "Text Info.csv"
tinfo=[]
with open(csvpath, newline='') as f:
    tinfo = list(csv.reader(f))
    del tinfo[0]
    for i in tinfo:
      i[1]=i[1][14:-1]
      i[3]=round(math.degrees(float(i[3])))%180
      if i[2]=="AcDbMText" or i[2]=="AcDbText":
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
        i[4],i[5]=upper_left,lower_right
      if i[2]=="AcDbRotatedDimension":
        i[4]=i[4][1:-1].split()
        for j in range(3): i[4][j]=float(i[4][j])
        i[5]=i[5][1:-1].split()
        for j in range(3): i[5][j]=float(i[5][j])
        i[6]=i[6][1:-1].split()
        for j in range(3): i[6][j]=float(i[6][j])
        # Get the start and end coordinates of the text box
        start_coor,end_coor = i[4],i[6]
        # Calculate the absolute upper-left and lower-right coordinates of the text box
        upper_left_x = min(start_coor[0],end_coor[0])
        upper_left_y = max(start_coor[1],end_coor[1])
        lower_right_x = max(start_coor[0],end_coor[0])
        lower_right_y = min(start_coor[1],end_coor[1])
        upper_left = [upper_left_x, upper_left_y]
        lower_right = [lower_right_x, lower_right_y]
        i[4],i[5]=upper_left,lower_right
      i[6]=" ".join(i[7].split()).upper()
      del i[8],i[7]
print("tinfo: [0] File Name, [1] Entity Name, [2] Object Type, [3] Rotation Angle, [4] Start Coor, [5] End Coor, [6] Text")

# %% [markdown]
# ### **Data Pre-Process**

# %%
#Data Pre-Process
#Line Info Pre-Process
dwgfname= sorted(list(set(i[0] for i in linfo)))
dwgftype=[]
dwgfline=[]
for i in dwgfname:
    dwgfline.append([])
    for j in linfo:
        if i == j[0]:
            dwgfline[-1].append(j[1:])
    dwgftype.append("Plan Drawings")
print("dwgfline[file name]: [0] Entity Name, [1] Layer Name, [2] Line Length, [3] Start Coor, [4] End Coord, [5] Line Gradient")

#Text Info Pre-Process
dwgfname= sorted(list(set(i[0] for i in tinfo)))
dwgtext=[]
for i in dwgfname:
    dwgtext.append([])
    for j in tinfo:
        if j[2]!="AcDbMText" and j[2]!="AcDbText" and i == j[0] and "WALL" in j[6] and "TYPE" in j[6] :
            dwgtext[-1].append(j[1:])
print("dwgtext[file name]: [0] Entity Name, [1] Object Type, [2] Rotation Angle, [3] Start Coor, [4] End Coor, [5] Text")


# %%
#check mergeable
import matplotlib.pyplot as plt
import numpy as np
colormap=['b-','g-','r-','c-','m-','b-.','g-.','c-.','r-.','m-.','b--','g--','r--','c--','m--']
mergeale_line=[]
for i in range(1,len(dwgfline)):
    for j in range(0,len(dwgfline[i])):
        for k in range(j+1,len(dwgfline[i])):
            line1=dwgfline[i][j][4][:2]+dwgfline[i][j][3][:2]
            line2=dwgfline[i][k][4][:2]+dwgfline[i][k][3][:2]
            if check_mergeable(line1,line2):
                mergeale_line.append(line1)
                mergeale_line.append(line2)
                x_values1 = [line1[0],line1[2]]
                x_values2 = [line2[0],line2[2]]
                y_values1 = [line1[1],line1[3]]
                y_values2 = [line2[1],line2[3]]

# %% [markdown]
# ### **Line Breaking**

# %%
#text and arrow pre-process
case1_type,wall_type=[],[]
for file in dwgtext:
  case1_type.append([])
  for text in file:
    type_text=text[5].replace("DIAPHRAGM WALL TYPE ","")
    case1_type[-1].append([text[3][0],text[3][1],text[4][0],text[4][1],type_text,'line','line'])
    wall_type.append(type_text)
wall_type=sorted(list(set(wall_type)))

range_line_0=[]
range_line_90=[]
cut_0=[]
cut_90=[]

for i,item in enumerate(case1_type):
    range_line_0.append([])
    range_line_90.append([])
    temp_0=[]
    temp_90=[]
    for j, jtem in enumerate(item):
        if jtem[5]!='line' and jtem[6]!='line':
            gradient=jtem[3]
            temp_line=rotate_coor(jtem[0],jtem[1],-gradient)+rotate_coor(jtem[2],jtem[3],-gradient)
            temp_line=rotate_coor(temp_line[0],temp_line[1],gradient)+rotate_coor(temp_line[2],temp_line[3],gradient)
            case1_type[i][j][:-3]=temp_line
        elif jtem[5]=='line' and jtem[6]=='line':
            gradient=90
            if abs(jtem[2]-jtem[0])>= abs(jtem[3]-jtem[1]):
                gradient=0
                range_line_0[-1].append([jtem[0],jtem[2]])
                temp_0.append(jtem[0])
                temp_0.append(jtem[2])
            else:
                gradient=90
                range_line_90[-1].append([jtem[1],jtem[3]])
                temp_0.append(jtem[1])
                temp_0.append(jtem[3])
    cut_0.append(sorted(list(set(temp_0))))
    cut_90.append(sorted(list(set(temp_90))))

# %%
#break line
dwgnfline=[]
for drawings_number in range(0,len(dwgfline)):
    dwgnfline.append([])
    for i,item in enumerate(dwgfline[drawings_number]):
        if item[5]==0:
            cut=0
            item=dwgfline[drawings_number][i]
            if item[3][0]>item[4][0]:
                item[3][0],item[4][0]=item[4][0],item[3][0]
            for j,jtem in enumerate(cut_0[drawings_number]):
                if item[3][0]<jtem<item[4][0]:
                    item1=copy.deepcopy(item)
                    if cut>0:item1[3][0]=cut_0[drawings_number][j-1]
                    else:pass
                    item1[4][0]=jtem
                    item1[2]=math.sqrt(math.pow((item1[4][0]- item1[3][0]),2)+math.pow((item1[4][1]- item1[3][1]),2))
                    item1[0]+=str(cut+1).zfill(2)
                    dwgnfline[-1].append(item1)
                    cut+=1
            if item[3][1]>item[4][1]:
                item[3][1],item[4][1]=item[4][0],item[3][1]
            for j,jtem in enumerate(cut_90[drawings_number]):
                if item[3][1]<jtem<item[4][1]:
                    item1=copy.deepcopy(item)
                    if cut>0:item1[3][1]=cut_90[drawings_number][j-1]
                    else:pass
                    item1[4][1]=jtem
                    item1[2]=math.sqrt(math.pow((item1[4][0]- item1[3][0]),2)+math.pow((item1[4][1]- item1[3][1]),2))
                    item1[0]+=str(cut+1).zfill(2)
                    dwgnfline[-1].append(item1)
                    cut+=1
            item1=copy.deepcopy(item)
            if cut>0:
                item1[3][0]=dwgnfline[-1][-1][4][0]
                item1[3][1]=dwgnfline[-1][-1][4][1]
            else:pass
            item1[2]=math.sqrt(math.pow((item1[4][0]- item1[3][0]),2)+math.pow((item1[4][1]- item1[3][1]),2))
            if cut>0:item1[0]+=str(cut+1).zfill(2)
            else:item1[0]+='00'
            dwgnfline[-1].append(item1)
        else:
            item1=copy.deepcopy(item)
            item1[2]=math.sqrt(math.pow((item1[4][0]- item1[3][0]),2)+math.pow((item1[4][1]- item1[3][1]),2))
            item1[0]+='00'
            dwgnfline[-1].append(item1)
    dwgfline[-1].sort(key=itemgetter(3,4),reverse=False)
        #elif item[5]==90:
            #print(item)
dwgfline_ref=copy.deepcopy(dwgfline[:])
dwgfline[:]=copy.deepcopy(dwgnfline[:])

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
            if dwgftype[dwgfline.index(i)]=="Plan Drawings":
                wall=wall_plan(shortest_group) 
                if max(wall.thickness)<wall.length:
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
                        #print(l[0],j,ep2ep_dist,max(j.thickness))
                        no_group_line[i].remove(l)
                        continue

# %% [markdown]
# ### **Line and Text Coordinate Adjustment for Case 1**

# %%
#text and arrow pre-process
for i,item in enumerate(case1_type):
    for j, jtem in enumerate(item):
        gradient=jtem[3]
        temp_line=rotate_coor(jtem[0],jtem[1],-gradient)+rotate_coor(jtem[2],jtem[3],-gradient)
        temp_line=rotate_coor(temp_line[0],temp_line[1],gradient)+rotate_coor(temp_line[2],temp_line[3],gradient)+[case1_type[i][j][4]]
        case1_type[i][j]=temp_line

# %%
#set wall type for case 1
for i,file in enumerate(dwgfile):
    for j,wall in enumerate(file[2:]):
        overlapped_line=[]
        for k,text in enumerate(case1_type[i]):
            text_value=text[4][:]
            text_coor=text[:4]
            text_gradient=text[3]
            if text_gradient<=45:
                text_gradient=0
                text_line_coor=[text_coor[0],0.5*(text_coor[1]+text_coor[3]),text_coor[2],0.5*(text_coor[1]+text_coor[3])]
            elif text_gradient>45:
                text_gradient=90
                text_line_coor=[0.5*(text_coor[0]+text_coor[2]),text_coor[1],0.5*(text_coor[0]+text_coor[2]),text_coor[3]]
            else:print("unknown text#set wall type for case 1")
            wall_line_coor=[]
            for line in wall.outer_side_lines:
                for other_line in wall.outer_side_lines:
                    p1,p2,p3,p4=line[3][:],line[4][:],other_line[3][:],other_line[4][:]
                    wall_line_coor.append([p1,p2,get_distance(p1,p2)])
                    wall_line_coor.append([p1,p3,get_distance(p1,p3)])
                    wall_line_coor.append([p1,p4,get_distance(p1,p4)])
                    wall_line_coor.append([p2,p3,get_distance(p2,p3)])
                    wall_line_coor.append([p2,p4,get_distance(p2,p4)])
                    wall_line_coor.append([p3,p4,get_distance(p3,p4)])
            wall_line_coor.sort(key=itemgetter(2),reverse=True)
            wall_line_coor=wall_line_coor[0][0][:2]+wall_line_coor[0][1][:2]
            if text_gradient-gradient_tolerance<=wall.gradient<=text_gradient+gradient_tolerance: #check gradient
                if check_overlap(wall_line_coor,text_line_coor)[0] and round(check_overlap(wall_line_coor,text_line_coor)[2],2)>0.01*wall.length: #check overlap for unassigned type wall
                    text_dist=b2b_CD(wall.coor,text_coor,wall.gradient) #calculate distance
                    overlapped_line.append([j+2,text_value,text_dist,check_overlap(wall_line_coor,text_line_coor)[2]])
        overlapped_line.sort(key=itemgetter(2),reverse=False)
        if len(overlapped_line)!=0:
            file[overlapped_line[0][0]].setType(overlapped_line[0][1])


# %% [markdown]
# ### **Line and Text Coordinate Adjustment for Case 2**

# %%
import PIL
from PIL import Image, ImageDraw, ImageFont
import pdf2image
import cv2
import easyocr
import numpy as np
import pandas as pd
from tqdm import tqdm

def wait():
    k = cv2.waitKey(0)
    if k == 27:
        cv2.destroyAllWindows()

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
        text = bound[1]
        top_left = tuple(bound[0][0])
        bottom_right = tuple(bound[0][2]) 
        top_top = tuple([bound[0][0][0], bound[0][0][1]-20])
        draw.text(top_top, text, font=font, fill=(255,0,0,128))
        draw.rectangle([top_left, bottom_right],outline='red' )
    #ah.show()
    return ah
    
def for_hori(bl, tr, p, thr) :
   if (p[0] > bl[0]-thr and p[0] < tr[0]+thr and p[1] > bl[1] and p[1] < tr[1]) :
      return True
   else :
      return False

def for_vert(bl, tr, p, thr) :
   if (p[0] > bl[0] and p[0] < tr[0] and p[1] > bl[1]-thr and p[1] < tr[1]+thr) :
      return True
   else :
      return False
   
print('Reading pdf...')
image1 = pdf2image.convert_from_path(dirpath+"\\-Layout1.pdf", dpi=230)

reader = easyocr.Reader(['en','ch_tra'])
dataframe=[]
if len(dwgfline)!= len(image1):
    raise Exception("Inconsistent DWG file number in CSV and PDF")

for image in tqdm(range(len(image1))):

    cv_img = cv2.cvtColor(np.asarray(image1[image]), cv2.COLOR_RGB2BGR)
    cv2.imwrite("img.png",cv_img)

    pilling = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    #pilling.show(title='Arrow_detection_result')

    img_gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    bounds = reader.readtext(img_gray , detail=1)
    array = np.array(bounds, dtype=object)

    for bound in bounds:
        p0, p1, p2, p3 = bound[0] # get coordinates
        p0 = (p0[0],p0[1])
        p2 = (p2[0],p2[1])
        white = cv2.rectangle(cv_img, p0, p2, color=(255,255,255), thickness =-1)

    # show white image
    pilling = Image.fromarray(cv2.cvtColor(white, cv2.COLOR_BGR2RGB))
    #pilling.show(title='Arrow_detection_result')

    img_gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    ret, th = cv2.threshold(img_gray , 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    filterSize =(2,2) 
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)
    img_bhat = cv2.morphologyEx(th, cv2.MORPH_BLACKHAT, kernel)
    img_invers = cv2.bitwise_not(th)
    img_sub = img_invers - img_bhat

    kernel2 = np.ones((2, 2))
    kernel4 = np.ones((3, 3))  # for big_arrow erode-1 dilate-2
    img_erode = cv2.erode(img_sub, kernel2, iterations=1)
    img_dilate = cv2.dilate(img_erode, kernel4, iterations=2)

    contours, hierarchy = cv2.findContours(img_dilate, cv2.RETR_LIST , cv2.CHAIN_APPROX_NONE)


    img = cv2.imread("./img.png")
    for i in range(len(contours)):
        x,y,w,h  = cv2.boundingRect(contours[i])
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),1)
        
    # show arrow head after white image
    pilling = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    #pilling.show(title='Arrow_detection_result')
    #cv2.imwrite("arrow_head.png", img)

    img = cv2.imread("./img.png")
    img_gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    ret, th = cv2.threshold(img_gray , 100, 255, 0)
    contours_a, hierarchy_a = cv2.findContours(th, cv2.RETR_LIST , cv2.CHAIN_APPROX_NONE)
    for i in range(len(contours_a)-1):
        x,y,w,h  = cv2.boundingRect(contours_a[i])
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),1)

    #show contours after white  image
    pilling = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    #pilling.show(title='Arrow_detection_result')
    #cv2.imwrite("countours.png", img)

    real_arrow = []
    img = cv2.imread("./img.png")
    for i in range(len(contours)):
        x1,y1,w1,h1  = cv2.boundingRect(contours[i])
        for j in range(len(contours_a)-1):
            x2,y2,w2,h2  = cv2.boundingRect(contours_a[j])
            if (cv2.contourArea(contours_a[j])> 100):
                if x2 < (x1+w1/2) and (x1+w1/2) < (x2+w2) and y2 < (y1+h1/2) and (y1+h1/2) < (y2+h2):
                    if (x2 + w2/2) < x1:
                        real_arrow.append([j,0])
                    else:
                        real_arrow.append([j,1])

    for i in range(len(real_arrow)):
        x,y,w,h  = cv2.boundingRect(contours_a[real_arrow[i][0]])
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),1)
    
    # show the real arrow counter
    pilling = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    #pilling.show(title='Arrow_detection_result')
    #cv2.imwrite("real_arrow.png", img)
    
    # pair contour with word
    pair_array2 = []
    word = "連續壁型式"

    img = cv2.imread("./img.png")

    for k in range(len(array[:,1])):
    
        if array[k,1].find(word) > -1:
            check = None
            dis = 1000000
            for i in range(len(real_arrow)):
                num = real_arrow[i][0]
                dir = real_arrow[i][1]
                x,y,w,h  = cv2.boundingRect(contours_a[num])
            
                if(dir == 0):
                    head_point = array[k][0][2]
                    tail_point = [x,y+h]
                    if ((tail_point[0]-head_point[0])**2 + (tail_point[1]-head_point[1])**2 ) < dis and ((tail_point[0]-head_point[0])**2 + (tail_point[1]-head_point[1])**2 ) < 15000:
                        dis = ((tail_point[0]-head_point[0])**2 + (tail_point[1]-head_point[1])**2 )
                        check = num
                elif(dir == 1):
                    head_point = array[k][0][0]
                    tail_point = [x+w,y]
                    if ((tail_point[0]-head_point[0])**2 + (tail_point[1]-head_point[1])**2 ) < dis and ((tail_point[0]-head_point[0])**2 + (tail_point[1]-head_point[1])**2 ) < 4000:
                        dis = ((tail_point[0]-head_point[0])**2 + (tail_point[1]-head_point[1])**2 )
                        check = num
            if check != None:
                x,y,w,h = cv2.boundingRect(contours_a[check])
                tail_point = [x+w,y]
                cv2.line(img,array[k][0][0],tail_point,(0,255,0),2)
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),1)
                top_left = tuple(array[k][0][0])
                bottom_right = tuple(array[k][0][2]) 
                cv2.rectangle(img,top_left,bottom_right,(255,0,0),1)

                pair_array2.append([k,check])

    # show pair result
    pilling = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    #pilling.show(title='Arrow_detection_result')
    #cv2.imwrite("pair_result.png", img)

    img = cv2.imread("img.png")
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Multilevel Thresholding -- OTSU method
    ret, th = cv2.threshold(img_gray, 250, 255, 0)

    # Morphological Operation -- Black Hat
    filterSize =(2,2) # (4,4)for dpi = 300, (2,2) for dpi = 200 (6,6) for filter dpi=300
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)

    img_bhat = cv2.morphologyEx(th, cv2.MORPH_BLACKHAT, kernel)

    # line thinning
    thinned = cv2.ximgproc.thinning(img_bhat)

    # get all the lines in the image
    lines = FLD(thinned, thinned)

    def check_line(lines):
        dist1 = 1000000000000000
        dist_y = 0
        record = 0
        for i in range(len(lines)):
            line = lines[i] 
            head_x = line[0,0]
            head_y = line[0,1]

            if(head_x < dist1):
                dist1 = head_x
                dist_y = head_y
                record =i
            elif(head_x == dist1 and head_y < dist_y):
                record = i
                dist1 = head_x
                dist_y = head_y

        return record
        
    


    ans = check_line(lines)
    ans_line = lines[ans]
    #print(f'the (x,y) for ans_line is ({ans_line[0,0]:.2f},{ans_line[0,1]})')

    img = cv2.imread("./img.png")
    head = (int(ans_line[0,0]),int(ans_line[0,1]))
    end = (int(ans_line[0,2]),int(ans_line[0,3]))
    img = cv2.line(img,head, end,(0,0,255),3 )

    # show ref line
    pilling = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    #pilling.show(title='Paired_Arrow')
    #cv2.imwrite("ref.png", img)

    # output csv
    index = list(range(len(pair_array2)+1))
    index[0] = 'REF'

    df = pd.DataFrame(np.arange((len(pair_array2)+1)*5).reshape(1+len(pair_array2),5), columns=['head_x', 'head_y', 'end_x', 'end_y','ocr'],
                    index=index)

    wall_type = []

    for i in pair_array2:
        indexx = i[0]
        string = array[indexx,1]
        check1 = 0
        for j,k in enumerate(string):
            if k == '式' :
                check1 = j
                if string[j+1] == ' ':
                    want_string = string[j+2:len(string)]
                else:
                    want_string = string[j+1:len(string)]
                    want_string = want_string.replace('5','s')
        wall_type.append(want_string)

    #print(wall_type)

    for index,i in enumerate(pair_array2): 
        arrow = int(i[1])
        x,y,w,h = cv2.boundingRect(contours_a[arrow])

        df.iloc[index+1,0] = int(x)
        df.iloc[index+1,1] = int(y)
        df.iloc[index+1,2] = int(x+w)
        df.iloc[index+1,3] = int(y+h)

        df.iloc[index+1,4] = wall_type[index]

    df.iloc[0,0] = int(ans_line[0,0])
    df.iloc[0,1] = int(ans_line[0,1])
    df.iloc[0,2] = int(ans_line[0,2])
    df.iloc[0,3] = int(ans_line[0,3])
    df.iloc[0,4] = 0

    dataframe.append(df.values.tolist())

# %%
#pdf post-process
all_wall_type=wall_type
pdf_coor,arrowtype,wall_type=[],[],[]
for index,file in enumerate(dataframe):
    pdf_coor.append([])
    arrowtype.append([])
    for i,item in enumerate(file):
        for j in range(len(item)-1):
          if j%2==0:
            item[j]=float(item[j]) 
          elif j%2==1:
            item[j]=3807-float(item[j]) #3807 == number of pixely axis when converting pdf to png
        if i==0:
            pdf_coor[-1]=item[:4]
            continue
        wall_type.append(item[4])
        arrowtype[-1].append(item[:])
wall_type=sorted(list(set(wall_type)))       

# %%
#import dwg coor
dwg_coor=[]
for i in range(0,len(dwgfline_ref)):
    dwgfline_ref[i].sort(key=itemgetter(3,4),reverse=False)
    max_height=[0,max(dwgfline_ref[i][0][3][1],dwgfline_ref[i][0][4][1])]
    for j in range(len(dwgfline_ref[i])):
        if min(dwgfline_ref[i][j][3][0],dwgfline_ref[i][j][4][0]) == min(dwgfline_ref[i][0][3][0],dwgfline_ref[i][0][4][0]):
            if dwgfline_ref[i][j][3][1] > max_height[1] or dwgfline_ref[i][j][4][1] > max_height[1]:
                max_height=[j,max(dwgfline_ref[i][j][3][1],dwgfline_ref[i][j][4][1])]
        else : break
    ref_line=dwgfline_ref[i][max_height[0]]
    dwg_coor.append([ref_line[3][0],ref_line[3][1],ref_line[4][0],ref_line[4][1]])

# %%
#coordinate adjustment equation
scale=[]
x_const=[]
y_const=[]
pdf_ncoor=[]
case2_type=[]
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
    case2_type.append([])
    for j in range(len(arrowtype[i])):
        case2_type[-1].append([])
        case2_type[-1][-1].append(arrowtype[i][j][0]*scale[i]+x_const[i])
        case2_type[-1][-1].append(arrowtype[i][j][1]*scale[i]+y_const[i])
        case2_type[-1][-1].append(arrowtype[i][j][2]*scale[i]+x_const[i])
        case2_type[-1][-1].append(arrowtype[i][j][3]*scale[i]+y_const[i])
        case2_type[-1][-1].append(arrowtype[i][j][4].upper())

# %%
#set wall type for case 2
loop=True
count=0
while loop:
    count+=1
    if count>=len(dwgfile[0]):break
    loop=False
    for n,file in enumerate(dwgfile): 
        for text in case2_type[n]:
            for wall in dwgfile[n][2:]:
                if CheckRectangleOverlap(wall.coor,text[:-1]):
                    if wall.type==None :
                        wall.setType(text[-1][:])
                        
                    elif wall.type==text[-1][:]:
                        pass
                    else:
                        dwgfile[n]=split_wall(wall,file)
                        loop=True
                else: pass

# %% [markdown]
# ### **Line and Text Coordinate Adjustment for Case 3**

# %%
#define relation
gradient_tolerance=20
for file in dwgfile:
        filename = file[0]
        drawing_type = file[1]
        content = file[2:]
        wall_relations = {}
        for wall in content:
            for other_wall in content:
                if wall != other_wall:
                    wall_relation = None
                    wall_points,other_wall_points = [],[]
                    points_side,other_point_side = [],[]
                    for line in wall.line_member:
                        coor1=tuple(np.around(np.array(line[3][:2]),2))
                        coor2=tuple(np.around(np.array(line[4][:2]),2))
                        wall_points.append(coor1)
                        wall_points.append(coor2)
                        if line in wall.inner_side_lines:
                            points_side.append("INNER")
                            points_side.append("INNER")
                        else:
                            points_side.append("OUTER")
                            points_side.append("OUTER")
                    for line in other_wall.line_member:
                        coor1=tuple(np.around(np.array(line[3][:2]),2))
                        coor2=tuple(np.around(np.array(line[4][:2]),2))
                        other_wall_points.append(coor1)
                        other_wall_points.append(coor2)
                        if line in other_wall.inner_side_lines:
                            other_point_side.append("INNER")
                            other_point_side.append("INNER")
                        else:
                            other_point_side.append("OUTER")
                            other_point_side.append("OUTER")
                    connected_points = set(wall_points) & set(other_wall_points)
                    if len(connected_points) > 0:
                        connected_wall_side = []
                        connected_other_wall_side = []
                        #print(connected_points)
                        for i in connected_points:
                            #print(wall_points.index(i))
                            #print(other_wall_points.index(i))
                            connected_wall_side.append(points_side[wall_points.index(i)])
                            connected_other_wall_side.append(other_point_side[other_wall_points.index(i)])
                        #print(connected_wall_side)
                        #print(connected_other_wall_side)
                        if len(connected_points) == 2:
                            if abs(wall.gradient-other_wall.gradient)<=gradient_tolerance:
                                wall_relation = "I"
                            else:
                                if len(set(connected_wall_side))==2 and len(set(connected_other_wall_side))==2:
                                    wall_relation = "L"
                                elif len(set(connected_wall_side))==1 or len(set(connected_other_wall_side))==1:
                                    wall_relation = "T"
                        elif len(connected_points) == 1:
                            if abs(wall.gradient-other_wall.gradient)<=gradient_tolerance:
                                wall_relation = "I"
                            else:
                                wall_relation = "T"
                        if wall_relation!=None: wall.relation[other_wall] = wall_relation

# %%
#assign type
walls_without_type = []
check_no_type_wall_exist=True
count=0
while check_no_type_wall_exist:
    check_no_type_wall_exist=False
    count+=1
    for i,file in enumerate(dwgfile):
        filename = file[0]
        drawing_type = file[1]
        content = file[2:]
        walls_without_type.append([])
        give_up_assign_type=False
        for wall in content:
            if wall.type==None :
                I_keys = [k for k, v in wall.relation.items() if v == 'I' and k.type!=None]
                L_keys = [k for k, v in wall.relation.items() if v == 'L' and k.type!=None]
                T_keys = [k for k, v in wall.relation.items() if v == 'T' and k.type!=None]
                if len(I_keys)!=0:
                    wall.type=I_keys[0].type
                    walls_without_type[-1].append(wall)
                elif len(L_keys)!=0 :
                    for i,item in enumerate(L_keys):
                        if 'T' not in L_keys[i].relation.values():
                            wall.type=L_keys[i].type
                            walls_without_type[-1].append(wall)
                            break
                        elif 'T' in L_keys[i].relation.values() and count>=len(content):
                            wall.type=L_keys[i].type
                            walls_without_type[-1].append(wall)
                elif len(T_keys)!=0 :
                    wall.type=T_keys[0].type
                    walls_without_type[-1].append(wall)
            if wall.type==None: 
                check_no_type_wall_exist=True
                if count==len(content)*10:
                    print("Cannot assign the type of some walls in "+drawing_type[:-1]+" ["+filename+"]")
                    give_up_assign_type=True
                    break
    if give_up_assign_type:
        print("Continue processing the data....")
        break

# %% [markdown]
# ### **Calculate Length and Thickness**

# %%
#Calculate and print result
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
#Calculate and print result
all_wall_thickness={}
all_wall_length={}
def calc_result():
    global dwgfile,all_wall_thickness,all_wall_length
    all_wall_thickness={}
    all_wall_length={}
    for f in dwgfile:
        if f[1] == "Plan Drawings":
            for wall in f[2:]:
                try:all_wall_length[wall.type]+=wall.length
                except:all_wall_length[wall.type]=wall.length
                try:all_wall_thickness[wall.type].extend(wall.thickness)
                except:all_wall_thickness[wall.type]=copy.copy(wall.thickness)
    print("Wall length for each type :")
    for type in all_wall_length:
        all_wall_length[type]=round(all_wall_length[type],2)
        print("wall_type "+str(type)+" / "+"wall_length="+str(all_wall_length[type]))
    print("Wall thickness for each type :")
    for type in all_wall_thickness:
        all_wall_thickness[type] = [round(x, 2) for x in all_wall_thickness[type] if x != 0]  # Round to 2 decimal places and remove zero values
        all_wall_thickness[type] = list(set(all_wall_thickness[type])) # Remove duplicate elements
        print("wall_type "+str(type)+" / "+"wall_thickness="+str(all_wall_thickness[type])[1:-1])
        if len(all_wall_thickness[type])>1:print("There is an inconsistency in the thickness of wall type "+str(type)+", please check it on the window")
    return all_wall_thickness, all_wall_length
all_wall_thickness, all_wall_length = calc_result()


# %% [markdown]
# ### **Export to XML** 

# %%
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
jpglayout = os.path.join(downloads_path, "Plan_Layout.jpg")

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
    global all_wall_thickness, all_wall_length

    tree, root = create_or_read_xml(file_path)

    plans = root.find(".//Drawing[@description='平面圖']")
    if plans is None:
        plans = ET.SubElement(root, "Drawing", description='平面圖')

    all_wall_type= list(set(all_wall_thickness.keys()) | set(all_wall_length.keys()))
    all_wall_type=sorted(all_wall_type, key=lambda x: (x is None, x or float('inf')))

    for type in all_wall_type:
        try:
            length = all_wall_length[type]
        except:
            length=[0]
        try:
            thickness = all_wall_thickness[type]
        except:
            thickness=[0]
        if length==[0] and thickness==[0]:
            continue
        if check_attribute_exists(plans, "description", "TYPE "+str(type)):
            continue
        # Create a new WorkItemType element
        work_item_type = ET.SubElement(plans, "WorkItemType", description="TYPE "+str(type))
            # Create a new DiaphragmWall element
        DiaphragmWall = ET.SubElement(work_item_type, "DiaphragmWall", description="連續壁")
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
        length_value.text = str(length)
                # Create a new Depth element
        depth = ET.SubElement(DiaphragmWall, "Depth", description="設計深度")
        depth_value = ET.SubElement(depth, "Value", unit="m")
                # Create a new Thickness element
        thickness_element = ET.SubElement(DiaphragmWall, "Thickness", description="厚度")
        thickness_value = ET.SubElement(thickness_element, "Value", unit="m")
        thickness_value.text = str(thickness)[1:-1]

    # 將xml檔案寫入
    tree.write(file_path, encoding="utf-8")

    print("The XML file has been saved at : " + file_path)

    return

def save_jpg_layout():
    global downloads_path, jpglayout, drawings_number, dwgfile, case1_type, case2_type

    file_path = filedialog.askdirectory( title='Please choose the save location for the JPG layout image.',initialdir=downloads_path)

    try:
        downloads_path = file_path
        jpglayout = os.path.join(downloads_path, "Plan_Layout.jpg")
        print("The JPG image has been saved at : " + str(jpglayout)[:-4]+"_X.jpg")
    except Exception as e:
        print(f"Error: {e}")
        downloads_path = str(Path.home() / "Downloads")
        jpglayout = os.path.join(downloads_path, "Plan_Layout.jpg")
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
        for i in case1_type[drawings_number]:
            try:
                ax.add_patch(Rectangle((i[0], i[3]), i[2]-i[0], i[1]-i[3],facecolor=box_color[wall_type_color_check.index(i[-1])%len(box_color)]))
            except:
                wall_type_color_check.append(i[-1])
                ax.add_patch(Rectangle((i[0], i[3]), i[2]-i[0], i[1]-i[3],facecolor=box_color[wall_type_color_check.index(i[-1])%len(box_color)]))
        for i in case2_type[drawings_number]:
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




# %%
# Check Final Reading Results Part 2

def canvas_click(event):
    global line_on_canvas, selected_wall, dwgfile, case1_type, case2_type, drawing_number
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
    x_coords2 = [coord for arrow in case1_type[drawing_number] for coord in [arrow[0], arrow[2]]]
    y_coords2 = [coord for arrow in case1_type[drawing_number] for coord in [arrow[1], arrow[3]]]
    x_coords3 = [coord for arrow in case2_type[drawing_number] for coord in [arrow[0], arrow[2]]]
    y_coords3 = [coord for arrow in case2_type[drawing_number] for coord in [arrow[1], arrow[3]]]
    x_coords=x_coords1+x_coords2+x_coords3
    y_coords=y_coords1+y_coords2+y_coords3
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
            wall_label.config(text="A Wall Has Been Chosen")
            wall_type_label.config(text="Wall Type = "+str(wall.type))
            wall_length_label.config(text="Wall Length = "+str(round(wall.length,2))+" m")
            wall_thickness_label.config(text="Wall Thickness = "+str([round(x, 2) for x in wall.thickness if x != 0])[1:-1]+" m")
            return
    if selected_wall==[]:   # No wall was clicked
        wall_label.config(text="No Wall Chosen")
        wall_type_label.config(text="Wall Type = None")
        wall_length_label.config(text="Wall Length = 0 m")
        wall_thickness_label.config(text="Wall Thickness = 0 m")

def on_type_select(event):
    global wall_type_color_check
    selected_index = color_legend_listbox.curselection()
    if selected_index[0] in range(0,len(wall_type_color_check)):
        color_legend_listbox.selection_clear(selected_index)

def change_type():
    global drawing_number, selected_wall, wall_type_color_check, dwgfile, all_wall_thickness, all_wall_length
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
        all_wall_thickness, all_wall_length = calc_result()
        color_legend_listbox.delete(0, tk.END)  # Delete all items in the listbox
        table_data = "| {:^16s} | {:^12s} | {:^12s} |".format("Color Legend", "Length (m)", "Thickness (m)")
        color_legend_listbox.insert(tk.END, table_data)
        for type in wall_type_color_check:
            try:
                length = all_wall_length[type]
            except:
                length=[0]
            try:
                thickness = all_wall_thickness[type]
            except:
                thickness=[0]
            if length==[0] and thickness==[0]:continue
            table_data = "|  ———— {:^10s} | {:^12s} | {:^12s} |".format("Type "+str(type), str(length), str(thickness)[1:-1])
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
    global drawing_number, line_on_canvas, selected_wall, dwgfile, case1_type, case2_type
    selected_file = select_dwg_combobox.get()
    drawing_number = dwgfname.index(selected_file)

    # Clear the canvas
    canvas.delete("all")
    line_on_canvas=[]

    # Draw the lines on the canvas
    x_coords1 = [coord for wall in dwgfile[drawing_number][2:] for line in wall.line_member for coord in [line[3][0], line[4][0]]]
    y_coords1 = [coord for wall in dwgfile[drawing_number][2:] for line in wall.line_member for coord in [line[3][1], line[4][1]]]
    x_coords2 = [coord for arrow in case1_type[drawing_number] for coord in [arrow[0], arrow[2]]]
    y_coords2 = [coord for arrow in case1_type[drawing_number] for coord in [arrow[1], arrow[3]]]
    x_coords3 = [coord for arrow in case2_type[drawing_number] for coord in [arrow[0], arrow[2]]]
    y_coords3 = [coord for arrow in case2_type[drawing_number] for coord in [arrow[1], arrow[3]]]
    x_coords=x_coords1+x_coords2+x_coords3
    y_coords=y_coords1+y_coords2+y_coords3
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

    for arrow in case1_type[drawing_number]:
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

    for arrow in case2_type[drawing_number]:
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
    wall_length_label.config(text="Wall Length = 0 m")
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
table_data = "| {:^16s} | {:^12s} | {:^12s} |".format("Color Legend", "Length (m)", "Thickness (m)")
color_legend_listbox.insert(tk.END, table_data)
for type in wall_type_color_check:
    try:
        length = all_wall_length[type]
    except:
        length=[0]
    try:
        thickness = all_wall_thickness[type]
    except:
        thickness=[0]
    if length==[0] and thickness==[0]:continue
    table_data = "|  ———— {:^10s} | {:^12s} | {:^12s} |".format("Type "+str(type), str(length), str(thickness)[1:-1])
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

# Create a label for displaying "Wall Length"
wall_length_label = tk.Label(menu_frame, text="Wall Length = 0 m", font=("Arial", 14), fg="blue")
wall_length_label.pack(pady=0)

# Create a label for displaying "Wall Thickness"
wall_thickness_label = tk.Label(menu_frame, text="Wall Thickness = 0 m", font=("Arial", 14), fg="blue")
wall_thickness_label.pack(pady=0)

# Create buttons
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

# %% [markdown]
# Remove Redundant Files

os.remove(dirpath+"\\"+"-Layout1.pdf")
os.remove(dirpath +"\\"+ "Line Info.csv")
os.remove(dirpath +"\\"+ "Text Info.csv")
os.remove(dirpath +"\\"+ "PUBLIST.dsd")

# %% [markdown]
# ### **Export to EXE** 

# %%
"""
1. Type : >Export to Python Script in search bar
2. Open CMD in the file folder
3. Type ：
pip install pyinstaller
pyinstaller --onefile "Data Process - Plan Drawings.py" -w
pyinstaller -F "Data Process - Plan Drawings.py" --collect-all easyocr
pyinstaller "Data Process - Plan Drawings.py" --add-data "C:/Users/Ricardo/.EasyOCR/model/*;models" --hidden-import easyocr --collect-all easyocr --noconfirm
"""


