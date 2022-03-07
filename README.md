<p align="center"><img src="/appicon_182x182.ico" width="150" /></p>

# PDF-splitter
PDF-splitter is a GUI application that's used to split 4-pages-in-1-sheet PDFs.
## Example
An input and output example is provided in the folder [examples](https://github.com/ManOnSaturn/PDF-splitter/tree/main/examples).
To create the example with multiple pages per sheet,
[this tutorial](https://helpx.adobe.com/acrobat/kb/print-multiple-pages-per-sheet.html) can be followed.

The live preview
<p align="center"><img src="/images/live_preview.png" width="300" /></p>

The toolbox
<p align="center"><img src="/images/toolbox.png" width="300" /></p>

## Usage
For the purpose of making the program usable to anyone, you can choose between two options

**Option 1 (easy mode)**: Open the executable

You just need to download the appropriate file for your Operative System and double-click it.
Check the folder [executables](https://github.com/ManOnSaturn/PDF-splitter/tree/main/executables)

**Option 2 (programmer  mode)**: Execute the source code

Download the project, move inside the project directory
```sh
pip install -r requirements.txt
python main.py
```
**Optional add-on**

If you don't want to have a 100MB PDF as an output, you can tick the option "compress" in the program.
In order for it to work, you need to have ghostscript installed.
Download it via [Ghostscript website](https://bit.ly/3Hv7rrO).

**How to create an executable**

On Windows, I've used pyinstaller v4.9 and executed this command:
```sh
pyinstaller main.py -F -w --name PDF-splitter-win64 --icon="appicon_182x182.ico" --add-data "appicon_182x182.ico;."
```
## Tech
PDF-splitter uses a number of projects to work properly:
- [PyPDF3] - PDF I/O operations simply done in Python.
- [Ghostscript] - Compress PDFs!
- [Open-CV] - Guess where the PDF's slides are.
- [Tkinter] - The python-included GUI library.


## The idea
While I had my exams in university, some teachers provided weirdly-formatted PDFs that contain shrunk slides. With the desire of an increased readability of the latters, I have created this program. It is also easily usable by non-tech-savvy students who don't want to bother with Python usage, by delivering executables.