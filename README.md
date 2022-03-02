# PDF-splitter
PDF-splitter is a GUI application that's used to split 4-pages-in-1-sheet PDFs.
## Example
An input and output example is provided in the folder [examples](https://github.com/ManOnSaturn/PDF-splitter/examples).
To create the example with multiple pages per sheet,
[this tutorial](https://helpx.adobe.com/acrobat/kb/print-multiple-pages-per-sheet.html) can be followed.

The live preview

The toolbox

## Usage
For the purpose of making the program usable to anyone, you can choose between two options

**Option 1 (easy mode)**: Open the executable

You just need to download the appropriate file for your Operative System and double-click it. Check the folder Executables

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
## Tech
PDF-splitter uses a number of projects to work properly:
- [PyPDF3] - PDF I/O operations simply done in Python.
- [Ghostscript] - Compress PDFs!
- [Open-CV] - Guess where the PDF's slides are.
- [Tkinter] - The python-included GUI library.


## The idea
While i had my exams in university, some teachers provided wierdly-formatted PDFs that contain shrinked slides. With the desire of an increased readability of the latters, i have created this program. It is also easly usable by non tech-savvy students who don't want to bother with Python usage, by delivering executables.