import cv2
import os
import numpy as np
import pandas as pd
import re

def convert_rgb_to_gaussian_blur(img):
    cv2_annotation_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray_annotation_img = cv2.cvtColor(cv2_annotation_image, cv2.COLOR_BGR2GRAY)
    _, th_annotation_img = cv2.threshold (gray_annotation_img, 240, 255, 0)
    GaussianBlur_annotation_img = cv2.GaussianBlur(th_annotation_img, (5, 5), 0)
    return GaussianBlur_annotation_img

def convert_rgb_to_dilate(img, text_info):
    '''
    Preprocess the image and remove the text from the image.

    ### Parameters:
        img: np.array
            The input image in which text is to be removed.
        text_info: list
            The list of text information in the image.
    
    ### Returns:
        np.array: The preprocessed image with text removed.
    
    Raises:
        None
    '''
    gray_annotation_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, th_annotation_img = cv2.threshold(gray_annotation_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    filterSize = (2,2) # (4,4)for dpi = 300, (2,2) for dpi = 200 (6,6) for filter dpi=300
    bhat_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)

    bhat_annotation_img = cv2.morphologyEx(th_annotation_img, cv2.MORPH_BLACKHAT, bhat_kernel)

    invers_annotation_img = cv2.bitwise_not(th_annotation_img)
    sub_annotation_img = invers_annotation_img - bhat_annotation_img

    erode_kernel = np.ones((4, 4))
    erode_annotation_img = cv2.erode(sub_annotation_img, erode_kernel, iterations=1)

    # turn the pixel to 0 if it is in the bounds
    for i in range(len(text_info)):
        x1, y1 = text_info[i][0][0]
        x2, y2 = text_info[i][0][2]
        erode_annotation_img[y1:y2, x1:x2] = 0

    dilate_kernel = np.ones((5, 5))
    dilate_annotation_img = cv2.dilate(erode_annotation_img, dilate_kernel, iterations=2)

    return dilate_annotation_img

def arrow_detection(img):
    '''
    Detect the arrow in the image and categorize them into horizontal and vertical arrows.

    ### Parameters:
        img: np.array
            The input image in which arrows are to be detected.

    ### Returns:
        tuple of three lists:
            hori_arrow (list): List of indices of horizontal arrows.
            verti_arrow (list): List of indices of vertical arrows.
            arrow_contours (list): List of all the arrow contours.

    Raises:
        ValueError: If the input is not a valid image array.
    '''
    if not isinstance(img, np.ndarray):
        raise ValueError("Invalid input: img should be a numpy array.")

    try:
        arrow_contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    except Exception as e:
        print(f"Error finding contours: {e}")
        return [], []
    
    hori_arrow = []
    verti_arrow = []

    for contour in arrow_contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > h:
            hori_arrow.append(contour)
        else:
            verti_arrow.append(contour)

    return hori_arrow, verti_arrow, arrow_contours

def euclidean_distance(p1, p2):
    '''
    Calculate the Euclidean distance between two points.

    ### Parameters:
        p1: tuple
            The first point.
        p2: tuple
            The second point.

    ### Returns:
        float: The Euclidean distance between the two points.
    '''
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def ann_line_detection(img):
    '''
    Detect the lines in the image and categorize them into horizontal and vertical lines.

    ### Parameters:
        img: np.array
            The input image in which lines are to be detected.

    ### Returns:
        tuple of two lists:
            hori_line (list): List of indices of horizontal lines.
            verti_line (list): List of indices of vertical lines.

    Raises:
        ValueError: If the input is not a valid image array.
    '''
    if not isinstance(img, np.ndarray):
        raise ValueError("Invalid input: img should be a numpy array.")
    
    thinned_img = cv2.ximgproc.thinning(img)

    fld = cv2.ximgproc.createFastLineDetector()
    lines = fld.detect(thinned_img)

    check = set()
    for i in range(len(lines)):
        for j in range(len(lines)-(i+1)):
            line1 = lines[i]
            line2 = lines[i+j+1]
            if (line1[0,0] < line1[0,2] or line1[0,1] < line1[0,3]) and euclidean_distance(line1[0], line2[1]) < 10 and euclidean_distance(line1[1], line2[0]) < 3:
                check.add(i+j+1)
            elif euclidean_distance(line1[0], line2[1]) < 10 and euclidean_distance(line1[1], line2[0]) < 3:
                check.add(i)
    
    hori_line = []
    verti_line = []
    for k, line in enumerate(lines):
        if k not in check and euclidean_distance(line[0], line[1]) > 30:
            (hori_line if line[0,0]-line[0,2] > line[0,1]-line[0,3] else verti_line).append(k)
    hori_line = [i for i in hori_line if lines[i][0,0] <= lines[i][0,2]]

    return hori_line, verti_line, lines

def line_arrow_pair(hori_lines, verti_lines, hori_arrows, verti_arrows, arrow_contours, annotation_img_lines):
    '''
    Pair the lines with the arrows.

    ### Parameters:
        hori_line (list): List of indices of horizontal lines.
        verti_line (list): List of indices of vertical lines.
        hori_arrow (list): List of indices of horizontal arrows.
        verti_arrow (list): List of indices of vertical arrows.

    ### Returns:
        pd.DataFrame: The dataframe containing the pair information.
            columns: ['line_index', 'left_arrow_index', 'right_arrow_index']
    '''

    def check_horizontal_alignment(bounding_box, point, threshold):
        """
        Check if the point is horizontally aligned within the bounding box with a given threshold.
        """
        (x, y, w, h) = bounding_box
        left, right = x, x + w
        return left - threshold < point[0] < right + threshold and y < point[1] < y + h

    def check_vertical_alignment(bounding_box, point, threshold):
        """
        Check if the point is vertically aligned within the bounding box with a given threshold.
        """
        (x, y, w, h) = bounding_box
        top, bottom = y, y + h
        return x < point[0] < x + w and top - threshold < point[1] < bottom + threshold
    
    num_of_lines = len(hori_lines) + len(verti_lines)
    line_arrow_pair_df = pd.DataFrame(columns = ['left_arrow', 'right_arrow'],index = range(len(num_of_lines)))
    line_arrow_pair_df.index = hori_lines + verti_lines

    for line_idx in hori_lines:
        line = annotation_img_lines[line_idx]
        p1, p2 = (int(line[0,0]), int(line[0,1])), (int(line[0,2]), int(line[0,3]))
        for arrow_idx in hori_arrows:
            bbox = cv2.boundingRect(arrow_contours[arrow_idx])
            # Check alignment for both endpoints of the line
            if check_horizontal_alignment(bbox, p1, 2):
                line_arrow_pair_df.at[line_idx, 'left_arrow'] = arrow_idx

            elif check_horizontal_alignment(bbox, p2, 3):
                line_arrow_pair_df.at[line_idx, 'right_arrow'] = arrow_idx

    for line_idx in verti_lines:
        line = annotation_img_lines[line_idx]
        p1, p2 = (int(line[0,0]), int(line[0,1])), (int(line[0,2]), int(line[0,3]))
        for arrow_idx in verti_arrows:
            bbox = cv2.boundingRect(arrow_contours[arrow_idx])
            if check_vertical_alignment(bbox, p1, 3):
                line_arrow_pair_df.at[line_idx, 'top_arrow'] = arrow_idx
                
            elif check_vertical_alignment(bbox, p2, 3):
                line_arrow_pair_df.at[line_idx, 'bottom_arrow'] = arrow_idx
    
    line_arrow_pair_df = line_arrow_pair_df.dropna(axis='index', how='all')

    return line_arrow_pair_df

def pair_ocr_with_line_arrow(text_info, line_arrow_pair_info, arrow_contours, annotation_img_lines):
    '''
    Pair OCR text with corresponding lines and arrows, creating a dataframe of these associations.

    Parameters:
        text_info (list of tuples): Each tuple contains OCR bounding box, text, and confidence.
        line_arrow_pair_info (DataFrame): DataFrame containing information about lines and their paired arrows.
        arrow_contours (list): List of contours for arrows.
        annotation_lines (list): List of line coordinates in the image.
    
    Returns:
        DataFrame: DataFrame containing the details of paired OCR texts and lines with additional geometric info.
    '''
    pair_list = []
    key_word = 'SHEET PILE'

    # Prepare an empty DataFrame for results
    columns = ['head_x', 'head_y', 'end_x', 'end_y', 'ocr']
    pair_df = pd.DataFrame(columns=columns)

    for idx, (bbox, text, conf) in enumerate(text_info):
        if key_word in text:
            middle_point = [(bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[2][1]) // 2]
            closest_distance = float('inf')
            closest_line_idx = -1

            # Find the closest line center to the OCR text
            for line_idx in line_arrow_pair_info.index:
                line = annotation_img_lines[line_idx]
                line_center = [(line[0,0] + line[0,2]) // 2, (line[0,1] + line[0,3]) // 2]
                distance = euclidean_distance(middle_point, line_center)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_line_idx = line_idx

            # Append index pair if a line was found
            if closest_line_idx != -1:
                pair_list.append((idx, closest_line_idx))

    # Process each found pair and extract coordinates
    for text_idx, line_idx in pair_list:
        line = annotation_img_lines[line_idx]
        line_info = line_arrow_pair_info.loc[line_idx]
        line_dict = {'ocr': text_info[text_idx][1]}  # Extract text from text_info

        # Adjust coordinates based on arrow presence
        for side in ['left', 'right']:
            arrow_key = f'{side}_arrow'
            if pd.notnull(line_info[arrow_key]):
                x, y, w, h = cv2.boundingRect(arrow_contours[int(line_info[arrow_key])])
                line_dict[f'head_x' if side == 'left' else 'end_x'] = x if side == 'left' else x + w
            else:
                line_dict[f'head_x' if side == 'left' else 'end_x'] = min(line[0,0], line[0,2]) if side == 'left' else max(line[0,0], line[0,2])

        # Set y-coordinates
        line_dict['head_y'] = min(line[0,1], line[0,3])
        line_dict['end_y'] = max(line[0,1], line[0,3])

        # Append the constructed row to the DataFrame
        pair_df = pair_df.append(line_dict, ignore_index=True)

    print(pair_df)
    return pair_df

def wall_line_detection(img):
    '''
    Detect the lines in the wall image.
    '''
    thinned_img = cv2.ximgproc.thinning(img)
    fld = cv2.ximgproc.createFastLineDetector()
    wall_img_lines = fld.detect(thinned_img)
    return wall_img_lines

def group_lines(lines, y_threshold=100):
        """Group lines based on y-coordinate and connect the leftmost and rightmost lines in each group."""
        # Sort lines by the average y-coordinate
        lines.sort(key=lambda x: (x[1] + x[3]) / 2)

        # Group lines by y-coordinate with a difference threshold
        grouped_lines = []
        current_group = [lines[0]]

        for line in lines[1:]:
            if abs(((line[1] + line[3]) / 2) - ((current_group[-1][1] + current_group[-1][3]) / 2)) > y_threshold:
                grouped_lines.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)
        
        if current_group:
            grouped_lines.append(current_group)

        # For each group, find the leftmost and rightmost line and connect them
        connected_lines = []
        for group in grouped_lines:
            if len(group) == 1:
                connected_lines.append((group[0][0], group[0][1], group[0][2], group[0][3]))
                continue
            # Find the leftmost and rightmost lines
            leftmost = min(group, key=lambda x: min(x[0], x[2]))
            rightmost = max(group, key=lambda x: max(x[0], x[2]))
            # Connect the leftmost start to the rightmost end
            connected_lines.append((min(leftmost[0], leftmost[2]), 
                                    (leftmost[1] + leftmost[3]) / 2, 
                                    max(rightmost[0], rightmost[2]), 
                                    (rightmost[1] + rightmost[3]) / 2))

        return connected_lines

def segment_main_lines_with_labels(connected_lines_by_y, ocr_data):

    # Extract the bounds for the upper and lower lines
    upper_bounds = (connected_lines_by_y[0][0], connected_lines_by_y[0][2])
    lower_bounds = (connected_lines_by_y[1][0], connected_lines_by_y[1][2])

    # Determine the mid y-coordinates of upper and lower lines
    upper_mid_y = (connected_lines_by_y[0][1] + connected_lines_by_y[0][3]) / 2
    lower_mid_y = (connected_lines_by_y[1][1] + connected_lines_by_y[1][3]) / 2
    
    # Function to determine the closest main line based on y-coordinate
    def closest_main_line(y_coord):
        if abs(y_coord - upper_mid_y) < abs(y_coord - lower_mid_y):
            return 'upper'
        else:
            return 'lower'
    
    # Assign lines to upper or lower based on y-coordinate
    ocr_data['line_group'] = ocr_data.apply(lambda row: closest_main_line((row['head_y'] + row['end_y']) / 2), axis=1)

    # Extract segments for upper and lower lines
    segments_upper = ocr_data[ocr_data['line_group'] == 'upper'][['head_x', 'end_x', 'ocr']]
    segments_lower = ocr_data[ocr_data['line_group'] == 'lower'][['head_x', 'end_x', 'ocr']]

    # Segmenting logic as previously defined
    def correct_segment_main_line(bounds, segments):
        line_segments = []
        start, end = bounds
        sorted_segments = sorted(segments, key=lambda x: x['head_x'])

        # Initialize the previous end to the start of the main line
        prev_end = start

        # Iterate through sorted segments and ensure no overlap
        for segment in sorted_segments:
            current_start = max(prev_end, segment['head_x'])  # Start at the greater of previous end or current head_x
            current_end = segment['end_x']
            
            # If there's a gap between the previous end and the current start, fill it with the previous segment's label
            if current_start > prev_end:
                line_segments.append((prev_end, current_start, segment['ocr']))  # Use the first segment's label for any initial gap
            
            # Append the current segment
            line_segments.append((current_start, current_end, segment['ocr']))
            prev_end = current_end  # Update the previous end

        # Handle any remaining portion of the main line after the last segment
        if prev_end < end:
            line_segments.append((prev_end, end, sorted_segments[-1]['ocr']))  # Use the last segment's label for the final gap

        return line_segments

    # Segmenting the upper and lower lines
    segmented_upper = correct_segment_main_line(upper_bounds, segments_upper.to_dict('records'))
    segmented_lower = correct_segment_main_line(lower_bounds, segments_lower.to_dict('records'))

    # Combine and return segmented data
    segmented_data = {'upper': segmented_upper, 'lower': segmented_lower}
    return segmented_data

def compute_wall_length(segmented_data):
    '''
    Compute the wall length of each type.
    '''
    def transpose_wall_type(wall_type_string):
        match_dic = {'IlI ': 'III ',
                     'IIl': 'III ',
                     'Ili ': 'III ',
                     'Iii ': 'III ',
                     'III ': 'III ',
                     }
        pattern = r'SP-(.*?)SHEET'
        match = re.search(pattern, wall_type_string)
        if match:
            target_string =  match.group(1)
            try:
                trans_string = match_dic[target_string]
            except:
                trans_string = target_string
        # replace the original string with the new string
        return wall_type_string.replace(target_string, trans_string)

    type_length_dict = {}
    for info in segmented_data['upper']:
        length = (info[1] - info[0]) * 15/620
        wall_type = transpose_wall_type(info[2])
        if wall_type in type_length_dict:
            type_length_dict[wall_type] += length
        else:
            type_length_dict[wall_type] = length

    return type_length_dict