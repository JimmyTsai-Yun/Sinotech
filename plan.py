from lib.utils import *
# from lib.plans_utils import convert_rgb_to_gaussian_blur, convert_rgb_to_dilate
# from lib.plans_utils import arrow_detection, ann_line_detection, line_arrow_pair, pair_ocr_with_line_arrow
# from lib.plans_utils import wall_line_detection, group_lines, segment_main_lines_with_labels, compute_wall_length
from lib.plans_utils import sheetpile_plan_brute_force
import keyboard

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

        self.save_to_xml(final_respones)

    def save_to_xml(self, response_list):
        print(response_list)

class Diaphragm_plan(Base_plan):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def run(self):
        pass