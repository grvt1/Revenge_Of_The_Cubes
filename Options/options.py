from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from json import JSONDecodeError
import json
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider
from kivy.uix.gridlayout import GridLayout


class ScreenOptions(Screen):
    class Options(RelativeLayout):
        current_screen = "menu"

        selected_resolution = 0
        selected_width = 0
        selected_height = 0

        label_height = 30
        label_width = 100
        padding = 5

        resolution_options = {1: "7680x4320p",
                              2: "3840x2160p",
                              3: "2048x1080p",
                              4: "2560x1440p",
                              5: "1920x1080p",
                              6: "1280x720p",
                              7: "640x480p"
                              }

        options = {"Resolution": {"Selected": 6, "Value": resolution_options, "Kivy": {}, "Layout": GridLayout(cols=3, rows=1), "Type": "Button"},
                   "FullScreen": {"Active": False, "Kivy": {}, "Layout": GridLayout(cols=1, rows=1), "Type": "CheckBox"},
                   "Sound": {"Value": 50, "Kivy": {}, "Layout": GridLayout(cols=2, rows=1), "Type": "Slider"},
                   "Music": {"Value": 50, "Kivy": {}, "Layout": GridLayout(cols=2, rows=1), "Type": "Slider"}
                   }

        options_layout = {"Main": GridLayout(size_hint=(None, None),
                                             height=120,
                                             pos=(10, 500),
                                             cols=2
                                             ),
                          "Titles": GridLayout(size_hint=(None, None),
                                               row_force_default=True,
                                               row_default_height=30,
                                               width=100,
                                               cols=1,
                                               rows=4
                                               ),
                          "Selection": GridLayout(size_hint=(None, None),
                                                  row_force_default=True,
                                                  row_default_height=30,
                                                  width=150,
                                                  cols=1,
                                                  rows=4
                                                  )
                          }

        default_options = {"Resolution": {"Selected": 6, "Value": resolution_options, "Kivy": {}, "Type": "Button"},
                           "FullScreen": {"Active": False, "Kivy": {}, "Type": "CheckBox"},
                           "Sound": {"Value": 50, "Kivy": {}, "Type": "Slider"},
                           "Music": {"Value": 50, "Kivy": {}, "Type": "Slider"}
                           }

        options_what_changed = {}

        saved = True

        buttons = {}

        popup = {"Not_saved": {"Popup": Popup(), "Layout": GridLayout(), "Kivy": {}},
                 "You_sure": {"Popup": Popup(), "Layout": GridLayout(), "Kivy": {}}
                 }
        popup_button_font_size = 14

        last_screen_active = "menu"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.load_from_settings_file()
            self.init_window()
            self.init_options()
            self.popup_init_changes_not_saved()
            self.popup_init_are_you_sure()
            Clock.schedule_interval(self.update, 1/60)

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
            # print main options
            for i in self.options:
                # add text in first column
                self.options[i]["Kivy"]["Title"] = Label(text=str(i) + ":",
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
                    if y != "Title":
                        widget = self.options[i]["Kivy"][y]
                        self.options[i]["Layout"].add_widget(widget)

                self.options_layout["Titles"].add_widget(self.options[i]["Kivy"]["Title"])
                self.options_layout["Selection"].add_widget(self.options[i]["Layout"])

            # back button
            self.init_options_back_button()

            # create default button
            self.init_options_reset_button()

            # create save button
            self.init_options_save_button()

            for i in self.options_layout:
                if i != "Main":
                    widget = self.options_layout[i]
                    self.options_layout["Main"].add_widget(widget)

            self.add_widget(self.options_layout["Main"])

        def init_options_button_row(self, i):
            self.options[i]["Kivy"]["LeftButton"] = Button(text="<",
                                                           pos_hint={"x": 0},
                                                           background_normal="",
                                                           background_color=(.55, .55, .55, 0),
                                                           font_size=30,
                                                           size_hint_x=.2
                                                           )
            self.options[i]["Kivy"]["LeftButton"].bind(on_press=self.option_change_with_button)
            self.options[i]["Kivy"]["LeftButton"].id = i

            selected_number = self.options[i]["Selected"]
            selected_text = self.options[i]["Value"][selected_number]
            self.options[i]["Kivy"]["Option_value"] = Label(text=selected_text,
                                                            size_hint_x=.6,
                                                            pos_hint={"center_x": .5}
                                                            )

            self.options[i]["Kivy"]["RightButton"] = Button(text=">",
                                                            pos_hint={"right": 1},
                                                            background_normal="",
                                                            background_color=(.55, .55, .55, 0),
                                                            font_size=30,
                                                            size_hint_x=.2
                                                            )
            self.options[i]["Kivy"]["RightButton"].bind(on_press=self.option_change_with_button)
            self.options[i]["Kivy"]["RightButton"].id = i

            # disable resolution if fullscreen is true
            if i == "FullScreen" and self.options["FullScreen"]["Active"]:
                for y in self.options["Resolution"]["Kivy"]:
                    self.options["Resolution"]["Kivy"][y].disabled = True

        def init_options_slider_row(self, i):
            self.options[i]["Kivy"]["Slider"] = Slider(min=0,
                                                       max=100,
                                                       value=self.options[i]["Value"],
                                                       cursor_height=20,
                                                       cursor_width=20,
                                                       background_width=50,
                                                       size_hint_x=.8
                                                       )
            self.options[i]["Kivy"]["Slider"].bind(value=self.option_change_with_slider)
            self.options[i]["Kivy"]["Slider"].id = i

            self.options[i]["Kivy"]["Option_value"] = Label(text=str(self.options[i]["Value"]) + "%",
                                                            size_hint_x=.2
                                                            )

        def init_options_checkbox_row(self, i):
            self.options[i]["Kivy"]["CheckBox"] = CheckBox()

            self.options[i]["Kivy"]["CheckBox"].active = self.options[i]["Active"]
            self.options[i]["Kivy"]["CheckBox"].bind(active=self.option_change_with_checkbox)
            self.options[i]["Kivy"]["CheckBox"].id = i

        def init_options_back_button(self):
            self.buttons["Back"] = Button(text="Go back",
                                          size_hint_x=None,
                                          width=self.label_width,
                                          size_hint_y=None,
                                          height=self.label_height,
                                          pos=(self.padding, self.padding)
                                          )
            self.buttons["Back"].bind(on_press=self.back_to_menu)
            self.buttons["Back"].id = "go_to_menu"
            self.add_widget(self.buttons["Back"])

        def init_options_last_row_anchors(self):
            for i in range(0, 1):
                self.add_widget(Label(text="",
                                      size_hint_x=None,
                                      width=0,
                                      size_hint_y=None,
                                      height=0
                                      )
                                )

        def init_options_reset_button(self):
            self.buttons["Default"] = Button(text="Default",
                                             halign="right",
                                             size_hint_x=None,
                                             width=self.label_width,
                                             size_hint_y=None,
                                             height=self.label_height,
                                             pos=(self.label_width + self.padding, 5)
                                             )
            self.buttons["Default"].bind(on_press=self.popup_init_are_you_sure_open)
            self.buttons["Default"].id = "default"
            self.add_widget(self.buttons["Default"])

        def init_options_save_button(self):
            self.buttons["Save"] = Button(text="Save",
                                          halign="right",
                                          size_hint_x=None,
                                          width=self.label_width,
                                          size_hint_y=None,
                                          height=self.label_height,
                                          pos=(self.label_width*3 + self.padding, 5)
                                          )
            self.buttons["Save"].bind(on_press=self.save_options_button)
            self.buttons["Save"].id = "save options"
            self.add_widget(self.buttons["Save"])

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
            self.options[i]["Kivy"]["Option_value"].text = str(value) + "%"
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

        def popup_init_changes_not_saved(self):
            # set up the layout
            self.popup["Not_saved"]["Layout"].cols = 3
            self.popup["Not_saved"]["Layout"].padding = (0, 5, 0, 0)

            # set up buttons
            self.popup["Not_saved"]["Kivy"]["Discard"] = Button(text="Discard",
                                                                size_hint=(None, None),
                                                                size=(self.label_width, self.label_height),
                                                                font_size=self.popup_button_font_size,
                                                                background_normal="",
                                                                background_color=(.6, .2, .2, 1)
                                                                )

            self.popup["Not_saved"]["Kivy"]["Empty_anchor"] = Label(text="",
                                                                    size_hint=(None, None),
                                                                    size=(self.label_width - 25, self.label_height),
                                                                    )

            self.popup["Not_saved"]["Kivy"]["Save"] = Button(text="Save",
                                                             size_hint=(None, None),
                                                             size=(self.label_width, self.label_height),
                                                             font_size=self.popup_button_font_size,
                                                             background_normal="",
                                                             background_color=(.2, .6, .2, 1)
                                                             )

            # bind buttons
            self.popup["Not_saved"]["Kivy"]["Discard"].bind(on_press=self.discard_options_all)
            self.popup["Not_saved"]["Kivy"]["Save"].bind(on_press=self.save_options)

            # add widgets
            for i in self.popup["Not_saved"]["Kivy"]:
                value = self.popup["Not_saved"]["Kivy"][i]
                self.popup["Not_saved"]["Layout"].add_widget(value)

            self.popup["Not_saved"]["Popup"] = Popup(title="Settings are not saved.\nDo you want to discard changes?",
                                                     title_align="center",
                                                     size_hint=(None, None),
                                                     size=(300, 115),
                                                     content=self.popup["Not_saved"]["Layout"]
                                                     )

        def popup_init_are_you_sure(self):
            # set up the layout
            self.popup["You_sure"]["Layout"].cols = 3
            self.popup["You_sure"]["Layout"].padding = (0, 5, 0, 0)

            # set up the buttons
            self.popup["You_sure"]["Kivy"]["Dont_reset"] = Button(text="Don't reset",
                                                                  size_hint=(None, None),
                                                                  size=(self.label_width, self.label_height),
                                                                  font_size=self.popup_button_font_size,
                                                                  background_normal="",
                                                                  background_color=(.6, .2, .2, 1)
                                                                  )

            self.popup["You_sure"]["Kivy"]["Empty_anchor"] = Label(text="",
                                                                   size_hint=(None, None),
                                                                   size=(self.label_width - 25, self.label_height),
                                                                   )

            self.popup["You_sure"]["Kivy"]["Yes_reset"] = Button(text="Reset",
                                                                 size_hint=(None, None),
                                                                 size=(self.label_width, self.label_height),
                                                                 font_size=self.popup_button_font_size,
                                                                 background_normal="",
                                                                 background_color=(.2, .6, .2, 1)
                                                                 )

            # bind the buttons and add ID's
            self.popup["You_sure"]["Kivy"]["Dont_reset"].bind(on_press=self.reset_to_default)
            self.popup["You_sure"]["Kivy"]["Dont_reset"].id = False
            self.popup["You_sure"]["Kivy"]["Yes_reset"].bind(on_press=self.reset_to_default)
            self.popup["You_sure"]["Kivy"]["Yes_reset"].id = True

            # add widgets
            for i in self.popup["You_sure"]["Kivy"]:
                value = self.popup["You_sure"]["Kivy"][i]
                self.popup["You_sure"]["Layout"].add_widget(value)

            self.popup["You_sure"]["Popup"] = Popup(title="Do you really want to reset settings?",
                                                    title_align="center",
                                                    size_hint=(None, None),
                                                    size=(300, 100),
                                                    content=self.popup["You_sure"]["Layout"]
                                                    )

        def popup_init_are_you_sure_open(self, instance):
            self.popup["You_sure"]["Popup"].open()

        def back_to_menu(self, instance):
            if not self.saved:
                self.popup["Not_saved"]["Popup"].open()

            elif self.saved:
                if self.last_screen_active == "menu":
                    App.get_running_app().root.transition.direction = "right"
                    App.get_running_app().root.transition.duration = 0.5
                else:
                    App.get_running_app().root.transition.duration = 0

                App.get_running_app().root.current = self.last_screen_active

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
                text[i] = value

            json.dump(text, settings_file)
            settings_file.close()

        def load_from_settings_file(self):
            try:
                settings_file = open("Options/settings", "r")
                load_settings_file = json.load(settings_file)
            except JSONDecodeError:
                self.dump_to_settings_file()
                settings_file = open("Options/settings", "r")
                load_settings_file = json.load(settings_file)

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

        def update_values_in_kivy(self):
            for i in self.options:
                option_type = self.options[i]["Type"]

                if option_type == "Button":
                    selected = self.options[i]["Selected"]
                    value = self.options[i]["Value"][selected]

                    self.options[i]["Kivy"]["Option_value"].text = value

                elif option_type == "CheckBox":
                    value = self.options[i]["Active"]

                    self.options[i]["Kivy"]["CheckBox"].active = value

                elif option_type == "Slider":
                    value = self.options[i]["Value"]

                    self.options[i]["Kivy"]["Slider"].value = value
                    self.options[i]["Kivy"]["Option_value"].text = str(value)

        def reset_to_default(self, instance):
            value = instance.id
            if value:
                for i in self.options:
                    option_type = self.options[i]["Type"]

                    if option_type == "Button":
                        self.options[i]["Selected"] = self.default_options[i]["Selected"]

                    elif option_type == "CheckBox":
                        self.options[i]["Active"] = self.default_options[i]["Active"]

                    elif option_type == "Slider":
                        self.options[i]["Value"] = self.default_options[i]["Value"]

                self.update_values_in_kivy()
                self.save_options(instance)

            self.popup["You_sure"]["Popup"].dismiss()

        def save_options_button(self, instance):
            self.save_options(None)

        def discard_options_all(self, instance):
            self.load_from_settings_file()
            self.update_values_in_kivy()
            self.popup["Not_saved"]["Popup"].dismiss()

        def save_options_resolution(self):
            if self.saved:

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

            no_of_options = len(self.options)
            option_main_height = no_of_options * self.label_height
            x, y = self.padding, self.selected_height - option_main_height - self.padding
            self.options_layout["Main"].pos = (x, y)

        def save_options(self, instance):
            self.popup["Not_saved"]["Popup"].dismiss()
            self.save_options_resolution()
            self.dump_to_settings_file()

            self.saved = True
            self.options_what_changed = {}
        def update(self, dt):
            self.save_options_resolution()

            if App.get_running_app().root.current != "Options":
                self.last_screen_active = App.get_running_app().root.current

