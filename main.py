from re import S
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView

from controller import *
from gui import *
from userGuide import *

from gui.saveLoad import *

from saveload import *

import os, sys
from kivy.resources import resource_add_path, resource_find

from kivy.config import Config
Config.set('kivy','window_icon','icon.png')
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'exit_on_escape', '0')

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.machine:ControlledTuringMachine = ControlledTuringMachine(TuringMachine(),
                                TableRuleController(self.ids["GeneralField"].ids["TuringRules"]),
                                TapeController(self.ids["GeneralField"].ids["TuringTape"]),
                                MainPanelController(self.ids["GeneralField"].ids["TuringControlPanel"]))

        SetHelpState(IDH_TOPIC_OPISANIE_OPERATSIJ)
        
        self.saveload:SavingLoadingTuringMachine = SavingLoadingTuringMachine(self.machine)

    def Save(self):
        SaveFileChooser(self.machine).open()

    def Load(self):
        LoadFileChooser(self.machine).open()

    def Help(self):
        OpenHelp(IDH_TOPIC_VVEDENIE, False)
        
class UIApp(App):
    #Отключение настроек на f1, замена на контекстную справку
    def open_settings(self, *largs):
        OpenHelp(GetHelpState())
    def build(self):
        self.icon = "icon.png"
        self.title = "Конструктор машины Тьюринга"
        screen = MainScreen()
        return screen

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    UIApp().run()
