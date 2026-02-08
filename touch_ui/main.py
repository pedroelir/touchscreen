from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
# from kivy.clock import Clock
import subprocess

Window.size = (800, 480)  # Match Pi touchscreen

COMMANDS = [
    # ("Reboot", "sudo reboot"),
    # ("Shutdown", "sudo shutdown now"),
    ("Say Hello", "echo 'Hello, World!'"),
    ("Start Camera", "libcamera-hello"),
    ("List blocks", "lsblk"),
]

class CommandScreen(Screen):
    def __init__(self, title, command, **kwargs):
        super().__init__(**kwargs)
        self.command = command
        self.title = title
        layout = BoxLayout()
        layout.add_widget(Label(text=title, font_size=48))
        self.add_widget(layout)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print("Screen touched down")
            subprocess.Popen(self.command, shell=True)
            return True
        return super().on_touch_down(touch)

class SwipeManager(ScreenManager):
    def on_touch_move(self, touch):
        if abs(touch.dx) > 40:
            if touch.dx < 0:
                print("Swiped left")
                self.transition = SlideTransition(direction="left")
                print("Going to next screen:", self.next())
                self.current = self.next()

            else:
                print("Swiped right")
                self.transition = SlideTransition(direction="right")
                print("Going to previous screen:", self.previous())
                self.current = self.previous()
                
            return True
        else:
            print("Swipe too short, ignoring")
        return super().on_touch_move(touch)

class TouchUI(App):
    def build(self):
        sm = SwipeManager()
        for i, (title, cmd) in enumerate(COMMANDS):
            # sm.add_widget(CommandScreen(title, cmd, name=str(i)))
            sm.add_widget(CommandScreen(title, cmd, name=f"{i} - {title}"))
        return sm

if __name__ == "__main__":
    TouchUI().run()
