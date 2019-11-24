#!/usr/bin/env python3
import threading
import time

import rootpath
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from scripts.finite_state_machine import FiniteStateMachine as FSM
from scripts.RobotControl import RobotControl
import logging
import json

__RED__ = [1, 0, 0, 1]
__RED_LOW__ = [0.25, 0, 0, 1]
__GREEN__ = [0, 1, 0, 1]
__GREEN_LOW__ = [0, 0.25, 0, 1]
__YELLOW__ = [1, 1, 0, 1]
__YELLOW_LOW__ = [0.25, 0.25, 0, 1]


def callback(instance):
    logging.info('[MesControl] The button <%s> is being pressed' % instance.text)


class MesControl(Screen):

    def change_state_idle_from_stopped(self, instance):
        self.state_machine.change_state('Reset', self.state_machine.state, 'Resetting')

    def change_state_idle_from_complete(self, instance):
        self.state_machine.change_state('Reset', self.state_machine.state, 'Resetting')

    def change_state_execute_from_idle(self, instance):
        self.state_machine.change_state('Start', 'Idle', 'Starting')

    def change_state_reset(self, instance):
        self.state_machine.change_state('Reset', self.state_machine.state, 'Resetting')

    def change_state_stopping(self, instance):
        self.state_machine.change_state('Stop', '*', 'Stopping')

    def change_state_clearing(self, instance):
        self.state_machine.change_state('Clear', 'Aborted', 'Clearing')

    def change_state_abort(self, instance):
        self.state_machine.change_state('Unhold', 'Held', 'Unholding')

    def lights_color(self, R, Y, G):

        if R:
            red = __RED__
        else:
            red = __RED_LOW__
        if Y:
            yellow = __YELLOW__
        else:
            yellow = __YELLOW_LOW__
        if G:
            green = __GREEN__
        else:
            green = __GREEN_LOW__

        self.btn_light1.background_color = green
        self.btn_light2.background_color = yellow
        self.btn_light3.background_color = red

    def light_tower(self, instance):
        state = self.state_machine.state
        if state == 'Stopping' or state == 'Stopped':
            self.lights_color(True, False, False)
        elif state == 'Aborting' or state == 'Aborted' or state == 'Clearing':
            if self.btn_light1.background_color == __GREEN__: #Green low color
                self.lights_color(False, False, True)
            else:
                self.lights_color(False, False, False)
        elif state == 'Resetting':
            if self.btn_light2.background_color == __YELLOW__: #Yellow low color
                self.lights_color(False, True, False)
            else:
                self.lights_color(False, False, False)
        elif state == 'Suspending' or state == 'Suspended':
            self.lights_color(False, True, False)
        elif state == 'Idle':
            if self.btn_light1.background_color == __GREEN__:
                self.lights_color(False, False, False)
            else:
                self.lights_color(False, False, True)
        elif state == 'Starting' or state == 'Execute' or state == 'Unholding' or state == 'Unsuspending':
            self.lights_color(False, False, True)
        elif state == 'Holding' or state == 'Held':
            if self.btn_light3.background_color == __RED__ and self.btn_light2.background_color == __YELLOW__ :
                self.lights_color(True, True, False)
            else:
                self.lights_color(False, False, False)

    def on_timeout(self, instance):
        current_state = self.state_machine.state
        #Update box placement
        square_base = [682, 80, 521, 80, 521, 164, 682, 164, 682, 80]
        addition = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        if current_state == 'Idle':
            addition = [0, 460, 0, 460, 0, 460, 0, 460, 0, 460]
        elif current_state == 'Resetting':
            addition = [0, 270, 0, 270, 0, 270, 0, 270, 0, 270]
        elif current_state == 'Stopping':
            addition = [254, 0, 254, 0, 254, 0, 254, 0, 254, 0]
        elif current_state == 'Stopped':
            addition = addition
        elif current_state == 'Clearing':
            addition = [254 * 2, 0, 254 * 2, 0, 254 * 2, 0, 254 * 2, 0, 254 * 2, 0]
        elif current_state == 'Aborted':
            addition = [254 * 3, 0, 254 * 3, 0, 254 * 3, 0, 254 * 3, 0, 254 * 3, 0]
        elif current_state == 'Aborting':
            addition = [254 * 4, 0, 254 * 4, 0, 254 * 4, 0, 254 * 4, 0, 254 * 4, 0]
        elif current_state == 'Complete':
            addition = [254 * 4, 460, 254 * 4, 460, 254 * 4, 460, 254 * 4, 460, 254 * 4, 460]
        elif current_state == 'Completing':
            addition = [254 * 3, 460, 254 * 3, 460, 254 * 3, 460, 254 * 3, 460, 254 * 3, 460]
        elif current_state == 'Starting':
            addition = [254, 460, 254, 460, 254, 460, 254, 460, 254, 460]
        elif current_state == 'Execute':
            addition = [254 * 2, 460, 254 * 2, 460, 254 * 2, 460, 254 * 2, 460, 254 * 2, 460]
        elif current_state == 'Suspending':
            addition = [254 * 3, 270, 254 * 3, 270, 254 * 3, 270, 254 * 3, 270, 254 * 3, 270]
        elif current_state == 'Suspended':
            addition = [254 * 2, 270, 254 * 2, 270, 254 * 2, 270, 254 * 2, 270, 254 * 2, 270]
        elif current_state == 'Unsuspending':
            addition = [254, 270, 254, 270, 254, 270, 254, 270, 254, 270]
        elif current_state == 'Unholding':
            addition = [254, 650, 254, 650, 254, 650, 254, 650, 254, 650]
        elif current_state == 'Held':
            addition = [254 * 2, 650, 254 * 2, 650, 254 * 2, 650, 254 * 2, 650, 254 * 2, 650]
        elif current_state == 'Holding':
            addition = [254 * 3, 650, 254 * 3, 650, 254 * 3, 650, 254 * 3, 650, 254 * 3, 650]

        self.line.points = [square_base[0] + addition[0], square_base[1] + addition[1], square_base[2] + addition[2],
                            square_base[3] + addition[3], square_base[4] + addition[4], square_base[5] + addition[5],
                            square_base[6] + addition[6], square_base[7] + addition[7], square_base[8] + addition[8],
                            square_base[9] + addition[9]]

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MesControl, self).__init__(**kwargs)

        self.state_machine = FSM.getInstance() #INIT STATEMACHINE

        ##Setup buttons
        # ON/OFF Bars
        self.btn_light1 = Button(text='', background_color=[1, 0, 0, 0.8], background_normal=' ')
        self.btn_light2 = Button(text='', background_color=[0, 1, 0, 0.8], background_normal=' ')
        self.btn_light3 = Button(text='', background_color=[1, 1, 0, 0.8], background_normal=' ')

        on_off_buttons = BoxLayout(orientation='horizontal', size_hint=(0.2, 0.2), pos_hint={'left': 1, 'top': 1},
                                   padding=[30, 30, 0, 30], spacing=10)
        on_off_buttons.add_widget(self.btn_light1)
        on_off_buttons.add_widget(self.btn_light2)
        on_off_buttons.add_widget(self.btn_light3)

        # Left collumn bars
        btn_start = Button(text='start')
        btn_reset = Button(text='reset')
        btn_stop = Button(text='stop')
        btn_clear = Button(text='clear')
        btn_abort = Button(text='unhold')

        btn_start.bind(on_press=self.change_state_execute_from_idle)
        btn_reset.bind(on_press=self.change_state_reset)
        btn_stop.bind(on_press=self.change_state_stopping)
        btn_clear.bind(on_press=self.change_state_clearing)
        btn_abort.bind(on_press=self.change_state_abort)
        # btn_reset.bind(on_press=callback)

        leftButtons = BoxLayout(orientation='vertical', size_hint=(0.2, 0.8), spacing=30,
                                pos_hint={'left': 1, 'bottom': 1}, padding=[30, 0, 0, 30])
        leftButtons.add_widget(btn_start)
        leftButtons.add_widget(btn_reset)
        leftButtons.add_widget(btn_stop)
        leftButtons.add_widget(btn_clear)
        leftButtons.add_widget(btn_abort)

        # Add widget layers
        self.add_widget(on_off_buttons)
        self.add_widget(leftButtons)

        # Add packml state image
        projectPath = rootpath.detect()
        img = Image(source=projectPath +'/scripts/GUI/images/packml.png', size_hint=(1, 1), pos_hint={'right': 1.1, 'center_y': 0.5}, opacity=0.8)
        self.add_widget(img)

        # Bind canvas to widget and set screen color
        self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        # Create box to highligh current state
        with self.canvas:
            Color(1, 0, 0, 0.8)
            self.line = Line()
            self.line.width = 6

        Clock.schedule_interval(self.on_timeout, 0.1)
        Clock.schedule_interval(self.light_tower, 0.5)

        # Start the main thread
        #self.start_main_thread("mainThread")


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
