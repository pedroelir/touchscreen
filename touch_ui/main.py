from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
# from kivy.clock import Clock
import subprocess
from logger import logger

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
            logger.debug("Screen touched down")
            touch.ud["swiped"] = False  # reset gesture state
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            logger.debug("Screen touched up")
            if not touch.ud.get("swiped", False):
                subprocess.Popen(self.command, shell=True)
                return True
        return super().on_touch_up(touch)


class SwipeManager(ScreenManager):
    SWIPE_THRESHOLD = 20  # pixels

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_move(touch)

        # Already swiped → ignore further movement
        if touch.ud.get("swiped", False):
            return True

        if abs(touch.dx) > self.SWIPE_THRESHOLD:
            touch.ud["swiped"] = True  # lock swipe

            if touch.dx < 0:
                logger.info(f"Going to next screen {self.next()}")
                self.transition = SlideTransition(direction="left")
                self.current = self.next()
            else:
                logger.info(f"Going to next screen {self.previous()}")
                self.transition = SlideTransition(direction="right")
                self.current = self.previous()

            return True

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
