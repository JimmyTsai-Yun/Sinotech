from lib.utils import *
from lib.utils import extract_sheetpile_type_depth
# from lib.plans_utils import convert_rgb_to_gaussian_blur, convert_rgb_to_dilate
# from lib.plans_utils import arrow_detection, ann_line_detection, line_arrow_pair, pair_ocr_with_line_arrow
# from lib.plans_utils import wall_line_detection, group_lines, segment_main_lines_with_labels, compute_wall_length
from lib.plans_utils import sheetpile_plan_brute_force
import keyboard
import pandas as pd
import numpy as np
from scipy.spatial import KDTree
from collections import Counter
from scipy.spatial.distance import cdist

# -------------------------------------------------------------------- #
# The Base_plan class is a parent class that contains the common methods
#
#
#
# -------------------------------------------------------------------- #
class Base_plan():
    def __init__(self, **kwargs) -> None:
        self.annotation_pdf_path = kwargs.get("pdf_path")
        self.wall_pdf_path = kwargs.get("pdf2_path")
        self.csv_path = kwargs.get("csv_path")
        self.output_path = kwargs.get("output_path")
        self.use_azure = kwargs.get("use_azure", False)
        if self.use_azure:
            self.client = construct_GPT4()

    def run(self):
        raise NotImplementedError("Subclasses should implement this!")
    
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
    
class Sheetpile_plan(Base_plan):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ocr_tool = OCRTool(type='en')

    def extract_data(self, annotation_img_lists, wall_img_lists):
        num_imgs: int = len(annotation_img_lists)

        responsed_list = []

        for i, ann_img in enumerate(annotation_img_lists):
            print(f"Processing image {i+1}/{num_imgs}")
            wall_img = wall_img_lists[i]

            # # convert ann_img to GaussianBlur
            # ann_guassian_img = convert_rgb_to_gaussian_blur(ann_img)
            # # extract text from GaussianBlur image
            # ann_text_info = self.ocr_tool.ocr(ann_guassian_img)
            # # 將 ann_img 做預處理，並將 ann_text 的位置塗白
            # dilate_ann_img = convert_rgb_to_dilate(ann_img, ann_text_info)
            # print("convert_rgb_to_dilate done")
            # # arrow detection
            # hori_arrow, verti_arrow, arrow_countours = arrow_detection(dilate_ann_img)
            # print("arrow_detection done")
            # # line detection
            # hori_line, verti_line, lines = ann_line_detection(dilate_ann_img)
            # print("ann_line_detection done")
            # # pair line and arrow
            # line_arrow_pair_info = line_arrow_pair(hori_line, verti_line, hori_arrow, verti_arrow, arrow_countours, lines)
            # print("line_arrow_pair done")
            # # pair ocr with line_arrow_pair
            # ocr_line_arrow_pair = pair_ocr_with_line_arrow(ann_text_info, line_arrow_pair_info, arrow_countours, lines)
            # print("pair_ocr_with_line_arrow done")

            # # wall img bhat 預處理
            # wall_dilate_img = convert_rgb_to_dilate(wall_img, [])
            # print("convert_rgb_to_dilate done")
            # # line detection
            # wall_lines = wall_line_detection(wall_dilate_img)
            # print("wall_line_detection done")
            # # line grouping according to the y axis
            # wall_grouped_lines = group_lines(wall_lines, 100)
            # print("group_lines done")

            # # Segment the main wall line according to the annotation detection result
            # segmented_data = segment_main_lines_with_labels(wall_grouped_lines, ocr_line_arrow_pair)
            # print("segment_main_lines_with_labels done")

            # # compute the wall length of each type 輸出格式：{type: length}
            # type_length_dict = compute_wall_length(segmented_data)
            # print("compute_wall_length done")

            type_length_dict = sheetpile_plan_brute_force(ann_img, wall_img, self.ocr_tool)
            
            
            responsed_list.append(type_length_dict)
        
        return responsed_list

    def run(self):
        annotation_img_lists = pdf2images(self.annotation_pdf_path, dpi=210)
        wall_img_lists = pdf2images(self.wall_pdf_path, dpi=210)

        respones_list = self.extract_data(annotation_img_lists, wall_img_lists)

        # 要把不同圖之間的相同type長度相加
        final_respones = {}
        for res in respones_list:
            for key, value in res.items():
                if key in final_respones:
                    final_respones[key] += value
                else:
                    final_respones[key] = value
        
        # 把結果印出來
        gui_dict = {}
        for key, value in final_respones.items():
            print(f"{key}: {value:.2f}m")
            single_type_result = {}
            sheetpile_type, sheetpile_depth = extract_sheetpile_type_depth(key)
            full_name = f"{sheetpile_type} {sheetpile_depth}m"
            single_type_result['Depth'] = sheetpile_depth
            single_type_result['Type'] = sheetpile_type
            single_type_result['Total length'] = "{:.2f}".format(value)
            gui_dict[full_name] = single_type_result

        # 建立GUI
        self.output_path = create_gui(gui_dict, "Sheet Pile Plan")

        # 把結果寫入xml檔案
        self.save_to_xml(final_respones)

        # 刪除暫存檔
        os.remove(self.annotation_pdf_path)
        os.remove(self.wall_pdf_path)

    def save_to_xml(self, response_dic):
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        plans = root.find(".//Drawing[@description='平面圖']")
        if plans is None:
            plans = ET.SubElement(root, "Drawing", description='平面圖')

        # 將response_list寫入平面圖子節點
        for key, value in response_dic.items():
            sheetpile_type, sheetpile_depth = extract_sheetpile_type_depth(key)
            if check_attribute_exists(plans, 'DEPTH', f"Depth {str(sheetpile_depth)}m"):
                continue
            else:
                pile = ET.SubElement(plans, 'WorkItemType', description="DEPTH", DEPTH=f"Depth {str(sheetpile_depth)}m")
                # 在 pile 底下建立Sheetpile子節點
                sheetpile = ET.SubElement(pile, 'Sheetpile', description="鋼板樁")
                # 在 sheetpile 底下建立type子節點
                type = ET.SubElement(sheetpile, 'Type', description="鋼板樁型號")
                type_value = ET.SubElement(type, 'Value')
                type_value.text = sheetpile_type
                # 在 sheetpile 底下建立length子節點
                length = ET.SubElement(sheetpile, 'Total', description="鋼板樁行進米")
                length_value = ET.SubElement(length, 'Value', unit="m")
                length_value.text = str(value)
                # 在 sheetpile 底下建立height子節點
                depth = ET.SubElement(sheetpile, 'Height', description="鋼板樁深度")
                depth_value = ET.SubElement(depth, 'Value', unit="m")
                depth_value.text = str(sheetpile_depth)

        # 將xml檔案寫入
        tree.write(self.output_path, encoding="utf-8")

# -------------------------------------------------------------------- #
class BoredPile_plan(Base_plan):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ocr_tool = OCRTool(type='en')

    def run(self):
        response_dic = {}

        img_lists = pdf_to_images(self.annotation_pdf_path, dpi=500, preprocess=False)

        for i, img in enumerate(img_lists):
            print(f"Processing image {i+1}/{len(img_lists)}")
            type_name, type_result = self.extract_data(img)
            response_dic[type_name] = type_result

        self.output_path = create_gui(response_dic, "Bored Pile Plan")

        self.save_to_xml(response_dic)

        os.remove(self.annotation_pdf_path)
        os.remove(self.csv_path)

        return

    def extract_data(self, img):
        # init the result dic
        single_type_result = {
            "type":None,
            "count":'0',
            "length":'0',
            "diameter":'0'
        }

        # image preprocessing
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img_th = cv2.threshold(img_gray, 240, 255, 0)

        # ocr
        bounds = self.ocr_tool.ocr(img_th)

        # get the type of the bored pile
        for bound in bounds:
            match = re.match(r'(\S+)cm(.*)BORED PILE TYPE (\S+)', bound[1])
            if match:
                diameter = re.sub(r'O', '0', match.group(1))
                single_type_result["diameter"] = diameter
                single_type_result["type"] = match.group(3)
                break

        def find_most_common_distance(csv_file_path):
            # 讀取 CSV 文件
            data = pd.read_csv(csv_file_path)

            # numbers of rows
            number_of_rows = data.shape[0]
            
            # 檢查數據中是否存在 x_coor 和 y_coor 欄位
            if 'x_coor' not in data.columns or 'y_coor' not in data.columns:
                return "CSV 文件中必須包含 'x_coor' 和 'y_coor' 欄位。"
            
            # 建立 KDTree 用於快速尋找最近點
            tree = KDTree(data[['x_coor', 'y_coor']])
            
            # 查詢最近的兩個鄰居的距離和索引
            distances, _ = tree.query(data[['x_coor', 'y_coor']], k=3)
            
            # 提取最近和次近鄰居的距離
            nearest_distances = distances[:, 1]
            second_nearest_distances = distances[:, 2]
            
            # 結合所有距離
            all_distances = np.concatenate((nearest_distances, second_nearest_distances))
            
            # 四捨五入距離以處理浮點數精確問題
            rounded_distances = np.round(all_distances, decimals=3)
            
            # 使用 Counter 統計最常見的距離
            distance_counts = Counter(rounded_distances)
            most_common_distance, _ = distance_counts.most_common(1)[0]
            
            return number_of_rows, most_common_distance
        
        n_points, most_common_distance = find_most_common_distance(self.csv_path)
        total_length = n_points * most_common_distance

        single_type_result["count"] = str(n_points)
        single_type_result["length"] = "{:.2f}".format(total_length)

        return single_type_result["type"], single_type_result

    def save_to_xml(self, response_dic):
        print("資料萃取結果: ", response_dic)
        print("已將資料寫入xml檔案: ", self.output_path)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        plans = root.find(".//Drawing[@description='平面圖']")
        if plans is None:
            plans = ET.SubElement(root, "Drawing", description='平面圖')
        
        # 將response_list寫入平面圖子節點
        for pile_type, pile_info in response_dic.items():
            if check_attribute_exists(plans, 'TYPE', f"{pile_type}"):
                continue
            else:
                pile = ET.SubElement(plans, 'WorkItemType', description="PILE TYPE", TYPE=f"{pile_type}")
                # 在 pile 底下建立 RowPile 子節點
                rowpile = ET.SubElement(pile, 'Rowpile', description="排樁")
                for key, value in pile_info.items():
                    if key == "type":
                        type = ET.SubElement(rowpile, 'Type', description="型式")
                        type_value = ET.SubElement(type, 'Value')
                        type_value.text = value
                    elif key == "count":
                        count = ET.SubElement(rowpile, 'Count', description="根數")
                        count_value = ET.SubElement(count, 'Value')
                        count_value.text = value
                    elif key == "length":
                        length = ET.SubElement(rowpile, 'Total', description="行進米")
                        length_value = ET.SubElement(length, 'Value', unit="m")
                        length_value.text = value
                    elif key == "diameter":
                        diameter = ET.SubElement(rowpile, 'Diameter', description="樁徑")
                        diameter_value = ET.SubElement(diameter, 'Value', unit="cm")
                        diameter_value.text = value
        
        # 將xml檔案寫入
        tree.write(self.output_path, encoding="utf-8")

class Diaphragm_plan(Base_plan):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def run(self):
        def calculate_slope(start, end):
            """計算兩點之間的斜率"""
            if end[0] - start[0] == 0:  # 避免除以零
                return float('inf')
            return (end[1] - start[1]) / (end[0] - start[0])

        def calculate_angle(slope1, slope2):
            """計算兩條線之間的角度差"""
            if slope1 == float('inf') and slope2 == float('inf'):
                return 0  # 兩條線都是垂直的
            elif slope1 == float('inf'):
                return 90  # 一條線是垂直的
            elif slope2 == float('inf'):
                return 90  # 另一條線是垂直的

            angle_rad = np.arctan(abs((slope2 - slope1) / (1 + slope1 * slope2)))  # 計算弧度
            angle_deg = np.degrees(angle_rad)  # 轉換為度
            return angle_deg

        def calculate_perpendicular_distance(line1, line2):
            """計算兩條線之間的平行距離"""
            # 提取線段的起始和結束點
            start1, end1 = np.array(line1[:2]), np.array(line1[2:])
            start2, end2 = np.array(line2[:2]), np.array(line2[2:])
            
            # 使用點到直線的距離公式
            # 直線方程為 Ax + By + C = 0
            A = end1[1] - start1[1]
            B = start1[0] - end1[0]
            C = A * start1[0] + B * start1[1]
            
            # 計算兩端點的距離
            distance1 = abs(A * start2[0] + B * start2[1] - C) / np.sqrt(A**2 + B**2)
            distance2 = abs(A * end2[0] + B * end2[1] - C) / np.sqrt(A**2 + B**2)
            
            # 取最小距離
            return min(distance1, distance2)
        
        df = pd.read_csv(self.csv_path, delimiter=',')

        # drop the last column
        df = df.iloc[:, :-1]

        # 整理資料，依據 ID 和 Layer 分組
        grouped = df.groupby(['FileName', 'ID', 'Layer'])

        # 建立一個列表來存儲每條線的起始和結束座標
        line_segments = []

        # 迭代每個分組以生成線段
        for (file_name, id_value, layer), group in grouped:
            x_coords = group['X'].values
            y_coords = group['Y'].values
            
            # 將每一對相鄰的點作為一條線段
            for i in range(len(x_coords) - 1):
                line_segments.append({
                    'FileName': file_name,
                    'ID': id_value,
                    'Layer': layer,
                    'Start_X': x_coords[i],
                    'Start_Y': y_coords[i],
                    'End_X': x_coords[i + 1],
                    'End_Y': y_coords[i + 1]
                })

        # 將線段資訊轉換為 DataFrame
        line_segments_df = pd.DataFrame(line_segments)

        # 建立一個列表來存儲每條線及其最近平行線的距離
        parallel_distances_angle = []

        # 依據 ID 和 Layer 分組
        for (file_name, id_value, layer), group in line_segments_df.groupby(['FileName', 'ID', 'Layer']):
            lines = group[['Start_X', 'Start_Y', 'End_X', 'End_Y']].values
            
            # 對於每一條線，尋找最近的平行線
            for line1 in lines:
                slope1 = calculate_slope(line1[:2], line1[2:])
                closest_distance = float('inf')  # 初始化為無窮大
                closest_line = None  # 用來儲存最近的平行線
                # 確認 line1 為水平線或垂直線
                x_distance = abs(line1[2] - line1[0])
                y_distance = abs(line1[3] - line1[1])
                if x_distance > y_distance:
                    direction1 = -1 if line1[0] > line1[2] else 1
                    is_horizontal = True
                else:
                    direction1 = -1 if line1[1] > line1[3] else 1
                    is_horizontal = False
                    
                
                for line2 in lines:
                    if np.array_equal(line1, line2):  # 跳過自身
                        continue
                    
                    slope2 = calculate_slope(line2[:2], line2[2:])
                    angle_diff = calculate_angle(slope1, slope2)

                    if angle_diff < 5:  # 若角度差小於5度，視為平行
                        if is_horizontal:
                            direction2 = -1 if line2[0] > line2[2] else 1
                        else:
                            direction2 = -1 if line2[1] > line2[3] else 1
                        if direction1 != direction2:
                            distance_value = calculate_perpendicular_distance(line1, line2)
                            if distance_value < closest_distance and distance_value > 0.05:  # 距離不為零且更近
                                closest_distance = distance_value
                                closest_line = line2
                
                # 如果找到最近的平行線，儲存其資訊
                if closest_line is not None:
                    parallel_distances_angle.append({
                        'FileName': file_name,
                        'ID': id_value,
                        'Layer': layer,
                        'Line_Start': (line1[0], line1[1]),
                        'Line_End': (line1[2], line1[3]),
                        'Closest_Line_Start': (closest_line[0], closest_line[1]),
                        'Closest_Line_End': (closest_line[2], closest_line[3]),
                        'Distance': closest_distance.round(2),
                        'Length': np.sqrt((line1[2] - line1[0])**2 + (line1[3] - line1[1])**2).round(3)
                    })
                else:
                    # 如果沒有找到平行線，儲存該條線的資訊，距離設為 NaN
                    parallel_distances_angle.append({
                        'FileName': file_name,
                        'ID': id_value,
                        'Layer': layer,
                        'Line_Start': (line1[0], line1[1]),
                        'Line_End': (line1[2], line1[3]),
                        'Closest_Line_Start': None,
                        'Closest_Line_End': None,
                        'Distance': None,
                        'Length': np.sqrt((line1[2] - line1[0])**2 + (line1[3] - line1[1])**2).round(3)
                    })

        # 將結果轉為 DataFrame 以便顯示
        parallel_distances_angle_df = pd.DataFrame(parallel_distances_angle)

        # 計算每組的線段長度總和和最常出現的距離
        result_df = parallel_distances_angle_df.groupby(['FileName', 'Layer', 'ID']).agg(
            Total_Length=('Length', 'sum'),
            Most_Frequent_Distance=('Distance', lambda x: x.mode()[0] if not x.mode().empty else None)
        ).reset_index()

        result_df['Length'] = (result_df['Total_Length'] - 2*result_df['Most_Frequent_Distance'])/2
        result_df['Length'] = result_df['Length'].round(1)

        # add the the total length of the line with the same layer
        final_df = result_df.groupby(['Layer']).agg(
            Total_Length=('Length', 'sum'),
            Thickness=('Most_Frequent_Distance', lambda x: x.mode()[0] if not x.mode().empty else None)
        ).reset_index()

        result_dir = {}
        for index, row in final_df.iterrows():
            result_dir[row['Layer']] = {'Length' : round(row['Total_Length'], 2)}
            result_dir[row['Layer']]['Thickness'] = row['Thickness']

        self.output_path = create_gui(result_dir, "Diaphragm Wall Plan")

        self.save_to_xml(result_dir)

        os.remove(self.csv_path)

    def save_to_xml(self, response_dic):
        print("已將資料寫入xml檔案: ", self.output_path)
        # 檢查是否已經有xml檔案，若有則讀取，若無則創建
        tree, root = create_or_read_xml(self.output_path)
        # 檢查是否有plans子節點，若無則創建，若有則刪除
        plans = root.find(".//Drawing[@description='平面圖']")
        if plans is None:
            plans = ET.SubElement(root, "Drawing", description="平面圖")

        # 將response_list寫入配筋圖子節點
        for wall_type, wall_info in response_dic.items():
            wall_thickness = wall_info['Thickness']
            wall_length = wall_info['Length']
            if check_attribute_exists(plans, 'description', "TYPE "+str(wall_type[5:])):
                continue
            else:
                WorkItemType = ET.SubElement(plans, 'WorkItemType', description="TYPE "+str(wall_type[5:]))
                DiaphragmWall = ET.SubElement(WorkItemType, "DiaphragmWall", description="連續壁")

                Thickness = ET.SubElement(DiaphragmWall, 'Thickness', description="厚度")
                Thickness_value = ET.SubElement(Thickness, 'Value', unit="m")
                Thickness_value.text = str(wall_thickness)

                Length = ET.SubElement(DiaphragmWall, 'Length', description="行進米")
                Length_value = ET.SubElement(Length, 'Value', unit="m")
                Length_value.text = str(wall_length)
        
        # 寫入xml檔案，utf-8編碼
        tree.write(self.output_path, encoding="utf-8")