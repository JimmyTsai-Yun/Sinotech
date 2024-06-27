from eval import SheetPile_eval, Diaphragm_eval
from plan import Sheetpile_plan, Diaphragm_plan, BoredPile_plan
from rebar import SheetPile_rebar, Diaphragm_rebar, BoredPile_rebar
from structure import Diaphragm_structure, BoredPile_structure
import sys
import os
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("-t", "--task", dest="task", help="The type of retaining wall", default="None")
    parser.add_argument("-d", "--drawing_type", dest="drawing_type", help="The type of drawing", default="None")
    parser.add_argument("-p", "--pdf_path", dest="pdf_path", help="The path to the pdf", default=".\\-Layout1.pdf")
    parser.add_argument("-c", "--csv_path", dest="csv_path", help="The path to the csv", default="None")
    parser.add_argument("-o", "--output_path", dest="output_path", help="The path to the output file", default=".\\result.xml") 
    parser.add_argument("-u", "--use_azure", dest="use_azure", help="Use GPT-4", default=False, action='store_true')
    # A optional argument for the pdf2 path (plan drawing may have 2 pdfs)
    parser.add_argument("-p2", "--pdf2_path", dest="pdf2_path", help="The path to the second pdf", default=".\\-Layout2.pdf")

    args = parser.parse_args()

    class_dictionary = {
        "SheetPile": {
            "eval": SheetPile_eval,
            "plan": Sheetpile_plan,
            "rebar": SheetPile_rebar
        },
        "Diaphragm": {
            "eval": Diaphragm_eval,
            "plan": Diaphragm_plan,
            "rebar": Diaphragm_rebar,
            "structure": Diaphragm_structure
        },
        "BoredPile":{
            "plan": BoredPile_plan,
            "rebar": BoredPile_rebar,
            "structure": BoredPile_structure
        }
    }
    
    try:
        target_class = class_dictionary[args.task][args.drawing_type]
        if target_class is not None:
            object = target_class(pdf_path=args.pdf_path, csv_path=args.csv_path, 
                                  output_path=args.output_path, use_azure=args.use_azure, pdf2_path=args.pdf2_path)
            if hasattr(object, 'run'):
                
                object.run()

                print("Done")
                return
            else:
                print(f"No run method defined for {args.task} {args.drawing_type}.")
        else:
            print(f"No class found for {args.task} {args.drawing_type}.")
    except KeyError as e:
        print(f"Error: Invalid task or drawing type specified - {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return

if __name__ == '__main__':
    main()