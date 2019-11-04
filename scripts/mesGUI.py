import datetime

from kivy.app import App
from kivy.factory import Factory
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from scripts.finite_state_machine import FiniteStateMachine as FSM
from kivy.uix.label import Label
from kivy.clock import Clock, mainthread
from kivy.uix.gridlayout import GridLayout
import threading
import time
from kivy.uix.image import Image
import kivy.uix.effectwidget
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
Window.clearcolor = (1,1,1,1)

from kivy.config import Config


Builder.load_file("mesGUI.kv")


class Menu(BoxLayout):
    manager = ObjectProperty(None)

def callback(instance):
    print('The button <%s> is being pressed' % instance.text)



class MesControl(Screen):

    state_machine = FSM(FSM.states_packml, FSM.transition)

    def change_state_idle_from_stopped(self, instance):
        self.state_machine.change_state('Reset', self.state_machine.state, 'Resetting')

    def change_state_idle_from_complete(self, instance):
        self.state_machine.change_state('Reset', self.state_machine.state, 'Resetting')

    def change_state_execute_from_idle(self,instance):
        self.state_machine.change_state('Start', 'Idle', 'Starting')

    def change_state_reset(self,instance):
        self.state_machine.change_state('Reset', self.state_machine.state, 'Resetting')

    def change_state_stopping(self, instance):
        self.state_machine.change_state('Stop', '*', 'Stopping')

    def change_state_clearing(self, instance):
        self.state_machine.change_state('Clear', 'Aborted', 'Clearing')

    def change_state_abort(self, instance):
        self.state_machine.change_state('Abort', '*', 'Aborting')

    def on_timeout(self, instance):
        label_text = 'PackML State:'

        self.lbl_state.text = label_text + ' ' +  self.state_machine.state

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MesControl, self).__init__(**kwargs)

        ##Setup buttons
        #ON/OFF Bars
        btn_on = Button(text='ON', background_color=[0,1,0,0.8], background_normal=' ')
        btn_off = Button(text='OFF', background_color=[1,0,0,0.8], background_normal=' ')
        btn_on.bind(on_press=callback)
        btn_off.bind(on_press=callback)

        on_off_buttons = BoxLayout(orientation='horizontal', size_hint=(0.2,0.2), pos_hint={'left':1,'top':1}, padding=[30,30,0,30], spacing=10)
        on_off_buttons.add_widget(btn_on)
        on_off_buttons.add_widget(btn_off)

        #Left collumn bars
        btn_start = Button(text='start')
        btn_reset = Button(text='reset')
        btn_stop = Button(text='stop')
        btn_clear = Button(text='clear')
        btn_abort = Button(text='abort')

        btn_start.bind(on_press=self.change_state_execute_from_idle)
        btn_reset.bind(on_press=self.change_state_reset)
        btn_stop.bind(on_press=self.change_state_stopping)
        btn_clear.bind(on_press=self.change_state_clearing)
        btn_abort.bind(on_press=self.change_state_abort)
        #btn_reset.bind(on_press=callback)

        leftButtons = BoxLayout(orientation='vertical', size_hint=(0.2, 0.8), spacing=30, pos_hint={'left': 1, 'bottom': 1}, padding=[30,0,0,30])
        leftButtons.add_widget(btn_start)
        leftButtons.add_widget(btn_reset)
        leftButtons.add_widget(btn_stop)
        leftButtons.add_widget(btn_clear)
        leftButtons.add_widget(btn_abort)

        #Add widget layers
        self.add_widget(on_off_buttons)
        self.add_widget(leftButtons)

        #Add packml state image
        self.img = Image(source='images/packml.png', size_hint=(1, 0.8), pos_hint={'right':1.1, 'center_y':0.6}, opacity=0.8)
        self.add_widget(self.img)

        #schedule a task to update a label of where it is
        self.lbl_state = Label(text='', font_size='30sp', pos_hint={ 'center_x':0.5, 'center_y':0.1})
        self.lbl_state.size_hint = [None, None]
        self.lbl_state.size =  self.lbl_state.texture_size
        self.add_widget(self.lbl_state)
        Clock.schedule_interval(self.on_timeout, 0.1)


        #Bind canvas to widget and set screen color
        self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            Color(0.75, 0.75, 0.75, 1)  # colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        #Start the main thread
        self.start_main_thread("mainThread")

    def start_main_thread(self, l_text):
        #initialize thread
        threading.Thread(target=self.main_thread_loop).start()

    def main_thread_loop(self):
        while True:
            ##BEGIN SWITCH CASE HERE, EXECUTE THE MES LOOP
            print('[State] {}'.format(self.state_machine.state))
            execute_state = self.state_machine.state
            if(execute_state == 'Starting'):
                self.state_machine.change_state('SC', 'Starting', 'Execute')
            elif(execute_state == 'Execute'):
                #Execute the main process here
                #and change the state to either: holding, suspending or completing
                self.state_machine.change_state('SC', 'Execute', 'Completing')
            elif(execute_state == 'Completing'):
                self.state_machine.change_state('SC', 'Completing', 'Complete')
            elif(execute_state == 'Resetting'):
                #Do some resetting procedure here
                self.state_machine.change_state('SC', 'Resetting', 'Idle')
            elif(execute_state == 'Aborting'):
                #Do some aborting stuff, like stopping the robot and change to aborted
                self.state_machine.change_state('SC', 'Aborting', 'Aborted')
            elif(execute_state == 'Clearing'):
                #Stop MES and do some clearing after an abort
                self.state_machine.change_state('SC', 'Clearing', 'Stopped')
            elif(execute_state == 'Stopping'):
                #Stop MES
                self.state_machine.change_state('SC', 'Stopping', 'Stopped')

            time.sleep(1)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

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


class MesOrders(Screen):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MesOrders, self).__init__(**kwargs)

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

    def on_stop(self):
        self.root.stop.set()

    def build(self):
        return Menu()


if __name__ == '__main__':
    MainApp().run()