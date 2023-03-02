from kivy.app import App
from kivy.config import Config
from kivy.uix.label import Label

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

import random
from kivy import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Line, Color, Quad
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen


class ScreenEndlessGameSelection(Screen):
    class Endless(RelativeLayout):
        from Endless.Endless_choose_difficulty import init_choose_difficulty, add_difficulty_layout_widget, change_difficulty, remove_choose_difficulty_layout, back_to_menu, update_choose_difficulty_layout

        difficulties = {"Easy": {"High score": 0, "Kivy": {}},
                        "Normal": {"High score": 0, "Kivy": {}},
                        "Hard": {"High score": 0, "Kivy": {}},
                        "Insane": {"High score": 0, "Kivy": {}},
                        }
        chosen_difficulty = None

        layout_choose_difficulty = {"Buttons": BoxLayout(orientation="horizontal",
                                                         size_hint=(1, .7),
                                                         pos_hint={"top": .9}
                                                         ),
                                    "Labels": BoxLayout(orientation="horizontal",
                                                        pos_hint={"top": .2},
                                                        size_hint=(1, .1)
                                                        ),
                                    "Back": Button(text="Back",
                                                   size_hint=(None, None),
                                                   width=100,
                                                   height=30,
                                                   pos_hint={"y": 0},
                                                   )
                                    }
        choose_difficulty_layout = RelativeLayout()

        V_NB_LINES = 30
        V_LINES_SPACING = (100/V_NB_LINES)/100
        v_lines = []

        H_NB_LINES = 15
        H_NB_LINES_real = int(H_NB_LINES + H_NB_LINES/2)
        H_LINES_SPACING = (100/(H_NB_LINES-1))/100
        h_lines = []

        NB_tiles = int((H_NB_LINES_real + 2)*V_NB_LINES)
        tiles = {}

        game_started = False

        move_speed_y = 20
        current_move_speed_y = 0
        current_offset_y = 0
        current_y_loops = 0
        inited = False

        max_mountains = .1
        prev_mount_left = 1
        prev_mount_right = 1

        ground_types = ["grass", "sand"]
        current_ground_type = "grass"

        pop_up_menu = {"Layout": BoxLayout(orientation="vertical",
                                           size_hint=(None, None),
                                           size=(150, 700),
                                           pos_hint={"center_x": .5, "y": .2}
                                           ),
                       "Buttons": {"Layout": BoxLayout(orientation="vertical",
                                                       size_hint=(None, None),
                                                       size=(150, 150),
                                                       pos_hint={"center_x": .5}
                                                       )
                                   }
                       }

        move_forward = ["w", "up"]
        move_back = ["s", "down"]
        menu = ["m", "escape"]

        keybinds = {"forward": {0: "w", 1: "up"},
                    "back": {0: "s", 1: "down"},
                    "menu": {0: "m", 1: "escape"}
                    }

        create_lake = {"left": {"Inited": False},
                       "right": {"Inited": False}
                       }
        lake_not_created = 0
        max_lake_width = .4

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.trigger_choose_difficulty_layout()
            self.add_widget(self.choose_difficulty_layout)
            Clock.schedule_interval(self.update, 1/60)

            if self.is_desktop:
                self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
                self._keyboard.bind(on_key_down=self.on_keyboard_down)
                self._keyboard.bind(on_key_up=self.on_keyboard_up)

        def is_desktop(self):
            if platform in ("linux", "win", "macosx"):
                return True
            else:
                return False

        def keyboard_closed(self):
            self._keyboard.unbind(on_key_down=self.on_keyboard_down)
            self._keyboard.unbind(on_key_up=self.on_keyboard_up)
            self._keyboard = None

        def on_keyboard_down(self, keyboard, keycode, text, modifiers):
            if keycode[1] == self.keybinds["forward"][0] or keycode[1] == self.keybinds["forward"][1]:
                self.current_move_speed_y = self.move_speed_y

            if keycode[1] == self.keybinds["back"][0] or keycode[1] == self.keybinds["back"][1]:
                spacing_y = self.height * self.H_LINES_SPACING * self.H_NB_LINES / 2
                if self.current_offset_y <= -spacing_y:
                    self.current_move_speed_y = 0
                else:
                    self.current_move_speed_y = -self.move_speed_y

        def on_keyboard_up(self, keyboard, keycode):
            for i in range(0, 1):
                if keycode[1] == self.keybinds["forward"][i] or keycode[1] == self.keybinds["back"][i]:
                    self.current_move_speed_y = 0
                    spacing_y = self.height * self.H_LINES_SPACING * self.H_NB_LINES / 2
                    if self.current_offset_y <= -spacing_y:
                        self.current_offset_y += 0.01

            if keycode[1] == "m":
                self.open_menu()

        def init_vertical_lines(self):
            with self.canvas:
                Color(1, 1, 1, 0)
                for i in range(0, self.V_NB_LINES):
                    self.v_lines.append(Line())

        def update_vertical_lines(self):
            # init lines if they are not inited yet
            if len(self.v_lines) == 0:
                self.init_vertical_lines()

            # then update the lines
            spacing_x = self.width*self.V_LINES_SPACING
            x1, y1 = 0, 0
            x2, y2 = 0, self.height
            for i in range(0, self.V_NB_LINES):
                x1 = x1 + spacing_x
                x2 = x1
                self.v_lines[i].points = (x1, y1, x2, y2)

        def init_horizontal_lines(self):
            with self.canvas:
                Color(1, 1, 1, 0)
                for i in range(len(self.h_lines), self.H_NB_LINES_real):
                    self.h_lines.append(Line(points=(0, 0, 0, 0)))

        def update_horizontal_lines(self):
            self.init_horizontal_lines()

            spacing_y = self.height*self.H_LINES_SPACING
            x1 = 0
            x2 = self.width
            for i in range(0, self.H_NB_LINES_real):
                y1 = (spacing_y*i) - self.current_offset_y
                self.h_lines[i].points = (x1, y1, x2, y1)

        def set_current_y_offset(self, dt):
            spacing_y = self.height*self.H_LINES_SPACING

            if self.current_offset_y >= spacing_y:
                # del and add new line
                del self.h_lines[0]

                # move tiles by one
                self.move_tiles_down()

                self.update_horizontal_lines()
                self.update_tiles()

                self.current_offset_y = self.current_move_speed_y*(dt*60)
                self.current_y_loops += 1

                self.change_ground_type()

            spacing_y = self.height * self.H_LINES_SPACING * self.H_NB_LINES/2
            if self.current_offset_y <= -spacing_y:
                self.current_move_speed_y = 0
                self.current_offset_y = -spacing_y

            else:
                self.current_offset_y += self.current_move_speed_y*(dt*60)

        def trigger_choose_difficulty_layout(self):
            self.init_choose_difficulty()
            self.add_difficulty_layout_widget()

        def init_tiles(self):
            count = len(self.tiles)
            with self.canvas.before:
                for i in range(count, self.NB_tiles):
                    self.tiles[i] = {}

                    self.tiles[i]["Quad"] = Quad(points=(0, 0, 0, 0, 0, 0, 0, 0))
                    self.tiles[i]["Type"] = ""

        def update_tiles(self):
            self.init_tiles()
            x = 0
            y = 0
            for i in self.tiles:
                self.tiles[i]["x"] = x
                self.tiles[i]["y"] = y

                spacing_x = self.V_LINES_SPACING*self.width
                spacing_y = self.H_LINES_SPACING*self.height
                off_screen = spacing_y*self.H_NB_LINES/2
                # off_screen = 0

                x1, y1 = spacing_x * x, spacing_y * y - self.current_offset_y - off_screen
                x2, y2 = spacing_x * x, spacing_y * (y+1) - self.current_offset_y - off_screen
                x3, y3 = spacing_x * (x+1), spacing_y * (y+1) - self.current_offset_y - off_screen
                x4, y4 = spacing_x * (x+1), spacing_y * y - self.current_offset_y - off_screen

                self.tiles[i]["Quad"].points = (x4, y4, x1, y1, x2, y2, x3, y3)

                end_of_line = (self.V_NB_LINES - 1) + self.V_NB_LINES * y

                if i == end_of_line:
                    y += 1
                    x = 0
                else:
                    x += 1

        def move_tiles_down(self):
            for i in self.tiles:
                if self.tiles[i]["y"] < self.H_NB_LINES_real:
                    tile_above = i + self.V_NB_LINES

                    self.tiles[i]["Quad"].points = self.tiles[tile_above]["Quad"].points

                    self.tiles[i]["Type"] = self.tiles[tile_above]["Type"]
                    self.tiles[i]["Quad"].source = self.tiles[tile_above]["Quad"].source

            self.put_texture()

            self.generate_land()

        def generate_land_mountains(self):
            random_max = int(self.V_NB_LINES * self.max_mountains)

            random_min_left = self.prev_mount_left - 1
            if random_min_left <= 0:
                random_min_left = 1

            random_max_left = self.prev_mount_left + 1
            if random_max_left > random_max:
                random_max_left = random_max

            random_min_right = self.prev_mount_right - 1
            if random_min_right <= 0:
                random_min_right = 1

            random_max_right = self.prev_mount_right + 1
            if random_max_right > random_max:
                random_max_right = random_max

            self.prev_mount_left = random.randint(random_min_left, random_max_left)
            self.prev_mount_right = random.randint(random_min_right, random_max_right)

        def generate_land_lake(self):
            self.generate_land_lake_where()

        def generate_land_lake_where(self):
            r = random.randint(self.lake_not_created, 100)
            if r == 100:
                lake_where = ""
                if self.create_lake["left"]["Inited"] and not self.create_lake["right"]["Inited"]:
                    lake_where = "right"

                elif self.create_lake["right"]["Inited"] and not self.create_lake["left"]["Inited"]:
                    lake_where = "left"

                elif not self.create_lake["right"]["Inited"] and not self.create_lake["left"]["Inited"]:
                    r = random.randint(0, 1)
                    if r == 0:
                        lake_where = "left"
                    elif r == 1:
                        lake_where = "right"

                if lake_where != "":
                    self.create_lake[lake_where]["Inited"] = True
                    self.lake_not_created = 0
                    self.generate_land_lake_dimensions(lake_where)
            else:
                self.lake_not_created += 1

        def generate_land_lake_dimensions(self, lake_where):
            if lake_where == "left":
                max_width = int(self.V_NB_LINES * self.max_lake_width)
                # where lake start on x
                start_x = random.randint(0, max_width - 1)
                self.create_lake[lake_where]["min_x"] = start_x
                self.create_lake[lake_where]["new_start_x"] = start_x

                # how wide
                end_x = random.randint(start_x + 1, max_width)
                self.create_lake[lake_where]["max_x"] = end_x
                self.create_lake[lake_where]["new_end_x"] = end_x

                # how tall
                end_y = random.randint(1, 100)
                self.create_lake[lake_where]["end_y"] = end_y

            if lake_where == "right":
                max_width = self.V_NB_LINES

                # where lake start on x
                start_x = random.randint(int(self.V_NB_LINES * (1 - self.max_lake_width)), max_width - 1)
                self.create_lake[lake_where]["min_x"] = start_x
                self.create_lake[lake_where]["new_start_x"] = start_x

                # how wide
                end_x = random.randint(start_x + 1, max_width)
                self.create_lake[lake_where]["max_x"] = end_x
                self.create_lake[lake_where]["new_end_x"] = end_x

                # how tall
                end_y = random.randint(1, 100)
                self.create_lake[lake_where]["end_y"] = end_y
            print("Lake")

        def generate_land(self):
            self.generate_land_mountains()
            self.generate_land_lake()

            self.generate_land_put_type()

            self.inited = True

        def generate_land_put_type(self):
            for i in self.tiles:
                named = False
                if self.tiles[i]["y"] == self.H_NB_LINES_real or self.tiles[i]["Type"] == "":
                    for y in self.create_lake:
                        if self.create_lake[y]["Inited"]:
                            start_x = self.create_lake[y]["new_start_x"]
                            end_x = self.create_lake[y]["new_end_x"]

                            left_tile = self.tiles[i - 1]["Type"]
                            bellow_left_tile = self.tiles[i - 1 - self.V_NB_LINES]["Type"]
                            bellow_tile = self.tiles[i - self.V_NB_LINES]["Type"]
                            if left_tile == "Lake" and bellow_left_tile != "Lake" and bellow_tile == "Lake":
                                end_x += 1

                            if start_x <= self.tiles[i]["x"] <= end_x:
                                if self.create_lake[y]["end_y"] >= 1:
                                    if self.tiles[i]["x"] == end_x:
                                        self.create_lake[y]["end_y"] -= 1

                                    min_x = self.create_lake[y]["min_x"]
                                    max_x = self.create_lake[y]["max_x"]

                                    new_start_x = start_x + random.randint(-1, 1)
                                    new_end_x = end_x + random.randint(-1, 1)

                                    # if start_x is to low then move 1 to the right
                                    if new_start_x < min_x or new_start_x < 0:
                                        new_start_x += 1
                                    # if start_x is higher or equal to the end_x move to the start_x to the left to avoid empty rows
                                    if new_start_x >= new_end_x:
                                        new_start_x -= 1

                                    # if end_x is to high then move 1 to the left
                                    if new_end_x > max_x or new_end_x > self.V_NB_LINES:
                                        new_end_x -= 1
                                    # if end_x is lower or equal to the start_x move the end_x to the right to avoid empty rows
                                    if new_end_x <= new_start_x:
                                        new_end_x += 1

                                    self.create_lake[y]["new_start_x"] = new_start_x
                                    self.create_lake[y]["new_end_x"] = new_end_x
                                    text = "Lake"
                                    named = True

                                if self.create_lake[y]["end_y"] == 0:
                                    self.create_lake[y]["Inited"] = False

                    if not named:
                        self.generate_land_mountains()
                        if self.prev_mount_left >= self.tiles[i]["x"] or self.tiles[i]["x"] >= (
                                self.V_NB_LINES - self.prev_mount_right):
                            text = "Mountain"
                        else:
                            text = "Ground"
                    self.tiles[i]["Type"] = text
            self.put_texture()

        def put_texture(self):
            for i in self.tiles:
                type_of_land = self.tiles[i]["Type"]
                if self.tiles[i]["y"] == self.H_NB_LINES_real or not self.inited:
                    if type_of_land == "Mountain":
                        self.tiles[i]["Quad"].source = f"C:\Python\Projects\Revenge of the Cubes\Texture\Mountain - {self.current_ground_type}.png"

                    elif type_of_land == "Ground":
                        r = random.randint(0, 25)
                        if r == 0:
                            self.tiles[i]["Quad"].source = f"C:\Python\Projects\Revenge of the Cubes\Texture\Ground - {self.current_ground_type}.png"
                        elif r == 1:
                            self.tiles[i]["Quad"].source = f"C:\Python\Projects\Revenge of the Cubes\Texture\Ground - {self.current_ground_type} 2.png"
                        else:
                            self.tiles[i]["Quad"].source = f"C:\Python\Projects\Revenge of the Cubes\Texture\Ground - {self.current_ground_type} 3.png"

                    elif type_of_land == "Lake":
                        left = self.tiles[i - 1]["Type"]
                        right = self.tiles[i + 1]["Type"]
                        above = self.tiles[i + self.V_NB_LINES]["Type"]
                        bellow = self.tiles[i - self.V_NB_LINES]["Type"]

                        self.tiles[i]["Quad"].source = "C:\Python\Projects\Revenge of the Cubes\Texture\lake.png"

        def change_ground_type(self):
            r = random.randint(self.current_y_loops, 1000)
            if r == 1000:
                current_type_index = self.ground_types.index(self.current_ground_type)
                if len(self.ground_types) - 1 == current_type_index:
                    next_type_index = 0
                else:
                    next_type_index = current_type_index + 1
                self.current_ground_type = self.ground_types[next_type_index]
                self.current_y_loops = 0

        def pop_up_menu_switch_screen(self, instance):
            App.get_running_app().root.transition.direction = "up"
            App.get_running_app().root.transition.duration = 0.5
            App.get_running_app().root.current = instance.id

            self.game_started = False
            self.remove_widget(self.pop_up_menu["Layout"])

        def back_to_game(self, instance):
            self.remove_widget(self.pop_up_menu["Layout"])
            self.game_started = True

        def init_open_menu(self):
            if len(self.pop_up_menu) == 2:
                self.pop_up_menu["Paused"] = Label(text="Paused",
                                                   font_size=50,
                                                   text_size=self.size,
                                                   valign="top",
                                                   halign="center"
                                                   )
                self.pop_up_menu["Buttons"]["Layout"].add_widget(self.pop_up_menu["Paused"])

                self.pop_up_menu["Buttons"]["Options"] = Button(text="Options",
                                                                on_press=self.pop_up_menu_switch_screen
                                                                )
                self.pop_up_menu["Buttons"]["Options"].id = "Options"

                self.pop_up_menu["Buttons"]["Back to game"] = Button(text="Back to game",
                                                                     on_press=self.back_to_game
                                                                     )

                self.pop_up_menu["Buttons"]["Empty"] = Label()

                self.pop_up_menu["Buttons"]["Exit"] = Button(text="Exit",
                                                             on_press=self.pop_up_menu_switch_screen
                                                             )

                self.pop_up_menu["Buttons"]["Exit"].id = "menu"

                for i in self.pop_up_menu["Buttons"]:
                    if i != "Layout":
                        self.pop_up_menu["Buttons"]["Layout"].add_widget(self.pop_up_menu["Buttons"][i])

                self.pop_up_menu["Layout"].add_widget(self.pop_up_menu["Buttons"]["Layout"])

        def open_menu(self):
            self.game_started = False
            self.init_open_menu()
            self.add_widget(self.pop_up_menu["Layout"])

        def update(self, dt):
            if self.game_started:
                # init and update lines
                self.update_vertical_lines()
                self.update_horizontal_lines()
                self.set_current_y_offset(dt)
                self.update_tiles()

            elif not self.game_started:
                self.update_choose_difficulty_layout()
