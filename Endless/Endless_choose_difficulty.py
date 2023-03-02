from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label


def init_choose_difficulty(self):
    for i in self.difficulties:
        # add buttons for choosing difficulty
        self.difficulties[i]["Kivy"]["Button"] = Button(text=i,
                                                        on_press=self.change_difficulty
                                                        )
        widget = self.difficulties[i]["Kivy"]["Button"]
        self.layout_choose_difficulty["Buttons"].add_widget(widget)

        # add text with high score
        self.difficulties[i]["Kivy"]["Label"] = Label(text="High score: \n" + str(self.difficulties[i]["High score"]),
                                                      valign="top",
                                                      halign="center",
                                                      padding_y=5
                                                      )
        widget = self.difficulties[i]["Kivy"]["Label"]
        self.layout_choose_difficulty["Labels"].add_widget(widget)

    self.layout_choose_difficulty["Back"].bind(on_press=self.back_to_menu)


def add_difficulty_layout_widget(self):
    for i in self.layout_choose_difficulty:
        self.choose_difficulty_layout.add_widget(self.layout_choose_difficulty[i])


def change_difficulty(self, instance):
    self.remove_choose_difficulty_layout()


def remove_choose_difficulty_layout(self):
    self.remove_widget(self.choose_difficulty_layout)
    self.update_tiles()
    self.generate_land()
    self.game_started = True

def back_to_menu(self, instance):
    App.get_running_app().root.transition.direction = "right"
    App.get_running_app().root.transition.duration = 0.5
    App.get_running_app().root.current = "menu"


def update_choose_difficulty_layout(self):
    x, y = 320, 72
    for i in self.difficulties:
        self.difficulties[i]["Kivy"]["Label"].text_size = (x, y)
