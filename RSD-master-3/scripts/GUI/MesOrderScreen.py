#!/usr/bin/env python3
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from scripts.GUI.table import Table
import logging
from scripts.MesOrder import MesOrder

import requests
import json




class MesOrderScreen(Screen):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MesOrderScreen, self).__init__(**kwargs)

        self.mesOrder = MesOrder()

        #Table setup#
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.my_table = Table()
        self.my_table.cols = 5

        decoded = self.get_orders()
        # look for an order with smallest ID which is not taken, so we can process it
        #Comment this for loop out if not on the RSD backbone server(or connect another flash server)
        if(decoded != None):
            for x in decoded['orders']:
                self.my_table.add_row(
                    [TextInput, {'text': str(x["id"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                    [TextInput, {'text': str(x["red"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                    [TextInput, {'text': str(x["blue"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                    [TextInput, {'text': str(x["yellow"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                    [TextInput, {'text': str(x["status"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}])


        self.my_table.label_panel.visible = True
        self.my_table.label_panel.labels[1].text = 'ID'
        self.my_table.label_panel.labels[2].text = 'Red'
        self.my_table.label_panel.labels[3].text = 'Blue'
        self.my_table.label_panel.labels[4].text = 'Yellow'
        self.my_table.label_panel.labels[5].text = 'status'
        self.my_table.label_panel.height_widget = 50
        self.my_table.number_panel.auto_width = True
        self.my_table.number_panel.visible = True
        self.my_table.scroll_view.bar_width = 10
        self.my_table.scroll_view.scroll_type = ['bars']
        self.my_table.scroll_view

        #Refresh button setup#
        btn_refresh = Button(text='REFRESH', background_color=[0, 0.8, 0, 1], background_normal=' ', font_size=8, on_press=self.refresh_callback)
        refresh_buttons = BoxLayout(orientation='horizontal', size_hint=(0.02, 0.055), pos_hint={'left': 1, 'top': 1})
        refresh_buttons.add_widget(btn_refresh)

        #Add the widgets
        self.add_widget(self.my_table)
        self.add_widget(refresh_buttons)

        ##Bind canvas to widget and set screen color
        self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def _keyboard_closed(self):
        pass

    def get_orders(self):
        # Get from database, needs MainDB to be running or on the backbone network
        # try:
        #     response = requests.get('http://127.0.0.1:5000/orders')
        #     decoded = json.loads(response.content)  # convert from JSON to dictionary
        # except requests.exceptions.ConnectionError:
        #     logging.error("[MesOrderScreen]Connection error")
        #
        # return decoded
        return self.mesOrder.get_order()



    def refresh_callback(self,instance):
        logging.info("[MesOrderScreen]" + 'The button <%s> is being pressed' % instance.text)
        #This wipes the table for data
        for i in range(0,len(self.my_table.grid.cells)):
            self.my_table.del_row(0)

        #add the updated table
        decoded = self.get_orders()
        for x in decoded['orders']:
            self.my_table.add_row(
                [TextInput, {'text': str(x["id"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                [TextInput, {'text': str(x["red"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                [TextInput, {'text': str(x["blue"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                [TextInput, {'text': str(x["yellow"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}],
                [TextInput, {'text': str(x["status"]), 'color_click': [1, 1, 1, 1], 'font_size': 18, 'halign':'center', 'disabled': True, 'background_disabled': ''}])

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """ Method of pressing keyboard  """
        if keycode[0] == 273:  # UP
            logging.info("[MesOrderScreen] Key pressed " + str(keycode))
        if keycode[0] == 274:  # DOWN
            logging.info("[MesOrderScreen] Key pressed " + str(keycode))
        if keycode[0] == 278:  # Home
            logging.info("[MesOrderScreen] Key pressed " + str(keycode))
        if keycode[0] == 279:  # End
            logging.info("[MesOrderScreen] Key pressed " +str(keycode))

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
