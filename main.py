from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.app import App

from Menu.menu import ScreenMenu
from Options.options import ScreenOptions
from Endless.Endless_main import ScreenEndlessGameSelection
from Survival.Survival import ScreenSurvivalGameSelection


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("main_kivy.kv")


class RevengeOfTheCubes(App):
    def build(self):
        return kv


RevengeOfTheCubes().run()
