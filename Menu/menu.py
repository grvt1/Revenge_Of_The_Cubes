from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen


class ScreenMenu(Screen):
    class Menu(RelativeLayout):
        title_text = "Revenge of The Cubes"
        title_font_size = 30
        title = {title_text: Label()}

        buttons_width = 180
        buttons_height = 40
        buttons = {"Endless mode": 0,
                   "Survival mode": 0,
                   "Options": 0,
                   "Exit": 0,
                   "Layout": BoxLayout(orientation="vertical",
                                       size_hint=(None, None),
                                       pos_hint={"center_x": .5, "y": .2}
                                       )
                   }

        schedule_interval = 0

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.init_menu_title()
            self.init_menu_button()
            self.schedule_interval = Clock.schedule_interval(self.update, 1/60)

        def init_menu_title(self):
            self.title[self.title_text] = Label(text=self.title_text,
                                                size_hint=(1, .3),
                                                pos_hint={"center_x": .5, "center_y": .9},
                                                font_size=self.title_font_size
                                                )
            self.add_widget(self.title[self.title_text])

        def init_menu_button(self):
            x, y = self.buttons_width, self.buttons_height
            for i in self.buttons:
                if i != "Layout":
                    self.buttons[i] = Button(text=i,
                                             size_hint=(None, None),
                                             width=x,
                                             height=y,
                                             on_press=self.switch_screen_to
                                             )
                    self.buttons[i].id = i.split(" ")
                    self.buttons["Layout"].add_widget(self.buttons[i])
            self.add_widget(self.buttons["Layout"])

        def update_menu_buttons(self):
            x, y = self.buttons_width, self.buttons_height
            self.buttons["Layout"].width = x
            self.buttons["Layout"].height = y

        def switch_screen_to(self, instance):
            i = instance.id
            if i[0] == "Exit":
                App.get_running_app().stop()

            else:
                App.get_running_app().root.transition.direction = "left"
                App.get_running_app().root.current = i[0]

        def update(self, dt):
            self.update_menu_buttons()
