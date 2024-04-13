import cv2
import numpy as np
from pdf2image import convert_from_path
import PIL
import easyocr
import os
import copy
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI
import os
import json
import base64
from mimetypes import guess_type
from roboflow import Roboflow

'''
Construct easyocr reader object
'''
def construct_easyocr_reader():
    reader = easyocr.Reader(['en'])
    return reader

'''
Construct robolow model object
'''
def construct_robolow_model():
    rf = Roboflow(api_key="AmMUXsxw896FwSFt1GP7")
    project = rf.workspace().project("sinotech")
    model = project.version(2).model
    return model

'''
Function to convert pdf to images, 
input is the path to the pdf file, output is a list of images
'''
def pdf_to_images(pdf_path, dpi=210, output_folder="./", drawing_type="sheet_pile-rebar"):
    images = convert_from_path(pdf_path, dpi=dpi)
    imgs_list = []
    for i, image in enumerate(images):
        cv2_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        _, img_th = cv2.thershold(img_gray, 240, 255, 0)
        img_blur = cv2.GaussianBlur(img_th, (5, 5), 0)
        imgs_list.append(img_blur)
        cv2.imwrite(output_folder + drawing_type + f"{i}.png", img_blur)

    return imgs_list

'''
Prepare for GPT4
Make sure there is a .env file in the root directory.
return the client object
'''
def construct_GPT4():
    load_dotenv(find_dotenv())

    api_base = os.getenv("GPT4V_ENDPOINT")
    api_key= os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = 'gpt4-vision'
    api_version = '2023-12-01-preview'

    client = AzureOpenAI(
        api_key=api_key,  
        api_version=api_version,
        base_url=f"{api_base}/openai/deployments/{deployment_name}/extensions",
    )
    return client

'''
Function to encode a local image into data URL 
input is the path to the image file, output is the data URL(string)
'''
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

'''
GPT4 call
input is the [gpt_client, data URL of the image, promt text]
output is the response from the API
'''
def GPT4_call(client, data_url, prompt_text):
    response = client.create_completion(
        model="gpt-4.0-turbo",
        prompt=prompt_text,
        data_url=data_url,
        max_tokens=100,
    )

    return response

'''
Template for the GPT4 API call
'''
def Call_GPT4_response(client, img_path, drawing_type = "sheet_pile-rebar"):
    all_type_drawings = {"sheet_pile-rebar":"Tell me the type of the sheet pile and the length of it. please response as the following template:{pile_type}:{length} e.g. SP-III:10m. just return the template, do not return any other information.",
                            "sheet_pile-eval":"Tell me if the drawing is about a sheet pile, if not return 'None', if yes tell me the type of the sheet pile and the length of it. please response as the following template:{pile_type}:{length} e.g. SP-III:10m. just return the template, do not return any other information." }
    data_url = local_image_to_data_url(img_path)
    try:
        prompt_text = all_type_drawings[drawing_type]
    except KeyError:
        return "Please enter the correct drawing type"
    response = GPT4_call(client, data_url, prompt_text)
    return response

'''
block split from result of robolow model
input is the result of the robolow model
output is the list of blocks and the corresponding images
'''
def block_split_by_roboflow(roboflow_predict_result, img):
    img_left = 80
    img_top = 80
    img_right = 2990
    img_bottom = 2400
    sorted_instance = sorted(roboflow_predict_result['predictions'], key=lambda k: k['y'])

    section_bbox_list = []
    dummy_y = 0
    temp_section_list = []

    # split the section according to y to represent each row
    for i, instance in enumerate(sorted_instance):
        x, y, w, h= instance['x'], instance['y'], instance['width'], instance['height']
        if y > (dummy_y + 100) and i != 0:
          # sort the temp section list by x and then append temp_section_list to section_bbox_list
          temp_section_list = sorted(temp_section_list, key=lambda k: k[0])
          section_bbox_list.append(copy.deepcopy(temp_section_list))
          # clear temp_section_list
          temp_section_list.clear()
          temp_section_list.append([x, y, w, h])
          dummy_y = y
        else:
          temp_section_list.append([x, y, w, h])
          dummy_y = y

    temp_section_list = sorted(temp_section_list, key=lambda k: k[0])
    section_bbox_list.append(copy.deepcopy(temp_section_list))
          
    # delete temp_section_list and dummy_y
    del temp_section_list
    del dummy_y
    
    # split each section into blocks
    block_list = []
    for i in range(len(section_bbox_list)):
        for j in range(len(section_bbox_list[i])):
            temp_block = [0,0,0,0]
            # if it is the first block
            if i == 0:
                temp_block[1] = img_top
            else:
                temp_block[1] = section_bbox_list[i-1][j][1] + section_bbox_list[i-1][j][3]/2

            # if it is the last block
            if i == len(section_bbox_list)-1:
                temp_block[3] = img_bottom
            else:
                temp_block[3] = section_bbox_list[i][j][1] + section_bbox_list[i][j][3]/2

            # if it is the left block
            if j == 0:
                temp_block[0] = img_left
            else:
                temp_block[0] = (section_bbox_list[i][j-1][0] + section_bbox_list[i][j][0])/2

            # if it is the right block
            if j == len(section_bbox_list[i])-1:
                temp_block[2] = img_right
            else:
                temp_block[2] = (section_bbox_list[i][j][0] + section_bbox_list[i][j+1][0])/2
            
            block_list.append(temp_block)

    block_images_list = []
    for i, block in enumerate(block_list):
        x, y, w, h = block

        block_img = img[int(y):int(h), int(x):int(w)]
        block_images_list.append(block_img)

    return block_list, block_images_list

'''
block split from result of ocr model
input is the result of the ocr model
output is the list of blocks and the corresponding images
'''
def block_split_by_ocr(ocr_predict_result, img, drawing_type="sheet_pile-rebar"):
    list = []
    keyword_dic = {"sheet_pile-rebar":"Sheet Pile"}
    # find keyword location
    for w in ocr_predict_result:
        if w[1].find(keyword_dic[drawing_type]) > -1:
            list.append(w[0]) # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    # sort keyword location by x1
    list.sort(key=lambda x: x[0][0]) # number_of_blocks * 4 corner points * (x, y)

    img_left = 140
    img_top = 100
    img_right = 6000
    
    # split each section into blocks
    block = []
    section_img_list = []
    for i in range(len(list)):
        temp_block = [0, img_top, 0, list[i][3][1]+60] # [x1, y1, x2, y2]
        # if it is the first block 求出x1
        if i == 0:
            temp_block[0] = img_left
        else:
            temp_block[0] = (list[i-1][0][0] + list[i-1][1][0] + list[i][0][0] + list[i][1][0])/4 # x1 + x2 /2
        
        # if it is the last block 求出x2
        if i == len(list)-1:
            temp_block[2] = img_right
        else:
            temp_block[2] = (list[i][0][0] + list[i][1][0] + list[i+1][0][0] + list[i+1][1][0])/4

        block.append(temp_block)
        section_img_list.append(img[int(temp_block[1]):int(temp_block[3]), int(temp_block[0]):int(temp_block[2])])

    return block, section_img_list