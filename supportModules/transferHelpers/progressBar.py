from tkinter import ttk
from tkinter.messagebox import showinfo
from .utils import Utils

class progressBar(ttk.Progressbar):

    def __init__(self, parent, optionList):
        # progressbar
        super().__init__(parent)
        
        self.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

        # label
        self.value_label = ttk.Label(parent)
        self.value_label['text'] = self.update_progress_label(optionList)
        self.value_label.grid(column=0, row=1, columnspan=2)


    def update_progress_label(self, optionList):
        return "\rProgresso: "+str(optionList[0])+"%  "+Utils.humansizeBytes(optionList[1])+"\s  "+Utils.toTime(optionList[2], optionList[1])


    def progress(self, optionList):
        print(optionList)
        if self['value'] < 100:
            self['value'] = optionList[0]
            tmpVar = self.update_progress_label(optionList)
            self.value_label['text'] = tmpVar
        else:
            showinfo(message='Download completato')