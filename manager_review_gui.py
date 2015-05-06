#!/usr/bin/env python3

from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from tkinter import constants
from tkinter.tix import LabelEntry
from manager_review import run

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
        
class Application(Frame):
    def run_with_args(self):
        self.args.name = self.item_name.get()
        self.args.submission_points = float(self.submission_points.get())
        return run(self.args)
        
    def createWidgets(self):

        button_opt = {'padx': 5, 'pady': 5}

        self.input_label = Label(self, text="input file").grid(row=0, sticky=W)
        self.gradebook_label = Label(self, text="gradebook file").grid(row=1, sticky=W)

        self.input_button = Button(self, text="Browse", command=self.set_input_file, width=10)  
        self.input_button.grid(row=0, column=1, **button_opt)

        self.gradebook_button = Button(self, text="Browse", command=self.set_gradebook_file, width=10)  
        self.gradebook_button.grid(row=1, column=1, **button_opt)

        self.gradebook_item_label = Label(self, text="Gradebook item name").grid(row=2, sticky=W)
        self.gradebook_itemname = Entry(self, textvariable=self.item_name).grid(row=2, column=1)

        self.label_submission_points = Label(self, text="Points for submission").grid(row=3, sticky=W)
        self.entry_submission_points = Entry(self, textvariable=self.submission_points).grid(row=3, column=1)

        self.run = Button(self)
        self.run["text"] = "Go",
        self.run["command"] = self.run_with_args
        self.run.grid(row=4,column=0)

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.grid(row=4, column=2)
        
    def set_input_file(self):
        fname = askopenfilename(filetypes=(("CSV files", "*.csv"),
                                           ))
        self.args.input_file = fname
        
    def set_gradebook_file(self):
        fname = askopenfilename(filetypes=(("CSV files", "*.csv"),
                                           ))
        self.args.gradebook = fname
        
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
