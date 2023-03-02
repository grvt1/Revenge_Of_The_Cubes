from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class ScreenSurvivalGameSelection(Screen):
    class Survival(BoxLayout):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.add_widget(Label(text="Survival"))
