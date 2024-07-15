import tkinter as tk
from tkinter import ttk, filedialog

import cv2
from PIL import Image, ImageTk
from image_processing import read_image, resize_image, select_area_from_image

class Calibration_Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.frame1 = tk.LabelFrame(self, text='Upload')
        self.frame2 = tk.LabelFrame(self, text='Concentration')
        self.frame3 = tk.LabelFrame(self, text='Best Fit Line')

        self.frame1.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.frame2.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.frame3.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.tk_images = []
        self.upload_image_frames = []

        # Frame 1
        upload_button = tk.Button(self.frame1, text='Upload Image', command=self.upload_image)
        upload_button.pack(side='top')
    
    def upload_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        for file in files:
            self.display_image(file)
    
    def display_image(self, file):
        image = read_image(file)
        image = resize_image(image, 0.5)
        image = select_area_from_image(image)
        tk_image = self.cv2_to_tk(image, scale=1)
        self.tk_images.append(tk_image)

        image_frame = tk.LabelFrame(self.frame1)
        image_frame.pack(side='top', fill="x", expand=True)

        image_label = tk.Label(image_frame, image=tk_image)
        image_label.image = tk_image
        image_label.pack(side='left')

        delete_button = tk.Button(image_frame, text='Delete', command=self.delete_image)
        delete_button.pack(side='left', fill="x", expand=True)
    
    def delete_image(self):
        

    def cv2_to_tk(self, image, scale=1):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image = image.resize(size=(int(image.size[0]*scale), int(image.size[1]*scale)))
        image = ImageTk.PhotoImage(image)
        return image

class Mixture_Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="This is Mixture Page")
        label.pack(side="top", fill="both", expand=True)

class Hack_Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="This is Hack Page")
        label.pack(side="top", fill="both", expand=True)

class Main_GUI():
    def __init__(self):
        root = tk.Tk()
        root.geometry('1440x1024')
        root.title('Mixture Hack')

        notebook = ttk.Notebook(root)
        notebook.pack(pady=10, fill='both', expand=True)

        frame1 = Calibration_Page(notebook)
        frame2 = Mixture_Page(notebook)
        frame3 = Hack_Page(notebook)

        frame1.pack(fill='both', expand=True)
        frame2.pack(fill='both', expand=True)
        frame3.pack(fill='both', expand=True)

        notebook.add(frame1, text='Calibration')
        notebook.add(frame2, text='Mixture')
        notebook.add(frame3, text='Hack')

        root.mainloop()