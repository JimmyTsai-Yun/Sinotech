import easyocr

reader = easyocr.Reader(['ch_tra', 'en'], gpu=False, model_storage_directory='.\\OCRmodel')