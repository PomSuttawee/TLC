import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk
import cv2
import matplotlib.pyplot as plt

from image_processing import read_image, resize_image, select_area_from_image
import calibration
import mixture
import mixture_hack

class GUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title('Mixture Hack')
        self.root.geometry('1400x1024')

        self.tk_images = []
        self.upload_image_frames = []
        self.image_data = []
        self.mixture_obj = None
        self.calibration_obj = []

        # MAIN FRAME <- [UPLOAD FRAME, INPUT DATA FRAME, RESULT FRAME]
        self.main_frame = tk.Frame(self.root)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.columnconfigure(2, weight=3)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # UPLOAD FRAME
        self.upload_frame = tk.LabelFrame(self.main_frame, text='Upload Files', font=('Arial', 14))
        self.upload_frame.grid(column=0, row=0, padx=10, pady=10, sticky='NSEW')
        ## Upload Button
        self.upload_button = tk.Button(self.upload_frame, text='Upload', command=self.upload_image)
        self.upload_button.pack(side=tk.TOP, pady=10)
        ## Get Result Button
        self.result_button = tk.Button(self.upload_frame, text='Get Result!', command=self.get_result)
        self.result_button.pack(side=tk.BOTTOM, pady=10)
        ## Scroll Canvas
        self.scroll_canvas = tk.Canvas(self.upload_frame)
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ## Scroll Bar
        self.scrollbar = ttk.Scrollbar(self.upload_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        ## Scrollable Frame
        self.scrollable_frame = tk.Frame(self.scroll_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(
                scrollregion=self.scroll_canvas.bbox("all")
            )
        )
        self.scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        # INPUT DATA FRAME <- [Mixture LabelFrame, Calibration LabelFrame]
        self.data_frame = tk.LabelFrame(self.main_frame, text='Input Data', font=('Arial', 14))
        self.data_frame.grid(column=1, row=0, padx=10, pady=10, sticky='NSEW')
        ## Mixture LabelFrame
        self.mixture_frame = tk.LabelFrame(self.data_frame, text='Mixture', font=('Arial', 12))
        self.mixture_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.mixture_frame.columnconfigure(0, weight=1)
        self.mixture_frame.columnconfigure(1, weight=2)
        ## Calibration LabelFrame
        self.calibration_frame = tk.LabelFrame(self.data_frame, text='Calibration', font=('Arial', 12))
        self.calibration_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ### Scroll Canvas
        self.result_scroll_canvas = tk.Canvas(self.calibration_frame)
        self.result_scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ### Scroll Bar
        self.result_scrollbar = ttk.Scrollbar(self.calibration_frame, orient="vertical", command=self.result_scroll_canvas.yview)
        self.result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        ### Scrollable Frame
        self.result_scrollable_frame = tk.Frame(self.result_scroll_canvas)
        self.result_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.result_scroll_canvas.configure(
                scrollregion=self.result_scroll_canvas.bbox("all")
            )
        )
        self.result_scroll_canvas.create_window((0, 0), window=self.result_scrollable_frame, anchor="nw")
        self.result_scroll_canvas.configure(yscrollcommand=self.result_scrollbar.set)

        # RESULT FRAME
        self.result_frame = tk.LabelFrame(self.main_frame, text='Result', font=('Arial', 14))
        self.result_frame.grid(column=2, row=0, padx=10, pady=10, sticky='NSEW')

        self.root.mainloop()
    
    def on_closing(self):
        self.root.quit()
        self.root.destroy()

    def upload_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        for file in files:
            self.display_image(file)
    
    def display_image(self, file):
        image = read_image(file)
        image = resize_image(image, 0.5)
        image = select_area_from_image(image)
        tk_image = self.cv2_to_tk(image, scale=0.25)
        
        # Frame for display each image [2 columns, 2 rows]
        frame = tk.LabelFrame(self.scrollable_frame, text='Image '+str(len(self.tk_images)+1))
        frame.pack(pady=10, fill=tk.X, side=tk.TOP)
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=1)
        ## Image [0, 0, 2 rowspan]
        image_label = tk.Label(frame, image=tk_image)
        image_label.image = tk_image
        image_label.grid(column=0, row=0, rowspan=2, sticky='NSEW')
        ## Combobox for selecting image type [1, 0]
        combobox = ttk.Combobox(frame,state='readonly', values=["Mixture", "Calibration"])
        combobox.grid(column=1, row=0,  padx=10)
        combobox.current(1)
        ## Delete Button [1, 1]
        delete_button = tk.Button(frame, text="Delete", command=lambda im=tk_image, f=frame, cb=combobox: self.delete_image(im, f, cb))
        delete_button.grid(column=1, row=1, padx=10)
        
        # Store all data
        self.tk_images.append(tk_image)
        self.upload_image_frames.append(frame)
        self.image_data.append({'file': image, 'combobox': combobox})
    
    def delete_image(self, image, frame, combobox):
        frame.destroy()
        self.tk_images.remove(image)
        self.upload_image_frames.remove(frame)
        self.image_data = [img for img in self.image_data if img['combobox'] != combobox]
        for i, labelframe in enumerate(self.upload_image_frames):
            labelframe.configure(text=f'Image {i+1}')
    
    def get_result(self):
        self.clear_result_frame()
        self.calibration_obj = []
        for data in self.image_data:
            image = data['file']
            image_type = data['combobox'].get()
            if image_type == "Mixture":
                self.mixture_obj = mixture.Mixture(image)
            elif image_type == "Calibration":
                calib = calibration.Calibration(image)
                for i, peak in enumerate(calib.peaks):
                    concentration = self.get_concentration(calib.preprocessed_image[i]).split(' ')
                    concentration = [float(x) for x in concentration]
                    peak.concentration = concentration
                calib.calculate_fit_line()
                self.calibration_obj.append(calib)

        mixture_hack.calculate_concentration(self.mixture_obj, self.calibration_obj)

        self.display_result()
    
    def display_result(self):
        # MIXTURE
        ## IMAGE
        tk_mixture = self.cv2_to_tk(self.mixture_obj.preprocessed_image, scale=0.5)
        mixture_image = tk.Label(self.mixture_frame, image=tk_mixture)
        mixture_image.image = tk_mixture
        mixture_image.grid(column=0, row=0, sticky='NSEW')
        ## INFO
        mixture_text = "Peak Area:"
        for color in 'RGB':
            mixture_text += f'\n        {color}: {self.mixture_obj.peak_area[color]}'
        mixture_info = tk.Label(self.mixture_frame, text=mixture_text, justify=tk.LEFT)
        mixture_info.grid(column=1, row=0, sticky='NSEW')

        # CALIBRATION
        for i, calib_obj in enumerate(self.calibration_obj):
            calib_frame = tk.LabelFrame(self.result_scrollable_frame, text=f'Calibration {i+1}', font=('Arial', 10))
            calib_frame.pack(pady=10, fill=tk.X, expand=True)
            calib_frame.columnconfigure(0, weight=1)
            calib_frame.columnconfigure(1, weight=1)
            ## PEAK
            for j, peak in enumerate(calib_obj.preprocessed_image):
                peak_frame = tk.LabelFrame(calib_frame, text=f'Peak {j+1}')
                peak_frame.pack(side=tk.TOP, padx=10, pady=5, fill=tk.X, expand=True)
                ### IMAGE
                tk_peak = self.cv2_to_tk(peak, scale=0.25)
                peak_image = tk.Label(peak_frame, image=tk_peak)
                peak_image.image = tk_peak
                peak_image.grid(column=0, row=0, sticky='NSEW')
                ### INFO
                peak_area_text = "Peak Area:"
                best_fit_line_text = "\nBest Fit Line:"
                for color in 'RGB':
                    peak_area_text += f"\n        {color}: {calib_obj.peaks[j].peak_area[color]}"
                    best_fit_line_text += f"\n        {color}: {calib_obj.peaks[j].best_fit_line[color]}"

                info_text = peak_area_text + best_fit_line_text
                peak_info = tk.Label(peak_frame, text=info_text, justify=tk.LEFT)
                peak_info.grid(column=1, row=0, sticky='NSEW')
        self.calibration_obj[0].plot_peak_area()
        self.calibration_obj[0].plot_intensity()
        for peak, info in self.calibration_obj[0].plot['Peak_area'].items():
            plt.figure(info)
        plt.show()

    def clear_result_frame(self):
        for widget in self.mixture_frame.winfo_children():
            widget.destroy()
        for widget in self.result_scrollable_frame.winfo_children():
            widget.destroy()

    def cv2_to_tk(self, image, scale=1):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image = image.resize(size=(int(image.size[0]*scale), int(image.size[1]*scale)))
        image = ImageTk.PhotoImage(image)
        return image

    def get_concentration(self, image):
        self.concentration_var = tk.StringVar()

        popup = tk.Toplevel(self.root)
        popup.title("Pop-up with Image and Input")

        # Load the image
        photo = self.cv2_to_tk(resize_image(image, 0.4))

        # Create a label to display the image
        image_label = tk.Label(popup, image=photo)
        image_label.image = photo  # Keep a reference to avoid garbage collection
        image_label.pack(side=tk.TOP, pady=10)

        # Create a label for the input prompt
        prompt_label = tk.Label(popup, text="Concentration:")
        prompt_label.pack(side=tk.TOP, pady=10)

        # Create an entry widget for input
        entry = tk.Entry(popup, width=50, textvariable=self.concentration_var)
        entry.pack(side=tk.TOP, pady=10)

        # Create a button to submit the input
        submit_button = tk.Button(popup, text="Submit", command=popup.destroy)
        submit_button.pack(side=tk.TOP, pady=10)

        popup.wait_window(popup)  # Wait for the popup window to be closed
        return self.concentration_var.get()  # Return the value of the StringVar