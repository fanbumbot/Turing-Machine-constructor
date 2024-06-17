from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class MyLabel(Label):
    background_color = [0, 0, 0, 0]
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3])
            Rectangle(pos=self.pos, size=self.size)