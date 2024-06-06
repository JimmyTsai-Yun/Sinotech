import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def create_gui(data_dict, table_name):

    def save_to_new_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".xml", 
                                                 filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
        if file_path:
            print(f"New file path: {file_path}")
            root.selected_file_path = file_path
            root.quit()  # 使主循環退出
            root.destroy()  # 銷毀窗口

    def save_to_existing_file():
        file_path = filedialog.askopenfilename(defaultextension=".xml",
                                               filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
        if file_path:
            print(f"Existing file path: {file_path}")
            root.selected_file_path = file_path
            root.quit()  # 使主循環退出
            root.destroy()  # 銷毀窗口

    root = tk.Tk()
    root.title(table_name)
    root.selected_file_path = None

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=1)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    second_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=second_frame, anchor="n")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    second_frame.bind("<Configure>", on_frame_configure)

    for obj, attributes in data_dict.items():
        sub_canvas = tk.Canvas(second_frame, relief="groove", bd=2)
        sub_canvas.pack(padx=5, pady=5, fill='both', expand=True)

        header = tk.Label(sub_canvas, text=obj, font=("Helvetica", 20))
        header.pack(pady = 5,side=tk.TOP, expand=True)

        for attr, value in attributes.items():
            attr_frame = tk.Frame(sub_canvas)
            attr_frame.pack(fill="x", padx=5, pady=5, expand=True)

            attr_label = tk.Label(attr_frame, text=attr+' : ', font=("Helvetica", 16))
            attr_label.pack(side=tk.LEFT, padx=5, pady=2)

            attr_entry = tk.Entry(attr_frame)
            attr_entry.insert(0, value)
            attr_entry.pack(side=tk.RIGHT, padx=5, pady=2)
        
        sub_canvas.bind('<Configure>', lambda e: sub_canvas.configure(scrollregion=sub_canvas.bbox("all")))

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    new_file_button = tk.Button(button_frame, text="存入新檔", command=save_to_new_file)
    new_file_button.pack(side=tk.LEFT, padx=5)

    existing_file_button = tk.Button(button_frame, text="寫入舊檔", command=save_to_existing_file)
    existing_file_button.pack(side=tk.LEFT, padx=5)

    root.mainloop()

    return root.selected_file_path

data = {
    "carA": {"wheel": 4, "color": "red", "speed": 100, "weight": 1000, "price": 1000000, "brand": "Toyota", "model": "Camry", "year": 2020},
    "carB": {"wheel": 4, "color": "red"},
    "carc": {"wheel": 4, "color": "red"},
    "card": {"wheel": 4, "color": "red"},
    "carf": {"wheel": 4, "color": "red"},
    "carg": {"wheel": 4, "color": "red"},
    "cary": {"wheel": 4, "color": "red"},
    "carg": {"wheel": 4, "color": "red"},
    "carh": {"wheel": 4, "color": "red"},
    # 可以添加更多的物體和屬性
}

file_path = create_gui(data, "Car Table")
print(f"Selected file path: {file_path}")