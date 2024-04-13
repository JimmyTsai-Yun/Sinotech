from lib.utils import *
import sys
import keyboard

class Base_eval():
    def __init__(self, **kwargs) -> None:
        self.pdf_path = kwargs.get("pdf_path")
        self.csv_path = kwargs.get("csv_path")
        self.output_path = kwargs.get("output_path")
        self.use_azure = kwargs.get("use_azure")
        if self.use_azure:
            self.clinet = construct_GPT4()

    def run(self):
        pass

    def wait_pdf(self):
        loader = Loader(self.pdf_path +" is being created. Please wait..", "PDF File has been created!", 0.05).start()
        try:
            # wait for the pdf file to be created
            while not os.path.exists(self.pdf_path):
                if keyboard.is_pressed("esc"):
                    break
            loader.stop()
            return
        except:
            return

class SheetPile_eval(Base_eval):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def run(self):
        pass

    

class Diaphragm_eval(Base_eval):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def run(self):
        pass