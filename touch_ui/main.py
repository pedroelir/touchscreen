from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

# from kivy.clock import Clock
import subprocess
import logging
from typing import Any, Literal
from touch_ui.logger import logger
from touch_ui.commands import COMMANDS

logger.setLevel(logging.INFO)  # Set log level to DEBUG for detailed output

Window.size = (800, 480)  # Match Pi touchscreen

class CommandScreen(Screen):
    def __init__(self, title: str, command: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self.command = command
        self.title = title
        layout = BoxLayout()
        layout.add_widget(Label(text=title, font_size=48))
        self.add_widget(layout)

    def on_touch_down(self, touch: Any) -> None | Literal[True]:
        if self.collide_point(*touch.pos):
            logger.debug("Screen touched down")
            touch.ud["swiped"] = False  # reset gesture state
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch: Any) -> None | Literal[True]:
        if self.collide_point(*touch.pos):
            logger.debug("Screen touched up")
            if not touch.ud.get("swiped", False):
                try:
                    logger.info(f"Running command: {self.command}")
                    p = subprocess.run(self.command, shell=True, timeout=60, capture_output=True, text=True)
                    logger.debug(f"Command '{self.command}' executed with return code {p.returncode}")
                    logger.info(f"Command output: {p.stdout}")
                    logger.debug(f"Command error: {p.stderr}")
                except subprocess.TimeoutExpired:
                    logger.warning(f"Command '{self.command}' timed out")
                except Exception as e:
                    logger.error(f"Error running command '{self.command}': {e}")

                return True
        return super().on_touch_up(touch)


class SwipeManager(ScreenManager):
    SWIPE_THRESHOLD = 20  # pixels

    def on_touch_move(self, touch: Any) -> None | bool:
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
    def build(self) -> SwipeManager:
        sm = SwipeManager()
        for i, (title, cmd) in enumerate(COMMANDS):
            # sm.add_widget(CommandScreen(title, cmd, name=str(i)))
            sm.add_widget(CommandScreen(title, cmd, name=f"{i} - {title}"))
        return sm


if __name__ == "__main__":
    TouchUI().run()
