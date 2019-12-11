import json

from kivy.clock import Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Label as CoreLabel
from kivy.lang.builder import Builder
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock

from scripts.OEE import OEE


class CircularProgressBar(ProgressBar):

    def __init__(self, prefix, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)

        # Set constant for the bar thickness
        self.thickness = 40

        #Label prefix
        self.label_prefix = prefix

        # Create a direct text representation
        self.label = CoreLabel(text=self.label_prefix + "0%", font_size=self.thickness, halign='center')

        # Initialise the texture_size variable
        self.texture_size = None

        # Refresh the text
        self.refresh_text()

        # Redraw on innit
        self.draw()

    def draw(self):

        with self.canvas:

            # Empty canvas instructions
            self.canvas.clear()

            # Draw no-progress circle
            Color(0.26, 0.26, 0.26)
            Ellipse(pos=self.pos, size=self.size)

            # Draw progress circle, small hack if there is no progress (angle_end = 0 results in full progress)
            Color(1, 0, 0)
            Ellipse(pos=self.pos, size=self.size,
                    angle_end=(0.001 if self.value_normalized == 0 else self.value_normalized*360))

            # Draw the inner circle (colour should be equal to the background)
            Color(0, 0, 0)
            Ellipse(pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                    size=(self.size[0] - self.thickness, self.size[1] - self.thickness))

            # Center and draw the progress text
            Color(1, 1, 1, 1)
            #added pos[0]and pos[1] for centralizing label text whenever pos_hint is set
            Rectangle(texture=self.label.texture, size=self.texture_size,
                  pos=(self.size[0] / 2 - self.texture_size[0] / 2 + self.pos[0], self.size[1] / 2 - self.texture_size[1] / 2 + self.pos[1]))


    def refresh_text(self):
        # Render the label
        self.label.refresh()

        # Set the texture size each refresh
        self.texture_size = list(self.label.texture.size)

    def set_value(self, value):
        # Update the progress bar value
        self.value = value

        # Update textual value and refresh the texture
        self.label.text = self.label_prefix + str(int(self.value_normalized*100)) + "%"
        self.refresh_text()

        # Draw all the elements
        self.draw()



class OEEScreen(Screen):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(OEEScreen, self).__init__(**kwargs)

        #Get oee instance
        self.oeeInstance = OEE.getInstance()

        self.availability = CircularProgressBar(prefix="Availability\n", size_hint=(None,None), height=400, width=400, max=100, pos=(50,50))
        self.performance = CircularProgressBar(prefix="Performance\n",size_hint=(None,None), height=400, width=400, max=100, pos=(500,50))
        self.quality = CircularProgressBar(prefix="Quality\n", size_hint=(None,None), height=400, width=400, max=100, pos=(50,475))
        self.oee = CircularProgressBar(prefix="OEE\n", size_hint=(None,None), height=400, width=400, max=100, pos=(500,475))
        self.add_widget(self.availability)
        self.add_widget(self.performance)
        self.add_widget(self.quality)
        self.add_widget(self.oee)

        font_size = 28
        btn_total = Button(text='Total Orders', font_size=font_size, halign='left')
        btn_good = Button(text='Good Orders', font_size=font_size, halign='left')
        btn_bad = Button(text='Bad Orders', font_size=font_size, halign='left')
        btn_uptime = Button(text='Uptime', font_size=font_size, halign='left')
        btn_downtime = Button(text='Downtime', font_size=font_size, halign='left')
        btn_totaltime = Button(text='Total Time', font_size=font_size, halign='left')
        oeeText = BoxLayout(orientation='vertical', size_hint=(0.3, 0.8), spacing=30, pos_hint={'right': 0.9, 'top': 0.9}, padding=[10, 10, 10, 10])
        oeeText.add_widget(btn_total)
        oeeText.add_widget(btn_good)
        oeeText.add_widget(btn_bad)
        oeeText.add_widget(btn_uptime)
        oeeText.add_widget(btn_downtime)
        oeeText.add_widget(btn_totaltime)
        self.add_widget(oeeText)

        #Bind canvas to widget and set screen color
        self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # colors range from 0-1 not 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        #Animate the progress bar
        Clock.schedule_interval(self.animate, 0.1)

    # Simple animation to show the circular progress bar in action
    def animate(self, dt):
        self.availability.set_value(self.oeeInstance.get_availability())
        self.performance.set_value(self.oeeInstance.get_performance())
        self.quality.set_value(self.oeeInstance.get_quality())
        self.oee.set_value(self.oeeInstance.get_oee())


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
