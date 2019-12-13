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

from scripts import finite_state_machine
from scripts.OEE import OEE
from scripts.RobotControl import RobotControl


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
        self.state_machine = finite_state_machine.FiniteStateMachine.getInstance()
        #Robot instance
        self.robot = RobotControl.getInstance()
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
        self.btn_total = Button(text='Total Orders:\n', font_size=font_size, halign='center')
        self.btn_good = Button(text='Good Orders:\n', font_size=font_size, halign='center')
        self.btn_bad = Button(text='Bad Orders:\n', font_size=font_size, halign='center')
        self.btn_uptime = Button(text='Uptime:\n', font_size=font_size, halign='center')
        self.btn_downtime = Button(text='Downtime:\n', font_size=font_size, halign='center')
        self.btn_totaltime = Button(text='Total Time:\n', font_size=font_size, halign='center')
        oeeTextRow1 = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=30, pos_hint={'right': 1, 'top': 1})
        oeeTextRow2 = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=30, pos_hint={'right': 1, 'top': 1})
        oeeTextRow3 = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=30, pos_hint={'right': 1, 'top': 1})
        oeeTextRow1.add_widget(self.btn_total)
        oeeTextRow1.add_widget(self.btn_good)
        oeeTextRow2.add_widget(self.btn_bad)
        oeeTextRow2.add_widget(self.btn_uptime)
        oeeTextRow3.add_widget(self.btn_downtime)
        oeeTextRow3.add_widget(self.btn_totaltime)
        oeeText = BoxLayout(orientation='vertical', size_hint=(0.3, 0.9), spacing=30, pos_hint={'right': 0.9, 'top': 0.95}, padding=[10, 10, 10, 10])
        oeeText.add_widget(oeeTextRow1)
        oeeText.add_widget(oeeTextRow2)
        oeeText.add_widget(oeeTextRow3)
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
        if self.state_machine.state == 'Execute' and not self.robot.getSafetyMode() == 5:
            self.oeeInstance.update(sys_up=True, task=self.state_machine.state)
        else:
            self.oeeInstance.update(sys_up=False, task=self.state_machine.state)

        self.availability.set_value(self.oeeInstance.get_availability()*100)
        self.performance.set_value(self.oeeInstance.get_performance()*100)
        self.quality.set_value(self.oeeInstance.get_quality()*100)
        self.oee.set_value(self.oeeInstance.get_oee()*100)

        #Update text:
        metrics = self.oeeInstance.get_metrics()
        self.btn_total.text ='Total Orders:\n' + str(metrics['Total Orders'])
        self.btn_good.text = 'Good Orders:\n' + str(metrics['Good Orders'])
        self.btn_bad.text ='Bad Orders:\n' + str(metrics['Bad Orders'])
        oeeTime = self.oeeInstance.get_time()
        self.btn_uptime.text ='Uptime [min]:\n' + str(round(oeeTime["Up-time"],3))
        self.btn_downtime.text ='Downtime [min]:\n' + str(round(oeeTime["Down-time"],3))
        self.btn_totaltime.text ='Total Time [min]:\n' + str(round(oeeTime["Total time"],3))


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
