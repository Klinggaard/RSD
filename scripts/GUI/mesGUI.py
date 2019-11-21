#!/usr/bin/env python3
import rootpath
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from scripts.GUI.MesControl import MesControl
from scripts.GUI.OEEScreen import OEEScreen
from scripts.GUI.MesOrderScreen import MesOrderScreen
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from scripts.execute import main_thread_loop
from scripts.finite_state_machine import FiniteStateMachine as FSM
import threading
import json

#Set window size
Window.size = (1853, 1016)
#Set to true for fullscreen
Window.fullscreen = False
Window.clearcolor = (1,1,1,1)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

projectPath = rootpath.detect()
Builder.load_file(projectPath + "/scripts/GUI/mesGUI.kv")

class Menu(BoxLayout):
    manager = ObjectProperty(None)


class Manager(ScreenManager):
    controlScreen = ObjectProperty(None)
    OEEScreen = ObjectProperty(None)
    orderScreen = ObjectProperty(None)


class MainApp(App):
    def build(self):
        return Menu()


if __name__ == '__main__':
    stateMachine = FSM(FSM.states_packml, FSM.transition)
    MainApp().run()
