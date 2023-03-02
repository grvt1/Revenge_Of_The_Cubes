import time

from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
import json

Config.set('graphics', 'width', '1080')
Config.set('graphics', 'height', '780')

from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.button import Button


# define our different screen
class ScreenMenu(Screen):
    pass


class ScreenOptions(Screen):
    class Options(GridLayout):
        current_screen = "menu"
        resolution_options = {1: "7680x4320p",
                              2: "3840x2160p",
                              3: "2048x1080p",
                              4: "2560x1440p",
                              5: "1920x1080p",
                              6: "1280x720p",
                              7: "640x480p"
                              }
        options = {"Resolution": {"Selected": 6, "Value": resolution_options, "Kivy": {}, "Type": "Button"},
                   "FullScreen": {"Active": True, "Kivy": {}, "Type": "CheckBox"},
                   "Sound": {"Value": 50, "Kivy": {}, "Type": "Slider"},
                   "Music": {"Value": 50, "Kivy": {}, "Type": "Slider"}
                   }

        options_what_changed = {}

        saved = True

        go_to_menu = []
        save = []
        empty_y_cells = []

        popup_insides = GridLayout()
        popup = Popup()

        selected_resolution = 0
        selected_width = 0
        selected_height = 0

        label_height = 30
        label_width = 100

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.load_from_settings_file()
            self.init_window()
            self.init_options()
            self.back_to_menu_not_saved_popup()
            Clock.schedule_interval(self.save_options_resolution, 1 / 60)

        def init_window(self):
            if not self.options["FullScreen"]["Active"]:
                self.selected_resolution = self.options["Resolution"]["Value"][
                    self.options["Resolution"]["Selected"]].split("x")
                self.selected_width = int(self.selected_resolution[0])
                self.selected_height = int(self.selected_resolution[1].removesuffix("p"))

                Window.size = (self.selected_width, self.selected_height)
            else:
                Window.fullscreen = True
                self.selected_width = Window.width
                self.selected_height = Window.height

        def init_options(self):
            self.cols = 5
            self.padding = 10
            self.spacing = (10, 0)

            # print main options
            for i in self.options:
                # add text in first column
                self.options[i]["Kivy"]["Option_left_text"] = Label(text=str(i),
                                                                    size_hint_x=None,
                                                                    width=self.label_width,
                                                                    size_hint_y=None,
                                                                    height=self.label_height
                                                                    )
                # if button add 1down button, current value, 1up button
                if self.options[i]["Type"] == "Button":
                    self.init_options_button_row(i)

                # if check add 1 empty, 1 check, 1 empty cells
                if self.options[i]["Type"] == "CheckBox":
                    self.init_options_checkbox_row(i)

                # if slider add empty cell, slider, current value
                elif self.options[i]["Type"] == "Slider":
                    self.init_options_slider_row(i)

                # add widgets
                for y in self.options[i]["Kivy"]:
                    self.add_widget(self.options[i]["Kivy"][y])

            # create empty cells so that last 2 buttons are on bottom
            self.init_options_y_anchor()

            # create last row
            # back button
            self.init_options_back_button()

            # create empty cells on the bottom to move "save" button to the right
            self.init_options_last_row_anchors()

            # create save button
            self.init_options_save_button()

            print(self.options)

        def init_options_button_row(self, i):
            self.options[i]["Kivy"]["LeftButton"] = Button(text="<",
                                                           size_hint_x=None,
                                                           width=self.label_width / 4,
                                                           size_hint_y=None,
                                                           height=self.label_height / 4
                                                           )
            self.options[i]["Kivy"]["LeftButton"].bind(on_press=self.option_change_with_button)
            self.options[i]["Kivy"]["LeftButton"].id = i

            selected_number = self.options[i]["Selected"]
            selected_text = self.options[i]["Value"][selected_number]
            self.options[i]["Kivy"]["Option_value"] = Label(text=selected_text,
                                                            size=self.size,
                                                            halign="center",
                                                            size_hint_x=None,
                                                            width=self.label_width * 2,
                                                            size_hint_y=None,
                                                            height=self.label_height
                                                            )

            self.options[i]["Kivy"]["RightButton"] = Button(text=">",
                                                            size_hint_x=None,
                                                            width=self.label_width / 4,
                                                            size_hint_y=None,
                                                            height=self.label_height / 4
                                                            )
            self.options[i]["Kivy"]["RightButton"].bind(on_press=self.option_change_with_button)
            self.options[i]["Kivy"]["RightButton"].id = i

            # disable resolution if fullscreen is true
            if i == "FullScreen" and self.options["FullScreen"]["Active"]:
                for y in self.options["Resolution"]["Kivy"]:
                    self.options["Resolution"]["Kivy"][y].disabled = True

        def init_options_slider_row(self, i):
            self.options[i]["Kivy"]["Empty_cell_left"] = Label(text="",
                                                               size_hint_x=None,
                                                               width=self.label_width / 4,
                                                               size_hint_y=None,
                                                               height=self.label_height / 4
                                                               )

            self.options[i]["Kivy"]["Slider"] = Slider(min=0,
                                                       max=100,
                                                       value=self.options[i]["Value"],
                                                       cursor_height=20,
                                                       cursor_width=20,
                                                       background_width=50,
                                                       padding=10,
                                                       height=self.label_height
                                                       )
            self.options[i]["Kivy"]["Slider"].bind(value=self.option_change_with_slider)
            self.options[i]["Kivy"]["Slider"].id = i

            self.options[i]["Kivy"]["Option_value"] = Label(text=str(self.options[i]["Value"]),
                                                            valign="bottom",
                                                            size_hint_x=None,
                                                            width=self.label_width / 4,
                                                            size_hint_y=None,
                                                            height=self.label_height / 4
                                                            )

            # add right anchor so everything stays in its place

            self.options[i]["Kivy"]["Anchor_right"] = Label(text="",
                                                            size_hint_x=None,
                                                            width=self.selected_width,
                                                            size_hint_y=None,
                                                            height=self.label_height
                                                            )

        def init_options_checkbox_row(self, i):
            self.options[i]["Kivy"]["Empty_cell_left"] = Label(text="",
                                                               size_hint_x=None,
                                                               width=self.label_width / 4,
                                                               size_hint_y=None,
                                                               height=self.label_height / 4
                                                               )

            self.options[i]["Kivy"]["CheckBox"] = CheckBox()
            self.options[i]["Kivy"]["CheckBox"].active = self.options[i]["Active"]
            self.options[i]["Kivy"]["CheckBox"].bind(active=self.option_change_with_checkbox)
            self.options[i]["Kivy"]["CheckBox"].id = i

            self.options[i]["Kivy"]["Empty_cell_right"] = Label(text="",
                                                                size_hint_x=None,
                                                                width=self.label_width / 4,
                                                                size_hint_y=None,
                                                                height=self.label_height / 4
                                                                )

        def init_options_y_anchor(self):
            widget_count = len(self.options) + 2
            empty_space_height = self.selected_height - (widget_count * self.label_height) - self.spacing[0]
            for i in range(0, self.cols):
                self.empty_y_cells.append(Label(text="",
                                                size_hint_x=None,
                                                width=self.label_width / 4,
                                                size_hint_y=None,
                                                height=empty_space_height
                                                )
                                          )
                self.add_widget(self.empty_y_cells[i])

        def init_options_back_button(self):
            self.go_to_menu = Button(text="Go back",
                                     size_hint_x=None,
                                     width=self.label_width,
                                     size_hint_y=None,
                                     height=self.label_height
                                     )
            self.go_to_menu.bind(on_press=self.back_to_menu)
            self.go_to_menu.id = "go_to_menu"
            self.add_widget(self.go_to_menu)

        def init_options_last_row_anchors(self):
            for i in range(0, self.cols - 2):
                self.add_widget(Label(text="",
                                      size_hint_x=None,
                                      width=0,
                                      size_hint_y=None,
                                      height=0
                                      )
                                )

        def init_options_save_button(self):
            self.save = Button(text="Save",
                               halign="right",
                               size_hint_x=None,
                               width=self.label_width,
                               size_hint_y=None,
                               height=self.label_height
                               )
            self.save.bind(on_press=self.save_options)
            self.save.id = "save options"
            self.add_widget(self.save)

        def option_change_with_button(self, instance):
            i = instance.id
            i_text = instance.text

            if i not in self.options_what_changed:
                # save old values before saving
                self.options_what_changed[i] = {}
                self.options_what_changed[i]["Old Value"] = self.options[i]["Selected"]

            # change selected number
            change_by = 0
            if i_text == "<":
                change_by = -1
            elif i_text == ">":
                change_by = 1
            self.options[i]["Selected"] += change_by

            # check if selected number is higher than number of values or equal to 0
            max_value = len(self.options[i]["Value"])
            if self.options[i]["Selected"] <= 0:
                self.options[i]["Selected"] = max_value
            elif self.options[i]["Selected"] > max_value:
                self.options[i]["Selected"] = 1

            # change text
            selected_number = self.options[i]["Selected"]
            new_text = self.options[i]["Value"][selected_number]
            self.options[i]["Kivy"]["Option_value"].text = new_text

            # save new value and compare with old value
            self.options_what_changed[i]["New Value"] = selected_number
            if self.options_what_changed[i]["Old Value"] == self.options_what_changed[i]["New Value"]:
                del self.options_what_changed[i]

            # if there are no changes in settings
            if self.options_what_changed == {}:
                self.saved = True
            else:
                self.saved = False

        def option_change_with_slider(self, *args):
            i = args[0].id

            # save old values before saving
            if i not in self.options_what_changed:
                self.options_what_changed[i] = {}
                self.options_what_changed[i]["Old Value"] = self.options[i]["Value"]

            value = int(args[1])
            self.options[i]["Kivy"]["Option_value"].text = str(value)
            self.options[i]["Value"] = value

            # save new value and compare with old value
            self.options_what_changed[i]["New Value"] = value
            if self.options_what_changed[i]["Old Value"] == self.options_what_changed[i]["New Value"]:
                del self.options_what_changed[i]

            # if there are no changes in settings
            if self.options_what_changed == {}:
                self.saved = True
            else:
                self.saved = False

        def option_change_with_checkbox(self, *args):
            i = args[0].id

            # save old values before saving
            if i not in self.options_what_changed:
                # save old values before saving
                self.options_what_changed[i] = {}
                self.options_what_changed[i]["Old Value"] = self.options[i]["Active"]

            self.options[i]["Active"] = args[1]
            if i == "FullScreen":
                for y in self.options["Resolution"]["Kivy"]:
                    self.options["Resolution"]["Kivy"][y].disabled = args[1]

            # save new value and compare with old value
            self.options_what_changed[i]["New Value"] = self.options[i]["Active"]
            if self.options_what_changed[i]["Old Value"] == self.options_what_changed[i]["New Value"]:
                del self.options_what_changed[i]

            # if there are no changes in settings
            if self.options_what_changed == {}:
                self.saved = True
            else:
                self.saved = False

        def back_to_menu_not_saved_popup(self):
            self.popup_insides.cols = 3
            self.popup_insides.padding = (0, 5, 0, 0)
            popup_insides_buttons = [Button(text="Discard",
                                            size_hint=(None, None),
                                            size=(self.label_width, self.label_height),
                                            background_normal="",
                                            background_color=(1, .2, .2, .4)
                                            ),
                                     Label(text="",
                                           size_hint=(None, None),
                                           size=(self.label_width - 25, self.label_height),
                                           ),
                                     Button(text="Save",
                                            size_hint=(None, None),
                                            size=(self.label_width, self.label_height),
                                            background_normal="",
                                            background_color=(.2, 1, .2, .4)
                                            )
                                     ]
            popup_insides_buttons[0].bind(on_press=self.discard_options_all,
                                          on_release=self.back_to_menu
                                          )
            popup_insides_buttons[2].bind(on_press=self.save_options,
                                          on_release=self.back_to_menu
                                          )
            for i in popup_insides_buttons:
                self.popup_insides.add_widget(i)

            self.popup = Popup(title="Settings are not saved.\nDo you want to discard changes?",
                               title_align="center",
                               size_hint=(None, None),
                               size=(300, 115),
                               content=self.popup_insides
                               )

        def back_to_menu(self, instance):
            if not self.saved:
                self.popup.open()

            elif self.saved:
                App.get_running_app().root.transition.direction = "right"
                App.get_running_app().root.transition.duration = 0.5
                App.get_running_app().root.current = "menu"

        def save_options_resolution(self, dt):
            if self.saved and (
                    App.get_running_app().root.current == "options" or App.get_running_app().root.current == "menu"):
                if not self.options["FullScreen"]["Active"]:
                    # change selected width/height
                    self.selected_resolution = self.options["Resolution"]["Value"][
                        self.options["Resolution"]["Selected"]].split("x")
                    self.selected_width = int(self.selected_resolution[0])
                    self.selected_height = int(self.selected_resolution[1].removesuffix("p"))

                    Window.fullscreen = False
                    Window.size = (self.selected_width, self.selected_height)
                elif self.options["FullScreen"]["Active"]:
                    Window.fullscreen = "auto"
                    self.selected_width = Window.width
                    self.selected_height = Window.height

                # change empty cells width
                for y in self.options:
                    self.options[y]["Kivy"]["Anchor_right"].width = self.selected_width

                # change empty cells height
                widget_count = len(self.options) + 2
                empty_space_height = self.selected_height - (widget_count * self.label_height) - self.spacing[0]
                for i in range(0, len(self.empty_y_cells)):
                    self.empty_y_cells[i].height = empty_space_height

        def discard_options_all(self, instance):
            pass

        def dump_to_settings_file(self):
            settings_file = open("settings", "w+")
            text = {}
            for i in self.options:
                option_type = self.options[i]["Type"]
                value = ""
                if option_type == "Button":
                    selected_number = self.options[i]["Selected"]
                    value = self.options[i]["Value"][selected_number]
                elif option_type == "CheckBox":
                    value = self.options[i]["Active"]
                elif option_type == "Slider":
                    value = self.options[i]["Value"]
                    print(value)
                text[i] = value

            json.dump(text, settings_file)
            settings_file.close()

        def load_from_settings_file(self):
            try:
                settings_file = open("settings", "r")
                load_settings_file = json.load(settings_file)
            except:
                self.dump_to_settings_file()
                settings_file = open("settings", "r")
                load_settings_file = json.load(settings_file)

            change_to_value = ""
            for i in load_settings_file:
                option_type = self.options[i]["Type"]
                value_in_file = load_settings_file[i]

                if option_type == "Button":
                    for y in self.options[i]["Value"]:
                        if self.options[i]["Value"][y] == value_in_file:
                            self.options[i]["Selected"] = y

                elif option_type == "CheckBox":
                    self.options[i]["Active"] = value_in_file

                elif option_type == "Slider":
                    self.options[i]["Value"] = load_settings_file[i]

                settings_file.close()

        def save_options(self, instance):
            self.popup.dismiss()
            self.save_options_resolution(1)
            self.dump_to_settings_file()

            self.saved = True


class ScreenGame(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("main_kivy.kv")


class RevengeOfTheCubes(App):
    def build(self):
        return kv


RevengeOfTheCubes().run()
