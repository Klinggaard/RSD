from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from scripts.GUI.MesControl import MesControl
from scripts.GUI.MesOrders import MesOrders

#Set window size
Window.size = (1853, 1016)
Window.clearcolor = (1,1,1,1)

Builder.load_file("mesGUI.kv")

class Menu(BoxLayout):
    manager = ObjectProperty(None)


class Help(Screen):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(Help, self).__init__(**kwargs)

        ##Bind canvas to widget and set screen color
        self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            Color(0.75, 0.75, 0.75, 1)  # colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class Manager(ScreenManager):
    controlScreen = ObjectProperty(None)
    helpScreen = ObjectProperty(None)
    orderScreen = ObjectProperty(None)

class MainApp(App):
    def build(self):
        return Menu()


if __name__ == '__main__':
    MainApp().run()