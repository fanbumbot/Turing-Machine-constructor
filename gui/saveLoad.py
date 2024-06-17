from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView

from saveload import *

import os
import sys

from relativePath import RelativePath

from userGuide import *

class SaveWarning(Popup):
    def __init__(self, fileChooser:'SaveFileChooser', filePath: str, *args):
        super(SaveWarning, self).__init__(*args)
        
        self.fileChooser = fileChooser
        self.filePath = filePath

    def Confirm(self):
        self.fileChooser.SaveConfirm(self.filePath)
        self.dismiss()
    def Cancel(self):
        self.dismiss()

class MyFileChooser(Popup):
    def __init__(self, machine:ControlledTuringMachine, callbackAction = None, *args):
        super(MyFileChooser, self).__init__(*args)
        
        self.machine = machine
        self.startDirectory = os.getcwd()
        
        self.chooser:FileChooserIconView = self.ids["FileChooser"]
        
        self.chooser.path = self.startDirectory
        
        self.callbackAction = callbackAction
        
    def SetInfo(self, text: str):
        self.ids["Info"].text = text

    def select(self, *args):
        self.SetInfo("")
        try:
            self.ids["Input"].text = os.path.basename(args[1][0])
        except:
            return
        
    def Action(self):
        if self.callbackAction != None:
            self.callbackAction(os.path.join(self.chooser.path, self.ids["Input"].text))
        
class SaveFileChooser(MyFileChooser):
    def __init__(self, machine:ControlledTuringMachine, *args):
        super(SaveFileChooser, self).__init__(machine, self.Save, *args)
        
        self.saving:SavingTuringMachine = SavingTuringMachine(machine)
        
        self.ids["Action"].text = "Сохранить"
        self.title = "Сохранение проекта"
        
        SetHelpState(IDH_TOPIC_SOKHRANENIE_PROEKTA)
        
    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def Save(self, filePath):
        if len(os.path.basename(filePath)) == 0:
            self.SetInfo("Введена пустая строка")
        elif not os.path.exists(filePath):
            self.saving.Save(filePath)
            self.dismiss()
        else:
            SaveWarning(self, filePath).open()
            
    def SaveConfirm(self, filePath):
        self.saving.Save(filePath)
        self.dismiss()
        
class LoadFileChooser(MyFileChooser):
    def __init__(self, machine:ControlledTuringMachine, *args):
        super(LoadFileChooser, self).__init__(machine, self.Load, *args)
        
        self.loading:LoadingTuringMachine = LoadingTuringMachine(machine)
        
        self.ids["Action"].text = "Загрузить"
        self.title = "Загрузка проекта"
        
        SetHelpState(IDH_TOPIC_ZAGRUZKA_PROEKTA)
        
    def on_dismiss(self):
        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
    def Load(self, filePath):
        if not os.path.exists(filePath):
            self.SetInfo("Файла с таким названием не существует")
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        elif not self.loading.Load(filePath):
            self.SetInfo("Не удалось загрузить данный файл")
            SetHelpState(IDH_TOPIC_AVARIJNYE_SITUATSII)
        else:
            self.dismiss()