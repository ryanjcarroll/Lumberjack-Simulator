import pygame as pg
from settings import *
import threading
import random

class SpriteAssetManager:
    def __init__(self):
        self.images = {}
        self.lock = threading.Lock()

    def load(self, path):
        with self.lock:
            if path not in self.images:
                # add new entries to the saved images
                image = pg.image.load(path)
                self.images[path] = image

            # hand out copies to avoid race conditions
            # TODO there's probably a better way but not sure what it is right now
            return self.images[path].copy()

    def load_from_tilesheet(self, path, row_index, col_index, tile_size):
        with self.lock:
            if path not in self.images:
                sheet = pg.image.load(path)
                self.images[path] = sheet

            tile_path = f"{path}?{row_index},{col_index},{tile_size}"
            if tile_path not in self.images:
                # Extract a single image from spritesheet
                x = col_index * tile_size
                y = row_index * tile_size

                tile_rect = pg.Rect(x, y, tile_size, tile_size)
                self.images[tile_path] = self.images[path].subsurface(tile_rect)

            return self.images[tile_path]
        
    def load_from_spritesheet(self, path, topleft:tuple, width:int, height:int):
        with self.lock:
            if path not in self.images:
                sheet = pg.image.load(path)
                self.images[path] = sheet
            
            tile_path = f"{path}?{topleft},width,height"
            if tile_path not in self.images:
                # Extract a single image from spritesheet by pixel coordinates
                tile_rect = pg.Rect(topleft[0], topleft[1], width, height)
                self.images[tile_path] = self.images[path].subsurface(tile_rect)

            return self.images[tile_path]
        
class SoundAssetManager:
    def __init__(self):
        self.lock = threading.Lock()
        pg.mixer.init()

        self.sounds = {
            "chop_tree":[
                self.load("sounds/chop_tree/industrial_tools_axe_chop_wood_002.mp3"),
                self.load("sounds/chop_tree/industrial_tools_axe_chop_wood_004.mp3"),
                self.load("sounds/chop_tree/industrial_tools_axe_chop_wood_005.mp3"),
                self.load("sounds/chop_tree/industrial_tools_axe_chop_wood_007.mp3"),
            ],
            "fell_tree":[
                self.load("sounds/split_tree/industrial_tools_axe_chop_wood_003.mp3"),
                self.load("sounds/split_tree/industrial_tools_axe_chop_wood_006.mp3"),
                self.load("sounds/split_tree/industrial_tools_axe_chop_wood_008.mp3"),
                self.load("sounds/split_tree/industrial_tools_axe_chop_wood_009.mp3"),
            ],
            "unpack":[
                self.load("sounds/misc/186719__andromadax24__chime_01.wav")
            ],
            "music":[
                self.load("sounds/music/559836__migfus20__relaxing-music.wav"),
                self.load("sounds/music/683268__migfus20__relaxing-chiptune-music.mp3"),
                self.load("sounds/music/714924__muyo5438__a-positive-and-inspiring-ambient.mp3"),
                self.load("sounds/music/723287__migfus20__relaxing-jazz-music-loop.mp3")
            ]
        }

    def load(self, path):
        return pg.mixer.Sound(path)
    
    def play_random(self, category):
        with self.lock:
            if category in self.sounds:
                r = random.randint(0, len(self.sounds[category])-1)
                self.sounds[category][r].play()
                
    def play(self, category, num):
        with self.lock:
            if category in self.sounds:
                if num < len(self.sounds[category]):
                    self.sounds[category][num].play()
                