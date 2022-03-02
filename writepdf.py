from PyPDF3 import PdfFileReader, PdfFileWriter
from tkinter.messagebox import askyesno, showerror, showinfo
import os
import locale
import webbrowser


def compress_pdf(input_file_name):
    """Compress the pdf via deletion of useless contents outside of view, which are present because of
       PyPDF3. It's done by ghostscript, so if it's not installed, the procedure will be interrupted.

    Parameters:
        input_file_name (str): File name of the file to compress.

    Returns:
        output_file_name (str): File name of the compressed file. Can be equal to None if ghostscript is not installed.

   """
    try:
        import ghostscript
    except RuntimeError:
        answer = askyesno("Compression failed!",
                          "Compression has failed because ghostscript is not installed in your system.\n\n"
                          "Do you wish to open the download page?", icon='error')

        if answer:
            webbrowser.open('https://www.ghostscript.com/releases/gsdnld.html')

        return None

    output_file_name = input_file_name[:-4] + "_compressed.pdf"
    args = [
        "ghostscript_process",  # actual value doesn't matter
        "-o" + output_file_name,
        "-sDEVICE=pdfwrite",
        "-dPDFSETTINGS=/prepress",
        input_file_name
    ]

    # arguments have to be bytes, encode them
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    ghostscript.Ghostscript(*args)
    return output_file_name


def write_pdf(file_path, output_path, pages_last_paper, x_entries, y_entries, width, height, compress):
    """Using PyPDF3, the individual pages are extracted from the original pdf.

        Parameters:
            file_path (str): File name of the file to split.
            output_path (str): Path of the file where to store the splitted pdf.
            pages_last_paper (tkinter.IntVar): Pages on last slide.
            x_entries (list(tkinter.IntVar)): Rectangles' x coordinates.
            y_entries (list(tkinter.IntVar)): Rectangles' y coordinates.
            width (tkinter.IntVar): Rectangles' width.
            height (tkinter.IntVar): Rectangles' x height.
            compress(tkinter.BooleanVar): Choice on whether to compress or not.

        Returns:
            (bool): File name of the compressed file. Can be equal to None if ghostscript is not installed.

       """
    pages_last_paper = pages_last_paper.get()
    x_list = []
    y_list = []
    for i in range(len(x_entries)):
        x_list.append(x_entries[i].get())
        y_list.append(y_entries[i].get())

    width = width.get()
    height = height.get()

    readers = []
    for _ in range(4):
        readers.append(PdfFileReader(file_path, strict=True))

    page_x, page_y = readers[0].getPage(0).cropBox.getUpperLeft()
    upper_left = [page_x.as_numeric(), page_y.as_numeric()]
    n_pages = readers[0].getNumPages()
    writer = PdfFileWriter()
    for n_page in range(n_pages):
        for idx, reader in enumerate(readers):
            page = reader.getPage(n_page)
            # PyPDF has its origins in lower left, opencv in upper left
            new_upper_left = (upper_left[0] + x_list[idx], upper_left[1] - y_list[idx])
            new_lower_right = (new_upper_left[0] + width, new_upper_left[1] - height)
            page.cropBox.setUpperLeft(new_upper_left)
            page.cropBox.setLowerRight(new_lower_right)
            writer.addPage(page)
            if n_page == n_pages - 1 and pages_last_paper == idx + 1:
                break

    try:
        out_stream = open(output_path, "wb")
    except PermissionError:
        showerror("Permission error!", "No writing permission on output file.")
        return False

    writer.write(out_stream)
    out_stream.close()

    if compress.get():
        comp_pth = compress_pdf(output_path)
        if comp_pth is not None:
            os.replace(comp_pth, output_path)

    showinfo("Process completed!", "Splitted PDF has been produced.")
