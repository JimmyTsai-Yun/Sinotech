import pdf2image
import easyocr

path = "C:\\Users\\jimmy\\Desktop\\sinotech2\\rebar_all.pdf"
images = pdf2image.convert_from_path(path, dpi=300, poppler_path='..\poppler-24.02.0\\Library\\bin')

reader = easyocr.Reader(['en'], model_storage_directory='..\\.EasyOCR\\model')
