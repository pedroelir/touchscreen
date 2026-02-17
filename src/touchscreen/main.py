import logging
import subprocess
from typing import Any, Literal

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, Rectangle

# from kivy.clock import Clock
from touchscreen.logger import logger
from touchscreen.commands import COMMANDS

logger.setLevel(logging.INFO)  # Set log level to DEBUG for detailed output

Window.size = (800, 480)  # Match Pi touchscreen

class CommandScreen(Screen):
    def __init__(self, title: str, command: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self.command = command
        self.title = title
        layout = BoxLayout(orientation="vertical")
        self.title_label = Label(text=title, font_size=48)
        # Label to show first 15 chars of output
        self.output_label = Label(text="", font_size=28)
        # Label to show return code with colored background
        self.retcode_label = Label(text="", size_hint_y=None, height=48, font_size=24)

        # Add a colored background to the retcode_label using canvas
        with self.retcode_label.canvas.before:
            # default color: gray
            self._ret_color = Color(0.5, 0.5, 0.5, 1)
            self._ret_rect = Rectangle(pos=self.retcode_label.pos, size=self.retcode_label.size)

        # Keep rectangle size/pos in sync
        def _update_rect(instance, value):
            self._ret_rect.pos = instance.pos
            self._ret_rect.size = instance.size

        self.retcode_label.bind(pos=_update_rect, size=_update_rect)

        layout.add_widget(self.title_label)
        layout.add_widget(self.output_label)
        layout.add_widget(self.retcode_label)
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
                    # Update UI: show first 15 characters of stdout and return code with colored background
                    out = (p.stdout or "").replace("\n", " ")
                    snippet = out[:15]
                    self.output_label.text = snippet
                    self.retcode_label.text = str(p.returncode)
                    # Green background for success, red otherwise
                    if p.returncode == 0:
                        self._ret_color.rgba = (0, 1, 0, 1)
                    else:
                        self._ret_color.rgba = (1, 0, 0, 1)
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


def main() -> None:
    """Entry point for the touchscreen application."""
    TouchUI().run()


if __name__ == "__main__":
    main()
