import cv2
import numpy as np
import tkinter as tk
from tkinter import Checkbutton, BooleanVar, IntVar
from tkinter import filedialog as fd
from tkinter.messagebox import showwarning
from PIL import Image, ImageTk
import fitz
import tempfile
import os
from writepdf import write_pdf
import sys
# import Pmw

# import ctypes
# user32 = ctypes.windll.user32
# user32.SetProcessDPIAware()
# screen_w, screen_h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

bg_color = "gray"


def save_temp_pix(page, alpha=False):
    """Save a temporary .png file. Alpha can be used to increase the precision of find_rectangles.

    Parameters:
        page (fitz.fitz.Page): Page from which generate an image.
        alpha (bool): Whether or not to include alpha channel in the image.

    Returns:
        tf.name (str): Temporary file name of the image.

   """
    pix = page.get_pixmap(alpha=alpha, annots=False)
    tf = tempfile.TemporaryFile(suffix=".png")
    pix.save(tf.name)
    return tf.name


def cv_to_photo_image(img):
    """Convert a Numpy ndarray to a PIL image.

       Parameters:
           img (numpy.ndarray): Image as a ndarray.

       Returns:
           im (PIL.Image.Image): Image as a PIL Image.

    """
    b, g, r = cv2.split(img)
    img = cv2.merge((r, g, b))
    im = Image.fromarray(img)
    return im


def find_rectangles(img):
    """Use OpenCV to find 4 biggest rectangles in a Numpy ndarray image.

        Parameters:
            img (numpy.ndarray): Image as a ndarray.

        Returns:
            rects (list(int, int, int, int)): List of 4 rectangles in the shape of (X,Y,W,H) May include dummies.

    """
    # Set non-black pixels to white to better distinguish borders
    color = (0, 0, 0)
    img = np.where((img == color).all(axis=2), 0, 255).astype(np.uint8)
    # Pre-processing for findContours
    blur = cv2.GaussianBlur(img, (9, 9), 0.5)
    edge = cv2.Canny(blur, 0, 1)

    contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        rects.append((x, y, w, h))

    rects.sort(key=lambda rect: (rect[2], rect[3]), reverse=True)  # Biggest rectangles first
    if len(rects) > 4:
        rects = rects[:4]  # take only 4 rectangles

    while len(rects) < 4:
        showwarning("Too few rectangles found", "Found less than 4 rectangles. Creating dummy/dummies.\n\n"
                                                "Pay attention to the correct ordering of the coordinates after this "
                                                "operation.")
        rects.append((0, 0, 1, 1))  # Found less rects than necessary, creating dummies

    # Sort rectangles by row, then by column. Necessary for ordering of PyPDF3's ouput
    rects.sort(key=lambda rect: (rect[1], rect[0]))
    return rects


def write_pdf_wrapper(file_path, pages_last_paper, x_list, y_list, width_iv, height_iv, compress):
    """Wrapper around write_pdf. Used to ask output file name.

        Parameters:
            file_path (str): File name of the file to split.
            pages_last_paper (tkinter.IntVar): Pages on last slide.
            x_list (list(tkinter.IntVar)): Rectangles' x coordinates.
            y_list (list(tkinter.IntVar)): Rectangles' y coordinates.
            width_iv (tkinter.IntVar): Rectangles' width.
            height_iv (tkinter.IntVar): Rectangles' x height.
            compress(tkinter.BooleanVar): Choice on whether to compress or not.

        Returns:

    """
    output_path = fd.asksaveasfilename(
        defaultextension='.pdf', filetypes=[("pdf files", '*.pdf')])
    write_pdf(file_path, output_path, pages_last_paper, x_list, y_list, width_iv, height_iv, compress)


def get_resource(resource):
    """Used to handle weird pyinstaller file loading and keep normal file loading intact.

        Parameters:
            resource (str): File name of the resource to load.

        Returns:
            (str): Full path to the resource to laod.

    """
    try:  
        base_path = sys._MEIPASS # If it's being run by pyinstaller
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, resource)

    
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PDF-splitter live preview')

        self.iconbitmap(default=get_resource("appicon_182x182.ico"))
        self.configure(bg=bg_color)
        filetypes = (
            ('PDF files', '*.pdf'),
            ('All files', '*.*')
        )
        file_path = fd.askopenfilename(filetypes=filetypes)

        doc = fitz.open(file_path)
        page = doc.load_page(0)

        pix_file_name = save_temp_pix(page, alpha=False)
        self.original_img = cv2.imread(pix_file_name)

        # Photo with alpha is helpful to distinguish slides' borders
        pix_file_name = save_temp_pix(page, alpha=True)
        self.rects = find_rectangles(cv2.imread(pix_file_name))

        self.geometry(str(self.original_img.shape[1]) + "x" + str(self.original_img.shape[0]))

        # self.resizable(width=False, height=False)
        im = cv_to_photo_image(self.original_img)
        self.python_image = ImageTk.PhotoImage(image=im)
        tk.Label(self, image=self.python_image).grid(row=0, column=0)

        self.x_list = []
        self.y_list = []
        self.width_iv = IntVar()
        self.height_iv = IntVar()
        self.start_tool_window(file_path)

    def start_tool_window(self, file_path):
        tool_window = tk.Toplevel(self)
        tool_window.resizable(width=False, height=False)
        tool_window.title('Toolbox')
        tool_window.configure(bg=bg_color)
        tool_window.geometry("350x150")

        tk.Label(tool_window, text="Rectangles", bg=bg_color).grid(row=0, column=0, columnspan=5)

        e_size = 5
        start = 1
        end = 5
        for i in range(start, end):
            # X entry
            tk.Label(tool_window, text="X", bg=bg_color).grid(row=i, column=1)
            iv = IntVar()
            iv.set(self.rects[i - start][0])
            iv.trace_add("write", self.add_rectangles)

            self.x_list.append(iv)
            tk.Entry(tool_window, width=e_size, textvariable=iv, validate="focusout").grid(row=i, column=2)

            # Y entry
            tk.Label(tool_window, text="Y", bg="gray").grid(row=i, column=3)
            iv = IntVar()
            iv.set(self.rects[i - start][1])
            iv.trace_add("write", self.add_rectangles)

            self.y_list.append(iv)
            tk.Entry(tool_window, width=e_size, textvariable=iv, validate="focusout").grid(row=i, column=4)

        # Dimensions of the rectangles
        tk.Label(tool_window, text="Dimensions", bg=bg_color).grid(row=0, column=6, columnspan=6)
        tk.Label(tool_window, text="Width", bg=bg_color).grid(row=1, column=7, padx=10)
        self.width_iv.set(max(int(l[2]) for l in self.rects))
        self.width_iv.trace_add("write", self.add_rectangles)
        tk.Entry(tool_window, width=e_size, textvariable=self.width_iv, validate="focusout").grid(row=1, column=8)
        tk.Label(tool_window, text="Height", bg=bg_color).grid(row=1, column=9)
        self.height_iv.set(max(int(l[3]) for l in self.rects))
        self.height_iv.trace_add("write", self.add_rectangles)
        tk.Entry(tool_window, width=e_size, textvariable=self.height_iv, validate="focusout").grid(row=1, column=10)
        self.add_rectangles()

        tk.Label(tool_window, text="Slides on last page", bg=bg_color).grid(row=2, column=7, columnspan=2)
        pages_last_paper = IntVar()
        pages_last_paper.set(4)
        tk.Entry(tool_window, width=e_size, textvariable=pages_last_paper, validate="focusout").grid(row=2, column=10)

        compress = BooleanVar()
        compress_button = Checkbutton(tool_window, text="Compress", variable=compress, bg="gray")
        compress_button.grid(row=3, column=8, columnspan=2)

        # Pmw removed 'cause of incompatibility with pyinstaller
        # if sys.version_info <= (3, 10):
        #     Pmw.initialise(tw)
        #     balloon = Pmw.Balloon(tw)
        #     balloon.bind(compress_button, "Recommended.\nCompress the file size by about 90% by deleting extra data.")

        tk.Button(tool_window, text="Start splitting",
                  command=lambda: write_pdf_wrapper(file_path, pages_last_paper, self.x_list,
                                                    self.y_list, self.width_iv, self.height_iv,
                                                    compress)).grid(row=4, column=8, columnspan=2)

    def add_rectangles(self, *args):
        img = self.original_img.copy()
        w = int(self.width_iv.get())
        h = int(self.height_iv.get())
        for i in range(len(self.x_list)):
            x = int(self.x_list[i].get())
            y = int(self.y_list[i].get())
            sub_img = img[y:y + h, x:x + w]
            gray_rect = np.ones(sub_img.shape, dtype=np.uint8) * 255
            res = cv2.addWeighted(sub_img, 0.5, gray_rect, 0.5, 1.0)
            img[y:y + h, x:x + w] = res
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        im = cv_to_photo_image(img)
        self.python_image = ImageTk.PhotoImage(image=im)
        tk.Label(self, image=self.python_image).grid(row=0, column=0)


if __name__ == "__main__":
    app = App()
    app.mainloop()
