# from kivy._event import partial
# from kivy.app import App
# from kivy.graphics import Color, Rectangle
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.button import Button
# from kivy.uix.label import Label
# from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition, NoTransition
# from kivy.uix.widget import Widget
# from kivy.base import runTouchApp
# from kivy.factory import Factory
#
# def callback(instance):
#     print('The button <%s> is being pressed' % instance.text)
#
# #Root widget for button layout
# class mesControlScreen(Screen):
#
#     def __init__(self, **kwargs):
#         # make sure we aren't overriding any important functionality
#         super(mesControlScreen, self).__init__(**kwargs)
#
#         #Setup Actionbar
#         actionbar = Factory.ActionBar(pos_hint={'top': 1})
#         av = Factory.ActionView()
#         av.add_widget(Factory.ActionPrevious(title='MES System', with_previous=False))
#         av.add_widget(Factory.ActionOverflow())
#
#         av.add_widget(Factory.ActionButton(text='EM Stop',background_color=[1,0,0,0.8], background_normal=' '))
#
#         ag = Factory.ActionGroup(text='Menu')
#         btn_mes_control = Factory.ActionButton(text='MES Control')
#         btn_order_view = Factory.ActionButton(text='Order view')
#
#         btn_mes_control.bind(on_press=callback)
#         btn_mes_control.bind(on_press=callback)
#
#
#         ag.add_widget(btn_mes_control)
#         ag.add_widget(btn_order_view)
#
#         av.add_widget(ag)
#         actionbar.add_widget(av)
#
#         #ON/OFF Bars
#         btn_on = Button(text='ON', background_color=[0,1,0,0.8], background_normal=' ')
#         btn_off = Button(text='OFF', background_color=[1,0,0,0.8], background_normal=' ')
#         on_off_buttons = BoxLayout(orientation='horizontal', size_hint=(0.2,0.4), pos_hint={'left':1,'top':1}, padding=[30,120,6,70], spacing=10)
#         on_off_buttons.add_widget(btn_on)
#         on_off_buttons.add_widget(btn_off)
#
#         #Left collumn bars
#         btn_reset = Button(text='reset')
#         btn_start = Button(text='start')
#         btn_stop = Button(text='stop')
#         btn_hold = Button(text='hold')
#         btn_clear = Button(text='clear')
#
#         btn_reset.bind(on_press=callback)
#
#         leftButtons = BoxLayout(orientation='vertical', size_hint=(0.2, 0.6), spacing=30, pos_hint={'left': 1, 'bottom': 1}, padding=[30,5,5,10])
#         leftButtons.add_widget(btn_reset)
#         leftButtons.add_widget(btn_start)
#         leftButtons.add_widget(btn_stop)
#         leftButtons.add_widget(btn_hold)
#         leftButtons.add_widget(btn_clear)
#
#         #Add widget layers
#         self.add_widget(actionbar)
#         self.add_widget(on_off_buttons)
#         self.add_widget(leftButtons)
#
#         ##Bind canvas to widget and set screen color
#         self.bind(size=self._update_rect, pos=self._update_rect)
#         with self.canvas.before:
#             Color(0.75, 0.75, 0.75, 1)  # colors range from 0-1 not 0-255
#             self.rect = Rectangle(size=self.size, pos=self.pos)
#
#
#     def _update_rect(self, instance, value):
#         self.rect.pos = instance.pos
#         self.rect.size = instance.size
#
# class mesOrderScreen(Screen):
#
#     def __init__(self, **kwargs):
#         # make sure we aren't overriding any important functionality
#         super(mesOrderScreen, self).__init__(**kwargs)
#
#         #Setup Actionbar
#         actionbar = Factory.ActionBar(pos_hint={'top': 1})
#         av = Factory.ActionView()
#         av.add_widget(Factory.ActionPrevious(title='MES System', with_previous=False))
#         av.add_widget(Factory.ActionOverflow())
#
#         av.add_widget(Factory.ActionButton(text='EM Stop',background_color=[1,0,0,0.8], background_normal=' '))
#
#         ag = Factory.ActionGroup(text='Menu')
#         ag.add_widget(Factory.ActionButton(text='MES Control'))
#         ag.add_widget(Factory.ActionButton(text='Order view'))
#
#         av.add_widget(ag)
#         actionbar.add_widget(av)
#
#         #addwidget to root
#         self.add_widget(actionbar)
#
#
#         ##Bind canvas to widget and set screen color
#         self.bind(size=self._update_rect, pos=self._update_rect)
#         with self.canvas.before:
#             Color(0.75, 0.75, 0.75, 1)  # colors range from 0-1 not 0-255
#             self.rect = Rectangle(size=self.size, pos=self.pos)
#
#
#     def _update_rect(self, instance, value):
#         self.rect.pos = instance.pos
#         self.rect.size = instance.size
#
#
#
# class MainApp(App):
#
#     def build(self):
#         #Create screenmanager and add screens
#         sm = ScreenManager(transition=NoTransition())
#         sm.add_widget(mesControlScreen(name='control'))
#         sm.add_widget(mesOrderScreen(name='order'))
#         return sm
#
#
#
# if __name__ == '__main__':
#     MainApp().run()
#
#

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

Window.clearcolor = (1,1,1,1)

Builder.load_file("mesGUI.kv")


class Menu(BoxLayout):
    manager = ObjectProperty(None)

def callback(instance):
    print('The button <%s> is being pressed' % instance.text)


class MesControl(Screen):

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
        btn_reset = Button(text='reset')
        btn_start = Button(text='start')
        btn_stop = Button(text='stop')
        btn_hold = Button(text='hold')
        btn_clear = Button(text='clear')

        #btn_reset.bind(on_press=callback)

        leftButtons = BoxLayout(orientation='vertical', size_hint=(0.2, 0.8), spacing=30, pos_hint={'left': 1, 'bottom': 1}, padding=[30,0,0,30])
        leftButtons.add_widget(btn_reset)
        leftButtons.add_widget(btn_start)
        leftButtons.add_widget(btn_stop)
        leftButtons.add_widget(btn_hold)
        leftButtons.add_widget(btn_clear)

        #Add widget layers
        self.add_widget(on_off_buttons)
        self.add_widget(leftButtons)

        ##Bind canvas to widget and set screen color
        self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            Color(0.75, 0.75, 0.75, 1)  # colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)


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

    def build(self):
        return Menu()


if __name__ == '__main__':
    MainApp().run()