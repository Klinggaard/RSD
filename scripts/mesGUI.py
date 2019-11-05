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
from kivy.graphics import Line
from kivy.animation import Animation

from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

#Set window size
Window.size = (1853, 1016)
Window.clearcolor = (1,1,1,1)

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
        current_state = self.state_machine.state

        square_base = [682, 80, 521, 80, 521, 164, 682, 164, 682, 80]
        addition = [0,0,0,0,0,0,0,0,0,0]

        if current_state == 'Idle':
            addition = [0, 460, 0, 460, 0, 460, 0, 460, 0, 460]
        elif current_state == 'Resetting':
            addition = [0, 270, 0, 270, 0, 270, 0, 270, 0, 270]
        elif current_state == 'Stopping':
            addition = [254, 0, 254, 0, 254, 0, 254, 0, 254, 0]
        elif current_state == 'Stopped':
            addition = addition
        elif current_state == 'Clearing':
            addition = [254*2, 0, 254*2, 0, 254*2, 0, 254*2, 0, 254*2, 0]
        elif current_state == 'Aborted':
            addition = [254*3, 0, 254*3, 0, 254*3, 0, 254*3, 0, 254*3, 0]
        elif current_state == 'Aborting':
            addition = [254*4, 0, 254*4, 0, 254*4, 0, 254*4, 0, 254*4, 0]
        elif current_state == 'Complete':
            addition = [254*4, 460, 254*4, 460, 254*4, 460, 254*4, 460, 254*4, 460]
        elif current_state == 'Completing':
            addition = [254*3, 460, 254*3, 460, 254*3, 460, 254*3, 460, 254*3, 460]
        elif current_state == 'Starting':
            addition = [254, 460, 254, 460, 254, 460, 254, 460, 254, 460]
        elif current_state == 'Execute':
            addition = [254*2, 460, 254*2, 460, 254*2, 460, 254*2, 460, 254*2, 460]
        elif current_state == 'Suspending':
            addition = [254*3, 270, 254*3, 270, 254*3, 270, 254*3, 270, 254*3, 270]
        elif current_state == 'Suspended':
            addition = [254*2, 270, 254*2, 270, 254*2, 270, 254*2, 270, 254*2, 270]
        elif current_state == 'Unsuspending':
            addition = [254, 270, 254, 270, 254, 270, 254, 270, 254, 270]
        elif current_state == 'Unholding':
            addition = [254, 650, 254, 650, 254, 650, 254, 650, 254, 650]
        elif current_state == 'Held':
            addition = [254*2, 650, 254*2, 650, 254*2, 650, 254*2, 650, 254*2, 650]
        elif current_state == 'Holding':
            addition = [254 * 3, 650, 254 * 3, 650, 254 * 3, 650, 254 * 3, 650, 254 * 3, 650]

        self.line.points = [square_base[0] + addition[0], square_base[1]+ addition[1], square_base[2]+ addition[2], square_base[3]+ addition[3], square_base[4]+ addition[4], square_base[5]+ addition[5], square_base[6]+ addition[6], square_base[7]+ addition[7], square_base[8]+ addition[8], square_base[9]+ addition[9]]


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
        img = Image(source='images/packml.png', size_hint=(1, 1), pos_hint={'right':1.1, 'center_y':0.5}, opacity=0.8)
        self.add_widget(img)

        #Bind canvas to widget and set screen color
        self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            Color(0.75, 0.75, 0.75, 1)  # colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        #Create box to highligh current state
        with self.canvas:
            Color(1,0,0,0.8)
            self.line = Line()
            self.line.width = 6

        Clock.schedule_interval(self.on_timeout, 0.1)

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

            #TODO: REMOVE THIS SLEEP WHEN NOT TESTING ANYMORE
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

items_1 = {'apple', 'banana', 'pear', 'pineapple'}
items_2 = {'dog', 'cat', 'rat', 'bat'}


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, GridLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    cols = 3

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.label1_text = str(index)
        self.label2_text = data['label2']['text']
        self.ids['id_label3'].text = data['label3']['text']  # As an alternate method of assignment
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        paired_iter = zip(items_1, items_2)
        self.data = []
        for i1, i2 in paired_iter:
            d = {'label2': {'text': i1}, 'label3': {'text': i2}}
            self.data.append(d)
        # can also be performed in a complicated one liner for those who like it tricky
        # self.data = [{'label2': {'text': i1}, 'label3': {'text': i2}} for i1, i2 in zip(items_1, items_2)]


class MesOrders(Screen):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MesOrders, self).__init__(**kwargs)
        self.recycle_view = RV()
        self.add_widget(self.recycle_view)

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