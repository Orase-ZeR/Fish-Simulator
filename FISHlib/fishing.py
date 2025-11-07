import pygame
import random
import os
from pygame.locals import *
import pytmx
from FISHlib.quest import Quest



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
new_path = os.path.dirname(BASE_DIR)
print(new_path)
def get_asset(*path_parts):
    return os.path.join(ASSETS_DIR, *path_parts)

tmx_path = new_path + "\\assets\\maps\\island.tmx"

tmx_data = pytmx.load_pygame(tmx_path)

fishing_zones = []
for obj in tmx_data.objects:
    if obj.type == "fishing_zones":
        zone_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        fishing_zones.append(zone_rect)

font = pygame.font.Font(None, 36)
text_surface = font.render("e", True, (255, 255, 255))


SPRITE_FISH = {
    "common": {
        "Poisson_Bar": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonBar.png").convert_alpha(), (16, 16)), 12),
        "Poisson_Blob": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonBlob.png").convert_alpha(), (16, 16)), 15),
        "Poisson_Truite": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonTruite.png").convert_alpha(), (32, 16)), 26)
    },
    "uncommon": {
        "Poisson_Crevette": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonCrevette.png").convert_alpha(), (16, 16)), 20),
        "Poisson_Pieuvre": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonPieuvre.png").convert_alpha(), (16, 16)),23)
    },
    "rare": {
        "Poisson_Espadon": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonEspadon.png").convert_alpha(), (32, 16)), 58),
        "Poisson_Rouge": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonRouge.png").convert_alpha(), (16, 16)), 34)
    },
    "epic": {
        "Poisson_Diable_Noir": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonDiableNoir.png").convert_alpha(), (16, 16)), 114)
    },
    "legendary": {
        "Poisson_Monstre_Marin": (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fish\\SpritePoissonMonstreMarin.png").convert_alpha(), (64, 32)), 462)
    }
}

SPRITE_FISHING_BAR = {
    "Fishing bar" : (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fishing\\fishing_bar.png").convert_alpha(), (248, 32)), (248, 32)),
    "Fishing bar selector" : (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fishing\\fishing_bar_selector.png").convert_alpha(), (8, 32)), (8, 32)),
    "common" : (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fishing\\fishing_bar_commun.png").convert_alpha(), (128, 16)), (128, 16)),
    "uncommon" : (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fishing\\fishing_bar_peu_commun.png").convert_alpha(), (96, 16)), (96, 16)),
    "rare" : (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fishing\\fishing_bar_rare.png").convert_alpha(), (64, 16)), (64, 16)),
    "epic" : (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fishing\\fishing_bar_epic.png").convert_alpha(), (32, 16)), (32, 16)),
    "legendary" : (pygame.transform.scale(pygame.image.load(new_path + "\\assets\\fishing\\fishing_bar_legendaire.png").convert_alpha(), (16, 16)), (16, 16))
}

class Fishing_zone_interaction:

    @staticmethod
    def is_in_fishing_zone(player_rect):
        for zone in fishing_zones:
            if player_rect.colliderect(zone):
                return True
        return False

    
    @staticmethod 
    def draw(screen, pos, sprite = text_surface):
        screen.blit(sprite, pos)


    @staticmethod
    def choice_rarity(pre_rarity):
        number = random.randint(1,100)
        if pre_rarity == None:
            return True ,"common"
        elif pre_rarity == 'common' and number <= 60:
            return True, "uncommon"
        elif pre_rarity == 'uncommon' and number <= 35:
            return True, "rare"
        elif pre_rarity == 'rare' and number <= 25:
            return True, "epic"
        elif pre_rarity == 'epic' and number <= 15:
            return True, "legendary"
        else:
            return False, pre_rarity

    
    @staticmethod
    def in_progess_fishing(pre_rarity, player_is_fishing ,rect_sprite_barre, rect_sprite_selector):
        
        active_overlay, rarity = Fishing_zone_interaction.choice_rarity(pre_rarity)
        
        if active_overlay and not player_is_fishing:

            return rarity, True, SPRITE_FISHING_BAR["Fishing bar"][0], SPRITE_FISHING_BAR[rarity][0], SPRITE_FISHING_BAR["Fishing bar selector"][0], False
        
        elif active_overlay:
            print(rect_sprite_barre, rect_sprite_selector)
            return rarity, True, SPRITE_FISHING_BAR["Fishing bar"][0], SPRITE_FISHING_BAR[rarity][0], SPRITE_FISHING_BAR["Fishing bar selector"][0], not Fishing_zone_interaction.rects_touch_or_overlap(rect_sprite_barre, rect_sprite_selector)
        else:
            print(rect_sprite_barre, rect_sprite_selector)
            return rarity, False, None, None, None, not Fishing_zone_interaction.rects_touch_or_overlap(rect_sprite_barre, rect_sprite_selector)
    
    @staticmethod
    def rects_touch_or_overlap(r1, r2):
        return not (r1.right < r2.left or r1.left > r2.right or
                r1.bottom < r2.top or r1.top > r2.bottom)



class Fish(pygame.sprite.Sprite):
    def __init__(self, screen, player_rect, rarity, id, image = None, name = None, price = None):
        
        super().__init__()
        self.id = id
        self.rarity = rarity
        print(name, image)
        if name == None:
            self.name = random.choice(list(SPRITE_FISH[rarity].keys()))
        else:
            self.name = name

        if image == None:
            self.image = SPRITE_FISH[rarity][self.name][0]
        else:
            self.image = image
        
        self.screen = screen
        self.player_rect = player_rect
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.player_rect.x, self.player_rect.y)
        if price == None:
            self.price = SPRITE_FISH[rarity][self.name][1]
        else:
            self.price = price
    def poisson_pecher(self, quest):
        if Fishing_zone_interaction.is_in_fishing_zone(self.player_rect):
            quest.verif_objet(self.name)
            self.rect = self.image.get_rect()
            self.rect.x = self.player_rect.x
            self.rect.y = self.player_rect.y
            return (0 ,self.image, self.rect)
            
