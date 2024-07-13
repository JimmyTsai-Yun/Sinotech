import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class ListFrame(ttk.Frame):
	def __init__(self, parent, text_data, item_height):
		super().__init__(master = parent)
		self.pack(expand = True, fill = 'both')

		# widget data
		self.text_data = text_data
		self.item_number = len(text_data)
		self.list_height = self.item_number * item_height

		# canvas 
		self.canvas = tk.Canvas(self, background = 'red', scrollregion = (0,0,self.winfo_width(),self.list_height))
		self.canvas.pack(expand = True, fill = 'both')

		# display frame
		self.frame = ttk.Frame(self)
		
		for type, type_dic in self.text_data.items():
			self.create_item(type, type_dic).pack(expand = True, fill = 'both', pady =  3, padx = 10)

		# scrollbar 
		self.scrollbar = ttk.Scrollbar(self, orient = 'vertical', command = self.canvas.yview)
		self.canvas.configure(yscrollcommand = self.scrollbar.set)
		self.scrollbar.place(relx = 1, rely = 0, relheight = 1, anchor = 'ne')

		# events
		self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(-int(event.delta / 60), "units"))
		self.bind('<Configure>', self.update_size)

	def update_size(self, event):
		if self.list_height >= self.winfo_height():
			height = self.list_height
			self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(-int(event.delta / 60), "units"))
			self.scrollbar.place(relx = 1, rely = 0, relheight = 1, anchor = 'ne')
		else:
			height = self.winfo_height()
			self.canvas.unbind_all('<MouseWheel>')
			self.scrollbar.place_forget()
		
		self.canvas.create_window(
			(0,0), 
			window = self.frame, 
			anchor = 'nw', 
			width = self.winfo_width(), 
			height = height)
	
	def create_item(self, type_name, type_dic):
		# create a frame with border
		frame = ttk.Frame(self.frame, borderwidth = 1, relief = 'solid')

        # create and apply a style for the type name label
		style = ttk.Style()
		style.configure('TypeName.TLabel', background='lightgray', anchor='center')

		# the number of keys in the dictionary
		num_keys = len(type_dic)
		# grid layout
		for i in range(num_keys+1):
			frame.rowconfigure(i, weight = 1)
		frame.columnconfigure((0,1,2,3), weight = 1)

		# widgets
		ttk.Label(frame, text = f'{type_name}', style='TypeName.TLabel').grid(row = 0, column = 0, rowspan = num_keys, sticky = 'nsew')

		for index, key in enumerate(type_dic.keys()):
			ttk.Label(frame, text = f'{key}', anchor='center').grid(row = index, column = 1, sticky = 'nsew')
			ttk.Label(frame, text = f':', anchor='center').grid(row = index, column = 2, sticky = 'nsew')
			ttk.Label(frame, text = f'{type_dic[key]}').grid(row = index, column = 3, sticky = 'nsew')
		return frame

def create_gui(data_dict, table_name):
    def save_to_new_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
        if file_path:
            print(f"New file path: {file_path}")
            window.selected_file_path = file_path
            window.quit()  # 使主循環退出
            window.destroy()  # 銷毀窗口

    def save_to_existing_file():
        file_path = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
        if file_path:
            print(f"Existing file path: {file_path}")
            window.selected_file_path = file_path
            window.quit()  # 使主循環退出
            window.destroy()  # 銷毀窗口

    # setup
    window = tk.Tk()
    window.title(table_name)
    window.selected_file_path = None  # 初始化選擇的檔案路徑
    window.update_idletasks()
    width = 500
    height = 400
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # create a frame for the list
    main_frame = ttk.Frame(window)
    main_frame.pack(fill=tk.BOTH, expand=True)  # 設置主框架

    # create a frame for save and load buttons (should be in the bottom of the window)
    button_frame = ttk.Frame(window)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)  # 設置按鈕框架

    new_file_button = tk.Button(button_frame, text="存入新檔", command=save_to_new_file)
    new_file_button.pack(side=tk.RIGHT, padx=5)

    existing_file_button = tk.Button(button_frame, text="寫入舊檔", command=save_to_existing_file)
    existing_file_button.pack(side=tk.RIGHT, padx=5)

    # You need to define or import the ListFrame class or use another way to display data
    list_frame = ListFrame(main_frame, data_dict, 80)

    window.mainloop()

    return window.selected_file_path

data = {
    "TypeT1": {"strength": 4200, "Depth": 18500, "Diameter": 800},
    "TypeT2": {"strength": 4200, "Depth": 18500, "Diameter": 600},
    "TypeT3": {"strength": 4200, "Depth": 18500, "Diameter": 800},
    "TypeT4": {"strength": 4200, "Depth": 18500, "Diameter": 800},
    "TypeT5": {"strength": 4200, "Depth": 18500, "Diameter": 800},
    
    }

file_path = create_gui(data, "Bored Pile Table")

# def create_gui(data_dict, table_name):

#     def save_to_new_file():
#         file_path = filedialog.asksaveasfilename(defaultextension=".xml", 
#                                                  filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
#         if file_path:
#             print(f"New file path: {file_path}")
#             root.selected_file_path = file_path
#             root.quit()  # 使主循環退出
#             root.destroy()  # 銷毀窗口

#     def save_to_existing_file():
#         file_path = filedialog.askopenfilename(defaultextension=".xml",
#                                                filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
#         if file_path:
#             print(f"Existing file path: {file_path}")
#             root.selected_file_path = file_path
#             root.quit()  # 使主循環退出
#             root.destroy()  # 銷毀窗口

#     root = tk.Tk()
#     root.title(table_name)
#     root.selected_file_path = None

#     main_frame = tk.Frame(root)
#     main_frame.pack(fill=tk.BOTH, expand=1)

#     canvas = tk.Canvas(main_frame)
#     canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

#     scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
#     scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=1)

#     canvas.configure(yscrollcommand=scrollbar.set)
#     canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

#     second_frame = tk.Frame(canvas)
#     canvas.create_window((0, 0), window=second_frame, anchor="n")

#     def on_frame_configure(event):
#         canvas.configure(scrollregion=canvas.bbox("all"))

#     second_frame.bind("<Configure>", on_frame_configure)

#     for obj, attributes in data_dict.items():
#         sub_canvas = tk.Canvas(second_frame, relief="groove", bd=2)
#         sub_canvas.pack(padx=5, pady=5, fill='both', expand=True)

#         header = tk.Label(sub_canvas, text=obj, font=("Helvetica", 20))
#         header.pack(pady = 5,side=tk.TOP, expand=True)

#         for attr, value in attributes.items():
#             attr_frame = tk.Frame(sub_canvas)
#             attr_frame.pack(fill="x", padx=5, pady=5, expand=True)

#             attr_label = tk.Label(attr_frame, text=attr+' : ', font=("Helvetica", 16))
#             attr_label.pack(side=tk.LEFT, padx=5, pady=2)

#             attr_entry = tk.Entry(attr_frame)
#             attr_entry.insert(0, value)
#             attr_entry['state'] = 'readonly'  # 使輸入框變為只讀
#             attr_entry.pack(side=tk.RIGHT, padx=5, pady=2)
        
#         sub_canvas.bind('<Configure>', lambda e: sub_canvas.configure(scrollregion=sub_canvas.bbox("all")))

#     button_frame = tk.Frame(root)
#     button_frame.pack(pady=10)

#     new_file_button = tk.Button(button_frame, text="存入新檔", command=save_to_new_file)
#     new_file_button.pack(side=tk.LEFT, padx=5)

#     existing_file_button = tk.Button(button_frame, text="寫入舊檔", command=save_to_existing_file)
#     existing_file_button.pack(side=tk.LEFT, padx=5)

#     root.mainloop()

#     return root.selected_file_path

# data = {
#     "TypeT1": {"strength": 4200, "Depth": 18500, "Diameter": 800},
#     "TypeT2": {"strength": 4200, "Depth": 18500, "Diameter": 600},
#     "TypeT3": {"strength": 4200, "Depth": 18500, "Diameter": 800},
#     "TypeT4": {"strength": 4200, "Depth": 18500, "Diameter": 800},
#     "TypeT5": {"strength": 4200, "Depth": 18500, "Diameter": 800},
#     # 可以添加更多的物體和屬性
# }

# file_path = create_gui(data, "Bored Pile Table")
# print(f"Selected file path: {file_path}")