import tkinter as tk
from tkinter import ttk, filedialog

import cv2
from PIL import Image, ImageTk
from image_processing import read_image, resize_image, select_area_from_image
import calibration

class Calibration_Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.frame1 = tk.LabelFrame(self, text='Upload')
        self.frame2 = tk.LabelFrame(self, text='Concentration')
        self.frame3 = tk.LabelFrame(self, text='Best Fit Line')

        self.frame1.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.frame2.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.frame3.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.original_images = []
        self.tk_images = []
        self.upload_image_frames = []
        self.calibration_objects = []
        self.concentration_entry = {}

        upload_button = tk.Button(self.frame1, text='Upload Image', command=self.upload_image)
        upload_button.pack(side='top')

        process_button = tk.Button(self.frame1, text='Process Image', command=self.process_image)
        process_button.pack(side='bottom')
    
    def upload_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        for file in files:
            self.display_frame1(file)
    
    def display_frame1(self, file):
        image = read_image(file)
        image = resize_image(image, 1)
        image = select_area_from_image(image)
        tk_image = self.cv2_to_tk(image, scale=0.1)
        self.original_images.append(image)
        self.tk_images.append(tk_image)

        frame = tk.LabelFrame(self.frame1)
        frame.pack(side='top', fill="x", expand=True, anchor='n')
        self.upload_image_frames.append(frame)

        image_label = tk.Label(frame, image=tk_image)
        image_label.image = tk_image
        image_label.pack(side='left', fill="x", expand=True)

        delete_button = tk.Button(frame, text='Delete', command=lambda im=tk_image, f=frame: self.delete_image(im, f))
        delete_button.pack(side='left')
    
    def delete_image(self, image, frame):
        frame.destroy()
        self.tk_images.remove(image)
        self.upload_image_frames.remove(frame)
        self.clear_frame2()

    def clear_frame2(self):
        for widget in self.frame2.winfo_children():
            widget.destroy()

    def process_image(self):
        self.clear_frame2()
        self.calibration_objects.clear()
        for image in self.original_images:
            calib_obj = calibration.Calibration(image)
            self.calibration_objects.append(calib_obj)
        self.display_frame2()
    
    def display_frame2(self):
        calculate_button = tk.Button(self.frame2, text='Calculate Best Fit Line', command=self.calculate_fit_line)
        calculate_button.pack(side='bottom')

        for i, calib_obj in enumerate(self.calibration_objects):
            calib_frame = tk.LabelFrame(self.frame2, text=f'Calibration {i+1}')
            calib_frame.pack(side='top', fill="x", expand=True, anchor='n')

            for j, peak in enumerate(calib_obj.peaks):
                peak_frame = tk.LabelFrame(calib_frame, text=f'Peak {j+1}')
                peak_frame.pack(side='top', fill="x", expand=True, anchor='n')
                info_frame = tk.Frame(peak_frame)
                info_frame.pack(side='left', fill="x", expand=True, anchor='n')
                tk_image = self.cv2_to_tk(resize_image(calib_obj.processed_image[j], 0.1))
                image_label = tk.Label(info_frame, image=tk_image)
                image_label.image = tk_image
                image_label.pack(side='top', fill="x", expand=True)
                # data = 'Peak Area:'
                # for color in 'RGB':
                #     data += f'\n\t{color}: {peak.peak_area[color]}'
                # data_label = tk.Label(info_frame, text=data)
                # data_label.pack(side='top', fill="x", expand=True)
                
                input_frame = tk.Frame(peak_frame)
                input_frame.pack(side='left', fill="x", expand=True, anchor='n')
                label = tk.Label(input_frame, text='Concentration:')
                label.pack(side='left')
                for k in range(len(peak.peak_area['R'])):
                    var_name = f'c_{i}_{j}_{k}'
                    self.concentration_entry[var_name] = tk.StringVar()
                    self.concentration_entry[var_name].set(k+1)
                    entry = tk.Entry(input_frame, justify='center', width=10, textvariable=self.concentration_entry[var_name])
                    entry.pack(side='left')

    def clear_frame3(self):
        for widget in self.frame3.winfo_children():
            widget.destroy()
    
    def calculate_fit_line(self):
        self.clear_frame3()
        for i, calib_obj in enumerate(self.calibration_objects):
            print(f'================= CALIB #{i} =========================')
            for j, peak in enumerate(calib_obj.peaks):
                peak.concentration.clear()
                for k in range(len(peak.peak_area['R'])):
                    peak.concentration.append(float(self.concentration_entry[f'c_{i}_{j}_{k}'].get()))
            calib_obj.calculate_fit_line()
        self.display_frame3()
    
    def display_frame3(self):
        for i, calib_obj in enumerate(self.calibration_objects):
            calib_frame = tk.LabelFrame(self.frame3, text=f'Calibration {i+1}')
            calib_frame.pack(side='top', fill="x", expand=True, anchor='n')

            for j, peak in enumerate(calib_obj.peaks):
                peak_frame = tk.LabelFrame(calib_frame, text=f'Peak {j+1}')
                peak_frame.pack(side='top', fill="x", expand=True, anchor='n')

                data = 'Best Fit Line:'
                for color in 'RGB':
                    data += f'\n\t{color}: {peak.best_fit_line[color]}'
                info_label = tk.Label(peak_frame, text=data)
                info_label.pack(side='top', fill="x", expand=True)
        
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
        root.geometry('1080x720')
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