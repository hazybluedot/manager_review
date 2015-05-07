#!/usr/bin/env python3

from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from tkinter import constants
from tkinter.tix import LabelEntry
from manager_review import run

encoding_options = ( 'utf-8', 'utf-16' )
delimiter_options = { ',': ',', '<tab>': '\t' }

class Arguments:
    def __init__(self):
        self.interactive = True
        self.comments = True
        self.input_file = None
        self.gradebook = None
        self.aliases='aliases.txt'
        self.name = "Manager's Review 2"
        self.submission_points = 3

    @property
    def submission_points(self):
        return self.__submission_points

    @submission_points.setter
    def submission_points(self, val):
        try:
            self.__submission_points = float(val)
        except TypeError:
            pass
        
    @property
    def input_file(self):
        return self.__input_file

    @input_file.setter
    def input_file(self, infile):
        self.__input_file = infile
        
    @property
    def gradebook(self):
        return self.__gradebook

    @gradebook.setter
    def gradebook(self, infile):
        self.__gradebook = infile

def set_input_file(callback):
    def _wrapper():
        fname = askopenfilename(filetypes=(("CSV files", "*.csv"),
                                           ("TXT files", "*.txt"),
                                       ))
        if fname:
            callback(fname)
    return _wrapper

class FileSelect:
    def __init__(self, Frame, text, row, **kwargs):
        self.attr = text.lower().replace(' ','_')
        self.label = Label(Frame, text=text).grid(row=row, sticky=W)
        self.button = Button(Frame,
                             text="Browse",
                             command=set_input_file(lambda x: setattr(self, 'file_name', x)),
                             width=10).grid(row=row, column=1)
        self.var_choice_encoding = StringVar()
        self.var_choice_encoding.set(encoding_options[0])
        self.optionmenu_encoding = OptionMenu(Frame, self.var_choice_encoding, *encoding_options).grid(row=row,column=2)

        self.var_choice_delimiter = StringVar()
        self.var_choice_delimiter.set(',')
        self.optionmenu_delimiter = OptionMenu(Frame, self.var_choice_delimiter, *delimiter_options.keys()).grid(row=row, column=3)
        
        self.frame = Frame

    def get(self):
        return (self.file_name, self.var_choice_encoding.get(), delimiter_options[self.var_choice_delimiter.get()])
                
class Application(Frame):
    def run_with_args(self):
        self.args.name = self.item_name.get()
        self.args.submission_points = float(self.submission_points.get())
        (self.args.input_file, self.args.input_file_encoding, self.args.input_file_delimiter) = self.fileselect_input.get()
        (self.args.gradebook, self.args.gradebook_encoding, self.args.gradebook_delimiter) = self.fileselect_gradebook.get()
        return run(self.args)
        
    def createWidgets(self):

        button_opt = {'padx': 5, 'pady': 5}

        self.fileselect_input = FileSelect(self, 'input_file', 0)
        self.fileselect_gradebook = FileSelect(self, 'gradebook file', 1)

        self.label_item_name = Label(self, text="Gradebook item name").grid(row=3, sticky=W)
        self.entry_item_name = Entry(self, textvariable=self.item_name).grid(row=3, column=1)
        
        self.label_submission_points = Label(self, text="Points for submission").grid(row=4, sticky=W)
        self.entry_submission_points = Entry(self, textvariable=self.submission_points).grid(row=4, column=1)
        
        self.run = Button(self)
        self.run["text"] = "Go",
        self.run["command"] = self.run_with_args
        self.run.grid(row=5,column=0)

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.grid(row=5, column=2)
        
    def __init__(self, master=None):
        Frame.__init__(self, master, borderwidth=5)
        self.master.title("Manager's Review Grading Tool")
        self.args = Arguments()
        self.item_name = StringVar()
        self.item_name.set(self.args.name)
        self.submission_points = StringVar()
        self.submission_points.set(self.args.submission_points)
        self.grid()
        self.createWidgets()
        self.input_label = None
        #self.rowconfigure('all', minsize = 200)
        #self.columnconfigure('all', minsize = 200)
        
if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
    root.destroy()
