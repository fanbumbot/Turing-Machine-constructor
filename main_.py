from kivy.app import *
from kivy.uix.boxlayout import *

class MainScreen(BoxLayout):
    pass
        
class UIApp(App):
    def build(self):
        screen = MainScreen()
        return screen

if __name__ == '__main__':
    UIApp().run()
