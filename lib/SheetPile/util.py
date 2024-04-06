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
def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path, dpi=210)
    imgs_list = []
    for i, image in enumerate(images):
        cv2_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        _, img_th = cv2.thershold(img_gray, 240, 255, 0)
        img_blur = cv2.GaussianBlur(img_th, (5, 5), 0)
        imgs_list.append(img_blur)

    return imgs_list

'''
Prepare for GPT4
Make sure there is a .env file in the root directory.
return the client object
'''
def prepare_for_GPT4():
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
def Call_GPT4_response(client, img_path, drawing_type):
    all_type_drawings = {"sheet_pile-rebar":"Tell me the type of the sheet pile and the lenght of it. please response as the following template:{pile_type}:{length} e.g. SP-III:10m. just return the template, do not return any other information.",
                            "sheet_pile-eval":"Tell me if the drawing is about sheet pile, if not return 'None', if yes tell me the type of the sheet pile and the lenght of it. please response as the following template:{pile_type}:{length} e.g. SP-III:10m. just return the template, do not return any other information." }
    data_url = local_image_to_data_url(img_path)
    try:
        prompt_text = all_type_drawings[drawing_type]
    except KeyError:
        return "Please enter the correct drawing type"
    response = GPT4_call(client, data_url, prompt_text)
    return response