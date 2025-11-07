import json
import os
import pytmx
import pygame


script_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(script_path))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
new_path = os.path.dirname(BASE_DIR)

def get_asset(*path_parts):
    return os.path.join(ASSETS_DIR, *path_parts)

tmx_path = new_path + "\\assets\\maps\\island.tmx"

tmx_data = pytmx.load_pygame(tmx_path)



dialogue_zone = []

for obj in tmx_data.objects:
    if obj.type == "dialogues":
        zone_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        dialogue_zone.append((zone_rect, obj.name))
        


class Dialogue:
    def __init__(self, quest):
        with open(os.path.join(new_path, "assets", "dialogues.json"), "r", encoding="utf-8") as f:
            self.dialogue = json.load(f)
            self.dialogue_temp = []
            self.dialogue_advencement = 0
            self.actual_dialogue = ""
            self.quest = quest
        
    
    def active_dialogue(self, pnj):
        self.dialogue_temp = self.dialogue[pnj]["data"]   
        if self.dialogue_advencement == len(self.dialogue_temp):
            self.dialogue_advencement = 0
            self.actual_dialogue = ""
            if not self.dialogue[pnj]["Active_quete"] == "Aucune":
                self.quest.creer_quest(self.dialogue[pnj]["Active_quete"])
            return False
        else:
            self.actual_dialogue = self.dialogue_temp[self.dialogue_advencement]
            self.dialogue_advencement += 1
            return True
        

class Dialogue_zone_interaction:

    def player_is_in_dialogue_zone(player_rect):
        for zone in dialogue_zone:
            
            if player_rect.colliderect(zone[0]):
                
                return zone[1] 
        return None

