import pygame as pg
from settings import *
import threading
import random
import json
from utility import remove_padding_and_scale

class SpriteAssetManager:
    def __init__(self):
        self.images = {}
        self.lock = threading.Lock()

    def load(self, path, resize:tuple=None, remove_padding=False):
        with self.lock:
            image_id = f"path={path}"
            
            # always save the base image if not saved yet
            if f"path={path}" not in self.images:
                image = pg.image.load(path).convert_alpha()
                self.images[image_id] = image

            # if modifications were passed, also save with those modifications
            if remove_padding:
                image_id += f"&resize={resize}"
            if resize:
                image_id += f"&remove_padding={remove_padding}"
            
            if image_id not in self.images:
                image = pg.transform.scale(image,resize)
                
                # remove padding if needed
                if remove_padding:
                    image = remove_padding_and_scale(image)
                # resize if needed
                if resize:
                    image = pg.transform.scale(image, resize)

                # save the final image
                self.images[image_id] = image

            # hand out copies to avoid race conditions
            # TODO there's probably a better way but not sure what it is right now
            return self.images[image_id].copy()

    def load_from_tilesheet(self, path, row_index, col_index, tile_size, resize:tuple=None, remove_padding=False):
        if f"path={path}" not in self.images:
            sheet = pg.image.load(path).convert_alpha()
            self.images[f"path={path}"] = sheet

        with self.lock:
            # generate the image_id
            image_id = f"path={path}?row={row_index}&col={col_index}&tilesize={tile_size}"
            if resize:
                image_id += f"&resize={resize}"
            if remove_padding:
                image_id += f"&remove_padding={remove_padding}"
            
            if image_id not in self.images:
                # Extract a single image from spritesheet
                x = col_index * tile_size
                y = row_index * tile_size

                tile_rect = pg.Rect(x, y, tile_size, tile_size)

                # load the base image
                image = self.images[f"path={path}"].subsurface(tile_rect)
                # remove padding if needed
                if remove_padding:
                    image = remove_padding_and_scale(image)
                # resize if needed
                if resize:
                    image = pg.transform.scale(image,resize)
                
                # save the final image
                self.images[image_id] = image
            
            # return a copy of the final image
            return self.images[image_id].copy()
        
    def load_from_spritesheet(self, path, topleft:tuple, width:int, height:int, resize:tuple=None, remove_padding=False):
        with self.lock:
            if f"path={path}" not in self.images:
                sheet = pg.image.load(path).convert_alpha()
                self.images[f"path={path}"] = sheet
            
            # generate the image_id
            image_id = f"path={path}?topleft={topleft}&width={width}&height={height}"
            if resize:
                image_id += f"&resize={resize}"
            if remove_padding:
                image_id += f"&remove_padding={remove_padding}"

            if image_id not in self.images:
                # Extract a single image from spritesheet by pixel coordinates
                tile_rect = pg.Rect(topleft[0], topleft[1], width, height)
                
                # load the base image
                image = self.images[f"path={path}"].subsurface(tile_rect)
                # remove padding if needed
                if remove_padding:
                    image = remove_padding_and_scale(image)
                # resize if needed
                if resize:
                    image = pg.transform.scale(image,resize)

                self.images[image_id] = image

            return self.images[image_id].copy()
        
class SoundAssetManager:
    def __init__(self):
        self.lock = threading.Lock()
        pg.mixer.init()

        self.sounds = {
            "chop_tree":[
                self.load("sounds/tree/chop/industrial_tools_axe_chop_wood_002.mp3"),
                self.load("sounds/tree/chop/industrial_tools_axe_chop_wood_004.mp3"),
                self.load("sounds/tree/chop/industrial_tools_axe_chop_wood_005.mp3"),
                self.load("sounds/tree/chop/industrial_tools_axe_chop_wood_007.mp3"),
            ],
            "fell_tree":[
                self.load("sounds/tree/fell/industrial_tools_axe_chop_wood_003.mp3"),
                self.load("sounds/tree/fell/industrial_tools_axe_chop_wood_006.mp3"),
                self.load("sounds/tree/fell/industrial_tools_axe_chop_wood_008.mp3"),
                self.load("sounds/tree/fell/industrial_tools_axe_chop_wood_009.mp3"),
            ],
            "chop_rock":[
                self.load("sounds/rock/chop/stone-001.wav"),
                self.load("sounds/rock/chop/stone-002.wav"),
            ],
            "fell_rock":[
                self.load("sounds/rock/fell/stone-003.wav"),
            ],
            "unpack":[
                self.load("sounds/misc/186719__andromadax24__chime_01.wav")
            ],
            "music":[
                self.load("sounds/music/559836__migfus20__relaxing-music.wav"),
                self.load("sounds/music/683268__migfus20__relaxing-chiptune-music.mp3"),
                self.load("sounds/music/714924__muyo5438__a-positive-and-inspiring-ambient.mp3"),
                self.load("sounds/music/723287__migfus20__relaxing-jazz-music-loop.mp3")
            ],
            "skillpoint":[
                self.load("sounds/misc/186719__andromadax24__chime_01.wav")
            ],
            "bat_wake":[
                self.load("sounds/bat/wake/batsound-001.wav"),
                self.load("sounds/bat/wake/batsound-002.wav"),
                self.load("sounds/bat/wake/batsound-003.wav"),
                self.load("sounds/bat/wake/batsound-004.wav"),
                self.load("sounds/bat/wake/batsound-005.wav"),
                self.load("sounds/bat/wake/batsound-006.wav"),
                self.load("sounds/bat/wake/batsound-007.wav")
            ],
            "bat_damage":[
                self.load("sounds/bat/damage/385046__mortisblack__damage.ogg")
            ],
            "bat_die":[
                self.load("sounds/bat/die/712917__greyfeather__retro-mouse-sound.wav")
            ],
            "player_damage":[
                self.load("sounds/player/damage/404108__deathscyp__damage-2.wav")
            ],
            "player_dodge":[
                self.load("sounds/player/dodge/585256__lesaucisson__swoosh-2.mp3")
            ],
            "slime":[
                self.load("sounds/slime/340794__kuchenanderung1__slime-squish.wav"),
                self.load("sounds/slime/353250__zuzek06__slimejump.wav")
            ],
            "shutter":[
                self.load("sounds/misc/shutter.wav")
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
                
class JSONFileManager:
    def __init__(self):
        self.files = {}

    def read(self, path):
        if path not in self.files:
            with open(path) as f_in:
                js = json.load(f_in)
            self.files[path] = js
        
        return self.files[path]
