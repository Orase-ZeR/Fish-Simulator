import pygame
import sys
import os
from pygame.locals import *
from PIL import Image, ImageFilter
import pytmx, pyscroll
from FISHlib.inventory import Inventory, Inventory_Engine, Cursor, Search_Bar, Item, ITEM_TEXTURES
from FISHlib.fishing import Fish, Fishing_zone_interaction, SPRITE_FISH
from FISHlib.dialogue import dialogue_zone, Dialogue, Dialogue_zone_interaction
import random
import datetime
from FISHlib.quest import *
import cv2

pygame.init()

# --- Fenêtre ---
fenetre = pygame.display.set_mode((1080, 720), RESIZABLE)
pygame.display.set_caption("FISH SIM GOTY 2025")
clock = pygame.time.Clock()

# --- Répertoires ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
# Chargement du GIF animé (à faire une seule fois avant la boucle)
gif_hotkey_e = Image.open(BASE_DIR+"/assets/gui/SpriteHotkeyEAnimation.gif")
gif_frames = []
quest_bg_base = pygame.image.load(os.path.join(BASE_DIR, "assets/gui/Quete.png")).convert_alpha()
quest_bg_w, quest_bg_h = quest_bg_base.get_size()

# Extraction de toutes les frames du GIF
try:
    while True:
        frame = gif_hotkey_e.copy().convert("RGBA")
        frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
        frame = pygame.transform.scale(frame, (frame.get_width() // 12, frame.get_height() // 12))
        gif_frames.append(frame)
        gif_hotkey_e.seek(gif_hotkey_e.tell() + 1)
except EOFError:
    pass  # fin du GIF

gif_frame_index = 0
gif_frame_timer = 0
gif_frame_delay = 100  # en ms (vitesse d’animation)


def get_asset(*path_parts):
    return os.path.join(ASSETS_DIR, *path_parts)
font_path = get_asset("DTM-Sans.otf")
if os.path.exists(font_path):
    title_font = pygame.font.Font(font_path, 150)  # taille large
else:
    print("Police DTM-Sans introuvable, fallback system font utilisée.")
    title_font = pygame.font.SysFont(None, 150)
quest_font = pygame.font.Font(font_path, 40)
tmx_path = BASE_DIR + "\\assets\\maps\\island.tmx"

tmx_data = pytmx.load_pygame(tmx_path)
collision_zones = []

tile_size = tmx_data.tilewidth  
coins = 0
font_money = pygame.font.Font(font_path, 36)  

health_bar_base = pygame.image.load(os.path.join(BASE_DIR, "assets/gui/SpriteHealthBar.png")).convert_alpha()
base_w, base_h = health_bar_base.get_size()

# Redimension si nécessaire (optionnel)
scale_factor = 0.2  # ajuste selon la taille de ton image
new_width = int(health_bar_base.get_width() * scale_factor)
new_height = int(health_bar_base.get_height() * scale_factor)
health_bar_img = pygame.transform.scale(health_bar_base, (new_width, new_height))

health_bar_width, health_bar_height = new_width, new_height
money_bag_img = pygame.image.load(os.path.join(BASE_DIR, "assets/gui/SpriteSacD'argent.png")).convert_alpha()
scale_factor = 0.75
new_width = int(money_bag_img.get_width() * scale_factor)
new_height = int(money_bag_img.get_height() * scale_factor)
money_bag_img = pygame.transform.scale(money_bag_img, (new_width, new_height))
# --- ICONES (on garde la version "base" non-scalée pour recalculer la taille dynamiquement) ---
icon_inv_base = pygame.image.load(get_asset("gui", "SpriteSacADos.png")).convert_alpha()
icon_quest_base = pygame.image.load(get_asset("gui", "Quete.png")).convert_alpha()

# tailles originales
icon_inv_orig_w, icon_inv_orig_h = icon_inv_base.get_size()
icon_quest_orig_w, icon_quest_orig_h = icon_quest_base.get_size()

# facteur de référence basé sur ta fenêtre de base (1080x720)
UI_BASE_W, UI_BASE_H = 1080, 720

# fact scale constants requested:
# - tu avais déjà divisé par 3 ; tu veux diviser ENCORE par 2 => total factor_inv = 1/6
# - pour le parchemin on prend la même base 1/6 puis on multiplie par 1.3
INV_BASE_SCALE = 1.0 / 6.0
QUEST_BASE_SCALE = (1.0 / 6.5) 

# police des lettres sous les icônes : on calcule dynamiquement plus bas selon la fenêtre
letter_font = None  # défini plus bas dans le code de draw (pour suivre le resize)


# état d'affichage du panneau quêtes
show_quest_panel = False

money_bag_width, money_bag_height = new_width, new_height

layer = None
for l in tmx_data.layers:
    if hasattr(l, "id") and l.id == 2:
        layer = l
        break

if layer is not None and hasattr(layer, "tiles"):
    for x, y, image in layer.tiles():
        rect = pygame.Rect(
            x * tile_size,
            y * tmx_data.tileheight,
            tile_size,
            tmx_data.tileheight
        )
        collision_zones.append(rect)

for obj in getattr(tmx_data, "objects", []):
    name = (getattr(obj, "name", "") or "").lower()
    otype = (getattr(obj, "type", "") or "").lower()
    oclass = (getattr(obj, "class", "") or "").lower()

    if otype == "collision" or name == "obj" or oclass == "objet":
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        collision_zones.append(rect)
# --- SPAWN ---
def get_spawn_position(tmx_path):
    try:
        try:
            tmx = pytmx.util_pygame.load_pygame(tmx_path)
        except Exception:
            tmx = pytmx.TiledMap(tmx_path)
    except Exception as e:
        print("Erreur chargement TMX pour trouver le spawn:", e)
        return None

    for obj in getattr(tmx, "objects", []):
        try:
            name = (obj.name or "").lower()
        except Exception:
            name = ""
        try:
            otype = (obj.type or "").lower()
        except Exception:
            otype = ""
        try:
            cls = (obj.properties.get("class", "") if hasattr(obj, "properties") else "") or ""
            cls = cls.lower()
        except Exception:
            cls = ""

        if name == "spawn" or otype == "spawn" or cls == "spawn":
            return (int(obj.x), int(obj.y))
    return None


zoom_level = 2.5
DRAW_SCALE = 1
# --- Constantes animation / joueur (pour la sprite-sheet) ---
FRAME_WIDTH = 16
FRAME_HEIGHT = 32
WALK_ANIMATION_SPEED = 0.05
IDLE_ANIMATION_SPEED = 0.3
PLAYER_DRAW_WIDTH = FRAME_WIDTH * DRAW_SCALE
PLAYER_DRAW_HEIGHT = FRAME_HEIGHT * DRAW_SCALE
# --- Charger la sprite-sheet via get_asset (place ton fichier dans assets/) ---
SPRITE_SHEET = pygame.image.load(get_asset("Player", "P1", "anim_perso_sheet.png")).convert_alpha()

# --- Charger l'image de fond (title screen) OU vidéo ---
VIDEO_PATH = get_asset("titlescreen", "title.mkv")
video_cap = cv2.VideoCapture(VIDEO_PATH)
if not video_cap.isOpened():
    print("Impossible de charger la vidéo du title screen, fallback image utilisée.")
    video_cap = None
    pil_img = Image.open(get_asset("titlescreen", "titlescreen.jpg"))
else:
    pil_img = None  # on désactive l'image statique si la vidéo marche

# --- Joueur (valeurs par défaut) ---
player_size = 8
player_color = (0, 0, 0)
player_x = 100
player_y = 100
player_speed = 3  # utilisé par la logique globale
quest = Quest(fenetre)

# --- Variables inventaire ---
inventory_list = [Inventory("Main", 1, 3, 50, 50, sorting_active=False, search_active=False)]
inventory_engine = Inventory_Engine(inventory_list)
cursor = Cursor()
search_bar = None
show_inventory = False  # afficher/inventaire ouvert avec 'I'
sprite_selector_I = None

liste_sprite = []
liste_sprite_fish = []
liste_sprite_quete = []

# --- Variable pour la peche ---
player_is_in_fishing_zone = False
player_is_fishing = False
can_fish = False
rarity = None
speed = 10
layer_base = 15
deplacement = [i for i in range(0, 230, speed)] + sorted([i for i in range(0, 230, speed)], reverse=True)
index = 0
fail = False
sprite_rarity_rect = None
sprite_selector_rect = None
shop_talk = False
stick1 = Fish(screen=fenetre, player_rect=pygame.Rect(3984, 2710, 16, 32), rarity="common", id=(len(liste_sprite_fish)), image=ITEM_TEXTURES["stick"], name="stick", price=100000)
liste_sprite.append((len(liste_sprite_fish),stick1))
liste_sprite_fish.append((len(liste_sprite_fish),stick1))
stick2 = Fish(screen=fenetre, player_rect=pygame.Rect(4029, 2767, 16, 32), rarity="common", id=(len(liste_sprite_fish)), image=ITEM_TEXTURES["stick"], name="stick", price=100000)
liste_sprite.append((len(liste_sprite_fish),stick2))
liste_sprite_fish.append((len(liste_sprite_fish),stick2))
string = Fish(screen=fenetre, player_rect=pygame.Rect(3984, 2620, 16, 32), rarity="common", id=(len(liste_sprite_fish)), image=ITEM_TEXTURES["string"], name="string", price=100000)
liste_sprite.append((len(liste_sprite_fish),string))
liste_sprite_fish.append((len(liste_sprite_fish),string))

def play_music(Musique):
        pygame.mixer.music.load(os.path.join(BASE_DIR, "assets", "music", Musique))
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.2)
        current_music = Musique

def play_sound(Sound):
        pygame.mixer.music.load(os.path.join(BASE_DIR, "assets", "music", Sound))
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.2)

# --- Bouton image ---
def image_button(surface, x, y, image_name, scale=2):
    bouton_img = pygame.image.load(get_asset("titlescreen", image_name)).convert_alpha()
    width, height = bouton_img.get_size()
    bouton_img = pygame.transform.scale(bouton_img, (width * scale, height * scale))
    rect = bouton_img.get_rect(topleft=(x, y))
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    surface.blit(bouton_img, rect.topleft)
    if rect.collidepoint(mouse) and click[0]:
        return True
    return False


# --- Gestion des sprites
def supprimer_sprite(id, liste):
    for sprite in liste[:]:
        if sprite[0] == id:
            liste.remove(sprite)
    return liste


def chercher_sprite(id, liste):
    for indice, sprite in enumerate(liste):
        if sprite[0] == id:
            return indice
    return None


def afficher_sprite(liste_sprite, fenetre, map_group_ref):
    """
    Si map_group_ref est None on blit les surfaces directement (UI sprites).
    Sinon on ajoute temporairement au groupe (pour que pyscroll les dessine).
    """
    try:
        if map_group_ref:
            for sprite in liste_sprite:
                try:
                    map_group_ref.add(sprite[1], layer=layer_base)
                except Exception:
                    # si sprite[1] n'est pas un sprite pyscroll-compatible, on ignore
                    pass
            map_group_ref.draw(fenetre)
            for sprite in liste_sprite:
                try:
                    map_group_ref.remove(sprite[1])
                except Exception:
                    pass
        else:
            # fallback: blit any surfaces that look like ImageSprite directly
            for sprite in liste_sprite:
                try:
                    rect = sprite[1].rect
                    fenetre.blit(sprite[1].image, rect.topleft)
                except Exception:
                    pass
    except Exception as e:
        # garder en console pour debug si besoin
        print("afficher_sprite error:", e)


class ImageSprite(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

class ImageGIF:
    def __init__(self, path, base_x, base_y, base_scale=1, base_window=(1080, 720), frame_duration=100):
        """
        base_x, base_y : origine en pixels à la window de référence (base_window)
        base_scale : scale relatif à la window de référence
        """
        self.base_x = base_x
        self.base_y = base_y
        self.base_scale = base_scale
        self.base_window = base_window
        self.frame_duration = frame_duration

        self.frames = []
        self.index = 0
        self.last_update = pygame.time.get_ticks()
        self.load_frames(path)  # remplit self.frames

    def load_frames(self, path):
        """Charge les frames depuis le fichier GIF (utilisé en init et lors d'un set_path)."""
        from PIL import Image, ImageSequence
        self.frames = []
        pil_image = Image.open(path)
        for frame in ImageSequence.Iterator(pil_image):
            frame = frame.convert("RGBA")
            data = frame.tobytes()
            size = frame.size
            mode = frame.mode
            surf = pygame.image.fromstring(data, size, mode)
            self.frames.append(surf)
        # remettre l'index à 0 pour éviter des out-of-range après reload
        self.index = 0

    def set_path(self, path, frame_duration=None):
        """Change le GIF affiché sans recréer l'objet (préserve base_*). Optionnel frame_duration."""
        if frame_duration is not None:
            self.frame_duration = frame_duration
        self.load_frames(path)

    def update(self):
        """Avance la frame (ne touche pas au rescaling / positionnement)."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.index = (self.index + 1) % len(self.frames)
            self.last_update = now

    def draw(self, surface):
        """Calcule taille/position à la volée en fonction de la taille actuelle de la fenêtre."""
        if not self.frames:
            return
        window_w, window_h = surface.get_size()

        # facteurs
        scale_x = window_w / self.base_window[0]
        scale_y = window_h / self.base_window[1]
        # on peut utiliser min ou moyenne; garde la même méthode que ton left (ici moyenne)
        scale_factor = (scale_x + scale_y) / 2 * self.base_scale

        # position calculée à partir de la base
        x = int(self.base_x * scale_x)
        y = int(self.base_y * scale_y)

        current_frame = self.frames[self.index]
        w, h = current_frame.get_size()
        new_w = max(1, int(w * scale_factor))
        new_h = max(1, int(h * scale_factor))
        scaled_frame = pygame.transform.smoothscale(current_frame, (new_w, new_h))

        surface.blit(scaled_frame, (x, y))

# --- Classe Player (hérite Sprite pour pyscroll) ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_override=None):
        super().__init__()
        self._layer = 6
        self.x = x
        self.y = y
        self.speed = speed_override if speed_override is not None else 2
        self.direction = "down"
        self.is_moving = False
        self.current_frame = 0
        self.animation_timer = 0
        self.animations = self.load_sprites()

        self.image = pygame.Surface((PLAYER_DRAW_WIDTH, PLAYER_DRAW_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 16)
        self.old_position = self.rect.copy()

    def save_location(self): self.old_position = self.rect.copy()

    def move_back(self):
        self.rect.topleft = self.old_position

    def load_sprites(self):
        animations = {}
        frames_per_line = {
            "walk_up": 12,
            "walk_down": 12,
            "walk_right": 10,
            "walk_left": 10,
            "idle_up": 5,
            "idle_down": 5,
            "idle_right": 5,
            "idle_left": 5,
        }

        for row, (key, frame_count) in enumerate(frames_per_line.items()):
            animations[key] = []
            for col in range(frame_count):
                rect = pygame.Rect(col * FRAME_WIDTH, row * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
                frame = SPRITE_SHEET.subsurface(rect).copy()
                animations[key].append(frame)
        return animations
    

    def update(self, dt, keys):
        prev_direction = self.direction
        self.is_moving = False
        if (keys[K_z] or keys[K_UP]) and not dialogue_active:
            self.y -= self.speed
            self.direction = "up"
            self.is_moving = True
        elif (keys[K_s] or keys[K_DOWN]) and not dialogue_active:
            self.y += self.speed
            self.direction = "down"
            self.is_moving = True          
        elif (keys[K_d] or keys[K_RIGHT]) and not dialogue_active:
            self.x += self.speed
            self.direction = "right"
            self.is_moving = True
        elif (keys[K_q] or keys[K_LEFT]) and not dialogue_active:
            self.x -= self.speed
            self.direction = "left"
            self.is_moving = True       
        else:
            self.direction = prev_direction

        current_anim = f"walk_{self.direction}" if self.is_moving else f"idle_{self.direction}"
        frame_count = len(self.animations[current_anim])
        animation_speed = WALK_ANIMATION_SPEED if self.is_moving else IDLE_ANIMATION_SPEED

        self.animation_timer += dt
        if self.animation_timer >= animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % frame_count

        frame_list = self.animations[current_anim]
        raw_frame = frame_list[self.current_frame % len(frame_list)]
        self.image = pygame.transform.scale(raw_frame, (PLAYER_DRAW_WIDTH, PLAYER_DRAW_HEIGHT))
        self.rect.topleft = (int(self.x), int(self.y))
        self.feet.width = int(self.rect.width * 0.5)
        self.feet.height = 16
        self.feet.topleft = (
            self.rect.centerx - self.feet.width // 2.5,
            self.rect.bottom - self.feet.height + 2,
        )

        
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def maybe_draw_interaction_gif(self,
                                   dt,
                                   gif_frames,
                                   gif_frame_timer,
                                   gif_frame_index,
                                   gif_frame_delay,
                                   liste_sprite,
                                   player_size,
                                   ImageSpriteClass):
        if not gif_frames:
            return gif_frame_timer, gif_frame_index

        # Avancement du timer du GIF (indépendant du positionnement)
        gif_frame_timer += dt * 1000  # dt en secondes -> ms
        if gif_frame_timer >= gif_frame_delay:
            gif_frame_timer = 0
            gif_frame_index = (gif_frame_index + 1) % len(gif_frames)

        # Frame actuelle du GIF
        current_gif_frame = gif_frames[gif_frame_index]

        # Position recalculée à CHAQUE frame (centré sur le joueur)
        gif_x = self.x + (player_size // 2) - (current_gif_frame.get_width() // 2) + 4
        gif_y = self.y - current_gif_frame.get_height() - 1

        # Crée le sprite en position actuelle du joueur
        gif_sprite = ImageSpriteClass(current_gif_frame, (gif_x, gif_y))
        liste_sprite.append(("Sprite Interaction", gif_sprite))

        return gif_frame_timer, gif_frame_index

# --- Charger une map Tiled (version robuste) ---
def load_map(filename, screen_size, zoom=1.0):
    if not os.path.isabs(filename):
        candidate = filename
    else:
        candidate = filename

    if not os.path.isfile(candidate):
        maps_dir = os.path.join(ASSETS_DIR, "maps")
        available = []
        if os.path.isdir(maps_dir):
            available = [f for f in os.listdir(maps_dir) if f.lower().endswith(".tmx")]
        raise FileNotFoundError(
            f"Map introuvable: {candidate}\nAttendu dans: {os.path.join(ASSETS_DIR, 'maps')}\nMaps disponibles: {available}"
        )

    try:
        tmx_data = pytmx.util_pygame.load_pygame(candidate)
    except Exception:
        tmx_data = pytmx.load_pygame(candidate)

    map_data = pyscroll.data.TiledMapData(tmx_data)
    map_layer = pyscroll.orthographic.BufferedRenderer(map_data, size=fenetre.get_size())

    # appliquer le zoom
    map_layer.zoom = zoom

    return map_layer


# --- Initialisation du Player ---
player = Player(player_x, player_y, speed_override=player_speed)

# --- Boucle principale ---
running = True
fullscreen = False
menu = True
map_layer = None
map_group = None
last_zone = None
play_music("main_menu.ogg")
current_music = "main_menu.ogg"
previous_music = None

fish_sizes = {
    "Poisson_Bar": (1, 1),
    "Poisson_Blob": (1, 1),
    "Poisson_Truite": (2, 1),
    "Poisson_Crevette": (1, 1),
    "Poisson_Pieuvre": (1, 1),
    "Poisson_Espadon": (2, 1),
    "Poisson_Rouge": (1, 1),
    "Poisson_Diable_Noir": (2, 2),
    "Poisson_Monstre_Marin": (3, 2)
}

dialogue = Dialogue(quest)
dialogue_active = False  # indique si un dialogue est en cours
dialogue_lines = []      # lignes actuelles du dialogue
dialogue_index = 0       # ligne actuelle
dialogue_timer = 0       # pour temporiser le défilement
dialogue_speed = 0.2     # secondes entre chaque ligne
dialogue_music_played = False
# --- Détection du mode plein écran ---
flags = pygame.display.get_surface().get_flags()
is_fullscreen = bool(flags & pygame.FULLSCREEN)

# --- Taille du gif selon le mode ---
center_x = fenetre.get_width() // 2

if is_fullscreen :
    gif_left = ImageGIF(get_asset("Player", "SpriteTetePersonnage1.gif"),
    base_x=center_x - fenetre.get_width() * 0.45, base_y=fenetre.get_height() * 0.5,
    base_scale=1, base_window=(1080, 720))

    # créer gif_right "neutre" au start — on le remplace ensuite avec set_path
    gif_right = ImageGIF(get_asset("Player", "SpriteTeteOie1.gif"),
    base_x=fenetre.get_width() * 0.7,
    base_y=fenetre.get_height() * 0.5,
    base_scale=0.6,
    base_window=(1080, 720))

else :
    gif_left = ImageGIF(get_asset("Player", "SpriteTetePersonnage1.gif"),
    base_x=center_x - fenetre.get_width() * 0.45, base_y=fenetre.get_height() * 0.5,
    base_scale=0.6, base_window=(1080, 720))

    # créer gif_right "neutre" au start — on le remplace ensuite avec set_path
    gif_right = ImageGIF(get_asset("Player", "SpriteTeteOie1.gif"),
    base_x=fenetre.get_width() * 0.7,
    base_y=fenetre.get_height() * 0.5,
    base_scale=0.6,
    base_window=(1080, 720))

# store some UI button dims (used each frame)
while running:
    dt = clock.tick(60) / 1000.0
    player.old_position = player.rect.copy()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_F11:
                fullscreen = not fullscreen 
                if fullscreen:
                    fenetre = pygame.display.set_mode((0, 0), FULLSCREEN)
                else:
                    fenetre = pygame.display.set_mode((1080, 720), RESIZABLE)
            elif event.key == K_i and not player_is_fishing:
                show_inventory = not show_inventory
            elif event.key == K_m:
                print(f"player_rect: {player.rect}")
            if event.key == pygame.K_r:
                    # rotate only if an item is held and it's not stackable (or size != (1,1))
                    if cursor.item is not None and not getattr(cursor.item, "stackable", False):
                        cursor.item.rotate()                    

            elif event.key == K_l:
                show_quest_panel = not show_quest_panel

            
            elif event.key == K_e and Dialogue_zone_interaction.player_is_in_dialogue_zone(player.rect):
                    zone = Dialogue_zone_interaction.player_is_in_dialogue_zone(player.rect)
                    if zone:
                            pecher_quest = quest.quests.get("Pecher son premier poisson")
                            
                            if zone == "port":
                                if pecher_quest and pecher_quest["finish"]:
                                    dialogue_active = dialogue.active_dialogue("Canard4")

                                elif quest.get_name() == "Pecher son premier poisson" and not quest.quests[quest.name_quest]["finish"]:
                                    dialogue_active = dialogue.active_dialogue("Canard5")
                                        
                                elif quest.get_name() == "Fabriquer la canne à pêche" and quest.quests[quest.name_quest]["finish"]:
                                    dialogue_active = dialogue.active_dialogue("Canard3")
                                    inventory_list[0].clear_inventory()
                                    can_fish = True
                                elif quest.get_name() == "Fabriquer la canne à pêche":
                                    dialogue_active = dialogue.active_dialogue("Canard2")
                                else:
                                    dialogue_active = dialogue.active_dialogue("Canard1")
                                
                                gif_right.set_path(get_asset("Player", "SpriteCanardPnj1.gif"), frame_duration=100)

                            elif zone == "shop":
                                if pecher_quest and pecher_quest["finish"] and not shop_talk:
                                    shop_talk = True
                                    dialogue_active = dialogue.active_dialogue("Shop1")
                                elif pecher_quest and pecher_quest["finish"]:
                                    if inventory_list[0].get_item_count() == 0:
                                        dialogue_active = dialogue.active_dialogue("Shop0")
                                    else:
                                        dialogue_active = dialogue.active_dialogue("Shop2")
                                        if not dialogue_active:
                                            
                                            for item in inventory_list[0].get_item_list():
                                                coins += SPRITE_FISH[item.rarity][item.name][1]
                                            inventory_list[0].clear_inventory()
                                if not dialogue_music_played:
                                    previous_music = current_music
                                    play_music("creepy_sound.mp3")
                                    dialogue_music_played = True
                                gif_right.set_path(get_asset("Player", "SpriteTetePnj.gif"), frame_duration=200)




            elif event.key == K_e and player_is_in_fishing_zone and can_fish:
                # appel de la logique de pêche (garde les mêmes signatures que toi)
                
                rarity, player_is_fishing, sprite_barre, sprite_rarity, sprite_selector, fail = Fishing_zone_interaction.in_progess_fishing(
                    rarity,
                    player_is_fishing,
                    sprite_rarity.rect if player_is_fishing else None,
                    sprite_selector_I.rect if player_is_fishing else None,
                )
                liste_sprite = supprimer_sprite("Sprite Barre", liste_sprite)
                liste_sprite = supprimer_sprite("Sprite Rareté", liste_sprite)
                
           
                if not fail:
                    if not player_is_fishing:
                        fish = Fish(screen=fenetre, player_rect=pygame.Rect(player.x, player.y, player_size, player_size), rarity=rarity, id=(len(liste_sprite_fish)))
                        fish_sprite = fish.poisson_pecher(quest)
                        liste_sprite.append((len(liste_sprite_fish), fish))
                        liste_sprite_fish.append((len(liste_sprite_fish), fish))
                        index = 0
                        liste_sprite = supprimer_sprite("Sprite Selector", liste_sprite)
                        fish_size = fish_sizes.get(fish.name, (1, 1))

                        # Création de l'Item avec la rareté du poisson pêché
                        Fisher = Item(
                            fish.name,
                            1,
                            size=fish_size,
                            rarity=rarity,  # on garde la rareté ici
                            stackable=False
                        )
                        
                        rarity = None  # on peut la réinitialiser après coup
                        
                    else:
                        temp_placement = (player.x + random.randint(-107, 107 - sprite_rarity.get_width()), player.y - 24)
                        sprite_barre = ImageSprite(sprite_barre, (player.x - 112, player.y - 32))
                        sprite_rarity = ImageSprite(sprite_rarity, temp_placement)
                        liste_sprite.append(("Sprite Barre", sprite_barre))
                        liste_sprite.append(("Sprite Rareté", sprite_rarity))
                else: 
                    print("Bruh")
                    player_is_fishing = False
                    fail = False
                    rarity = None
                    index = 0
                    liste_sprite = supprimer_sprite("Sprite Selector", liste_sprite)
        # Vérifie si le joueur est dans une zone de pêche
        player_is_in_fishing_zone = Fishing_zone_interaction.is_in_fishing_zone(
            pygame.Rect(player.x, player.y, player_size, player_size)
        ) if quest.get_name() == 'Pecher son premier poisson' else False

        # Supprime toujours l’ancien sprite avant de recréer
        liste_sprite = supprimer_sprite("Sprite Interaction", liste_sprite)

        if player_is_in_fishing_zone and not player_is_fishing and gif_frames:
            # Avancement du timer du GIF (indépendant du positionnement)
            gif_frame_timer += dt * 1000
            if gif_frame_timer >= gif_frame_delay:
                gif_frame_timer = 0
                gif_frame_index = (gif_frame_index + 1) % len(gif_frames)

            # Frame actuelle du GIF (on l’actualise toutes les 100 ms)
            current_gif_frame = gif_frames[gif_frame_index]

            # Position recalculée à CHAQUE frame (60 FPS)
            gif_x = player.x + (player_size // 2) - (current_gif_frame.get_width() // 2) + 4
            gif_y = player.y - current_gif_frame.get_height() - 1

            # Crée le sprite en position actuelle du joueur
            gif_sprite = ImageSprite(current_gif_frame, (gif_x, gif_y))
            liste_sprite.append(("Sprite Interaction", gif_sprite))


        # variables gérées dans la boucle principale (déclare-les avant la boucle)
        # gif_frames = [...]
        # gif_frame_timer = 0.0
        # gif_frame_index = 0
        # gif_frame_delay = 100
        # player_size = PLAYER_DRAW_WIDTH
        # liste_sprite = []

        # vérifie les zones
        in_dialogue = Dialogue_zone_interaction.player_is_in_dialogue_zone(player.rect)
        in_fishing = (Fishing_zone_interaction.is_in_fishing_zone(player.rect) and not player_is_fishing) if quest.get_name() == 'Pecher son premier poisson' else False

        if (in_dialogue or in_fishing) and gif_frames:
            gif_frame_timer, gif_frame_index = player.maybe_draw_interaction_gif(
                dt,
                gif_frames,
                gif_frame_timer,
                gif_frame_index,
                gif_frame_delay,
                liste_sprite,
                player_size,
                ImageSprite  # ou ta classe ImageSprite si nom différent
            )
            


    window_size = fenetre.get_size()
    fenetre.fill((0, 0, 0))  # clear frame
    
    if menu:
        # --- fond (vidéo ou image) ---
        if video_cap:
            ret, frame = video_cap.read()
            if not ret:
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = video_cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (window_size[0], window_size[1]))
                pil_frame = Image.fromarray(frame)
                pil_blur = pil_frame.filter(ImageFilter.GaussianBlur(radius=5))
                background = pygame.image.fromstring(pil_blur.tobytes(), pil_blur.size, pil_blur.mode)
                fenetre.blit(background, (0, 0))
            else:
                if pil_img:
                    pil_resized = pil_img.resize(window_size, Image.LANCZOS)
                    pil_blur = pil_resized.filter(ImageFilter.GaussianBlur(radius=5))
                    background = pygame.image.fromstring(pil_blur.tobytes(), pil_blur.size, pil_blur.mode)
                    fenetre.blit(background, (0, 0))
        else:
            pil_resized = pil_img.resize(window_size, Image.LANCZOS)
            pil_blur = pil_resized.filter(ImageFilter.GaussianBlur(radius=5))
            background = pygame.image.fromstring(pil_blur.tobytes(), pil_blur.size, pil_blur.mode)
            fenetre.blit(background, (0, 0))

        # --- Titre FISHSIM ---
        shadow_offset = 6
        title_text_shadow = title_font.render("FISHSIM", True, (0, 0, 0))
        title_text = title_font.render("FISHSIM", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(window_size[0] // 2, window_size[1] // 2 - 250))
        shadow_rect = title_rect.copy()
        shadow_rect.move_ip(shadow_offset, shadow_offset)
        fenetre.blit(title_text_shadow, shadow_rect)
        fenetre.blit(title_text, title_rect)

        # --- Gestion de l'état des contrôles ---
        if "show_controls" not in globals():
            show_controls = False

        # --- Bouton Touches (toujours visible) ---
        touches_img = pygame.image.load(get_asset("titlescreen", "bouton_touches.png")).convert_alpha()
        touches_img = pygame.transform.scale(touches_img, (touches_img.get_width() * 2, touches_img.get_height() * 2))
        touches_rect = touches_img.get_rect()
        touches_rect.bottomright = (window_size[0] - 30, window_size[1] - 30)
        fenetre.blit(touches_img, touches_rect.topleft)

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if touches_rect.collidepoint(mouse) and click[0]:
            show_controls = not show_controls
            pygame.time.wait(200)  # petit délai anti double-clic

        # --- Affichage selon l'état ---
        if not show_controls:
            # Boutons Jouer / Quitter visibles
            bouton_width, bouton_height = 200, 200
            bouton_x = window_size[0] // 2 - bouton_width // 2 - 20
            bouton_y = window_size[1] // 2 - bouton_height // 2
            espacement = 20

            # Bouton Jouer
            if image_button(fenetre, bouton_x, bouton_y, "bouton_jouer.png", scale=4):
                tmx_path = get_asset("maps", "island.tmx")
                map_layer = load_map(tmx_path, window_size, zoom=zoom_level)
                map_group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)
                map_group.add(player)
                pygame.mixer.music.stop()
                play_sound("game_start.mp3")
                menu = False
                pygame.time.wait(800)
                play_music("valley_sound.mp3")
                last_zone = "map"

                spawn_pos = get_spawn_position(tmx_path)
                if spawn_pos is not None:
                    player.x = spawn_pos[0] - 32 // 2
                    player.y = spawn_pos[1] - 64 // 2
                    player.rect.topleft = (int(player.x), int(player.y))
                    print(f"Player spawn trouvé à {spawn_pos}")
                else:
                    player.x, player.y = 100, 100
                    player.rect.topleft = (int(player.x), int(player.y))
                    print("Aucun spawn trouvé dans le TMX — position par défaut utilisée.")

                menu = False
                pygame.mouse.set_visible(False)
                inventory_list = [Inventory("Sac à dos", 2, 3, 50, 50, sorting_active=False, search_active=False)]
                inventory_engine = Inventory_Engine(inventory_list)
                cursor = Cursor()
                search_bar = None

            # Bouton Quitter
            if image_button(fenetre, bouton_x, bouton_y + bouton_height + espacement, "bouton_quitter.png", scale=4):
                running = False

        else:
            # --- Affichage du panneau de contrôles ---
            font_controls = pygame.font.Font(font_path, 60)
            lignes = [
                "ZQSD : Déplacement",
                "E : Interagir",
                "I : Inventaire",
                "ÉCHAP : Quitter le jeu",
            ]
            start_y = window_size[1] // 2 - (len(lignes) * 60) // 2
            for i, ligne in enumerate(lignes):
                text = font_controls.render(ligne, True, (255, 255, 255))
                rect = text.get_rect(center=(window_size[0] // 2, start_y + i * 80))
                # ombre légère
                shadow = font_controls.render(ligne, True, (0, 0, 0))
                shadow_rect = rect.copy()
                shadow_rect.move_ip(3, 3)
                fenetre.blit(shadow, shadow_rect)
                fenetre.blit(text, rect)

    else:
        # gameplay update + draw
        if map_layer and map_group:
            keys = pygame.key.get_pressed()
            if not player_is_fishing:
                player.update(dt, keys)

                player_rect = player.rect
                current_zone = "map"

                for obj in tmx_data.objects:
                    # Si la zone est définie par le champ TYPE (Tiled)
                    if obj.type == "village_music":
                        zone_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        if player_rect.colliderect(zone_rect):
                            current_zone = "village"
                            break

                if current_zone != last_zone:
                    pygame.mixer.music.stop()
                    if current_zone == "village":
                        play_music("village.ogg")
                    else:
                        play_music("valley_sound.mp3")
                    last_zone = current_zone
            # center la caméra sur le joueur
            map_group.center(player.rect.center)
            # draw map + sprites (pyscroll)
            map_group.draw(fenetre)

            # synchronise pour le reste du code (pêche, collisions, etc.)
            player_x, player_y = player.x, player.y
        else:
            # si pas encore de map_group (sélection de menu), évite crash
            pass

    # fishing moving selector
    if player_is_fishing:
        index += 1
        liste_sprite = supprimer_sprite("Sprite Selector", liste_sprite)
        # safeguard: sprite_selector must be defined (set earlier by fishing logic)
        sprite_selector_I = ImageSprite(sprite_selector, ((player.x - 107 + deplacement[index % (len(deplacement))]), player.y - 32))
        liste_sprite.append(("Sprite Selector", sprite_selector_I))

    # UI sprites drawing (works with or without map_group)
    layer_base += 1
    afficher_sprite(liste_sprite, fenetre, map_group)
    if show_inventory and inventory_engine and cursor:
        inventory_engine.update(cursor, "")           # dessine l'inventaire
        keys = pygame.key.get_pressed()
        cursor.update(keys, (0, 0), 1)                # met à jour le curseur d'inventaire

    if not menu: 
        # optionally show mouse when inventory open
        # --- HUD argent ---
        window_w, window_h = fenetre.get_size()

        # Position de l'image (coin supérieur droit)
        bag_x = window_w - money_bag_width - 20  
        bag_y = 20

        # Dessin de l'image du sac
        fenetre.blit(money_bag_img, (bag_x, bag_y))

        # Texte centré au milieu du sac
        coin_text = font_money.render(str(coins), True, (255, 255, 255))
        coin_shadow = font_money.render(str(coins), True, (0, 0, 0))

        text_x = bag_x + (money_bag_width - coin_text.get_width()) // 1.7
        text_y = bag_y + (money_bag_height - coin_text.get_height()) // 2

        # ombre
        fenetre.blit(coin_shadow, (text_x + 2, text_y + 2))
        fenetre.blit(coin_text, (text_x, text_y))

            # --- HUD barre de vie ---
        # --- HUD barre de vie adaptable ---
        window_w, window_h = fenetre.get_size()

        # Échelle relative à la taille de l'écran
        # (exemple : la barre fait 20% de la largeur de l'écran)
        target_width = int(window_w * 0.3)
        scale_factor = target_width / base_w
        target_height = int(base_h * scale_factor)

        # Redimension dynamique
        health_bar_img = pygame.transform.smoothscale(health_bar_base, (target_width, target_height))

        # Position en bas à gauche (toujours avec marge)
        bar_x = 20
        bar_y = window_h - target_height - 20

        # Affichag
        fenetre.blit(health_bar_img, (bar_x, bar_y))
        # --- ICONES INVENTAIRE + QUETE (responsive, petites tailles demandées) ---
        window_w, window_h = fenetre.get_size()

        # facteur de mise à l'échelle relatif à la résolution de base 1080x720
        scale_x = window_w / UI_BASE_W
        scale_y = window_h / UI_BASE_H
        ui_scale = (scale_x + scale_y) / 2.0  # moyenne pour garder proportions

        # calcule tailles cibles à la volée
        inv_target_w = max(1, int(icon_inv_orig_w * INV_BASE_SCALE * ui_scale))
        inv_target_h = max(1, int(icon_inv_orig_h * INV_BASE_SCALE * ui_scale))

        quest_target_w = max(1, int(icon_quest_orig_w * QUEST_BASE_SCALE * ui_scale))
        quest_target_h = max(1, int(icon_quest_orig_h * QUEST_BASE_SCALE * ui_scale))

        # redimensionne les surfaces (smoothscale pour meilleure qualité)
        icon_inv_img = pygame.transform.smoothscale(icon_inv_base, (inv_target_w, inv_target_h))
        icon_quest_img = pygame.transform.smoothscale(icon_quest_base, (quest_target_w, quest_target_h))

        # marges et positionnement (remonté depuis le bas)
        icon_margin_right = int(20 * ui_scale)
        icon_margin_bottom = int(30 * ui_scale)   # ajuste pour remonter/descendre les icones
        icon_gap = int(12 * ui_scale)

        # positions : parchemin à droite, sac à gauche (côte-à-côte)
        quest_x = window_w - quest_target_w - icon_margin_right
        quest_y = window_h - quest_target_h - icon_margin_bottom

        inv_x = quest_x - inv_target_w - icon_gap
        inv_y = window_h - inv_target_h - icon_margin_bottom

        # dessine les icônes
        fenetre.blit(icon_inv_img, (inv_x, inv_y))
        fenetre.blit(icon_quest_img, (quest_x, quest_y))

        # police pour lettres sous icones : dépend de la taille actuelle de l'icône
        # taille de police environ 30% de la hauteur de l'icone (clamp)
        letter_size = max(10, int(inv_target_h * 0.30))
        try:
            letter_font = pygame.font.Font(font_path, letter_size)
        except Exception:
            letter_font = pygame.font.SysFont(None, letter_size)

        # dessiner lettres centrées sous les icônes (I pour inventory, L pour quest) avec ombre
        letter_I = letter_font.render("I", True, (255, 255, 255))
        letter_I_shadow = letter_font.render("I", True, (0, 0, 0))
        li_x = inv_x + (inv_target_w - letter_I.get_width()) // 2
        li_y = inv_y + inv_target_h + max(2, int(4 * ui_scale))
        fenetre.blit(letter_I_shadow, (li_x + 1, li_y + 1))
        fenetre.blit(letter_I, (li_x, li_y))

        letter_L = letter_font.render("L", True, (255, 255, 255))
        letter_L_shadow = letter_font.render("L", True, (0, 0, 0))
        ll_x = quest_x + (quest_target_w - letter_L.get_width()) // 2
        ll_y = quest_y + quest_target_h + max(2, int(4 * ui_scale))
        fenetre.blit(letter_L_shadow, (ll_x + 1, ll_y + 1))
        fenetre.blit(letter_L, (ll_x, ll_y))

        # surbrillance si ouvert
        if show_inventory:
            pygame.draw.rect(fenetre, (255, 255, 255), (inv_x - 4, inv_y - 4, inv_target_w + 8, inv_target_h + 8), 2)
        if show_quest_panel:
            pygame.draw.rect(fenetre, (255, 255, 255), (quest_x - 4, quest_y - 4, quest_target_w + 8, quest_target_h + 8), 2)

        # stocke/refait les hitboxes utilisés pour la détection du clic (globaux ou variables accessibles)
        current_icon_hitboxes = {
            "inv": pygame.Rect(inv_x, inv_y, inv_target_w, inv_target_h),
            "quest": pygame.Rect(quest_x, quest_y, quest_target_w, quest_target_h)
        }



    if dialogue.actual_dialogue:
        # --- Fond noir semi-transparent ---
        dialogue_box_height = 140
        dialogue_box = pygame.Surface((fenetre.get_width(), dialogue_box_height))
        dialogue_box.set_alpha(180)
        dialogue_box.fill((0, 0, 0))
        fenetre.blit(dialogue_box, (0, fenetre.get_height() - dialogue_box_height))

        # --- Texte ---
        texte, speaker = dialogue.actual_dialogue
        full_text = f"{speaker}: {texte}"

        # --- Détection du mode plein écran ---
        flags = pygame.display.get_surface().get_flags()
        is_fullscreen = bool(flags & pygame.FULLSCREEN)

        # --- Taille de police selon le mode ---
        font_size = 30 if is_fullscreen else 25
        dialogue_font = pygame.font.Font(font_path, font_size)

        # --- Décalage du texte (plus vers la droite) ---
        x_pos = int(fenetre.get_width() * 0.20)
        y_pos = fenetre.get_height() - dialogue_box_height * 0.60

        # --- Ombre du texte ---
        text_shadow = dialogue_font.render(full_text, True, (0, 0, 0))
        text_surf = dialogue_font.render(full_text, True, (255, 255, 255))

        # --- Affichage du texte avec ombre ---
        fenetre.blit(text_shadow, (x_pos + 3, y_pos + 3))
        fenetre.blit(text_surf, (x_pos, y_pos))
        # affichage tetes gif

        gif_left.update()
        gif_right.update()
        gif_left.draw(fenetre)
        gif_right.draw(fenetre)
        
    if not dialogue.actual_dialogue and previous_music:
        play_music(previous_music)
        previous_music = None
        dialogue_music_played = False

    for zone in collision_zones:
        if player.feet.colliderect(zone):
            player.rect.topleft = player.old_position.topleft
            player.x, player.y = player.old_position.topleft

    for k, poisson in list(enumerate(liste_sprite_fish)):
        fish_obj = poisson[1]
        if player.rect.colliderect(fish_obj.rect) and quest.quests != {}:
            

            # Construire l'Item correspondant au poisson (comme tu le fais lors de la pêche)
            # On récupère la taille depuis fish_sizes si disponible, sinon (1,1)
            fish_size = fish_sizes.get(getattr(fish_obj, "name", ""), (1, 1))
            fish_rarity = getattr(fish_obj, "rarity", None)

            Fisher = Item(
                fish_obj.name,
                1,
                size=fish_size,
                rarity=fish_obj.rarity,
                stackable=getattr(fish_obj, "stackable", False)
            )

            # Tentative d'ajout dans l'inventaire principal (index 0) — adapte si nécessaire
            added = False

            added = inventory_list[0].add_item(Fisher)

            if added:
                # Suppression effective du poisson au sol
                quest.verif_objet(fish_obj.name)
                liste_sprite = supprimer_sprite(fish_obj.id, liste_sprite)
                liste_sprite_fish = supprimer_sprite(fish_obj.id, liste_sprite_fish)
                
            else:
                # Inventaire plein (ou placement partiel) -> laisser le sprite sur le sol
                #print("Inventaire plein — le poisson reste sur le sol.")
                # si add_item a consommé une partie (stackable partiel), on a mis Fisher.amount leftover
                # on peut mettre à jour le fish_obj si utile (ex: fish_obj.amount = Fisher.amount) ; à toi de voir
                pass
    

    if quest.quests == {} and not menu:
        liste_sprite_quete = supprimer_sprite("Image_Quete", liste_sprite_quete)

    elif not menu:
        temp = quest.get_required_items()
        lignes = [f"{quest.get_name()}"]
        for item in temp:
            lignes.append(f"{item[0]}: {item[1]}/{item[2]}")

        liste_sprite_quete = supprimer_sprite("Image_Quete", liste_sprite_quete)

        for i in lignes:
            text_surface = quest_font.render(i, True, (255, 255, 255))
            liste_sprite_quete.append(("Image_Quete", text_surface))


    # --- affichage du panneau de quêtes (gauche, centré verticalement, sans fond, avec titre) ---
    # --- affichage du panneau de quêtes (gauche, centré verticalement, sans fond, avec ombre noire sur le texte) ---
    if not menu and show_quest_panel and liste_sprite_quete:
        window_w, window_h = fenetre.get_size()

        # paramètres d'affichage
        line_height = 46      # espace vertical entre chaque ligne
        padding = 12
        start_x = 40          # marge gauche

        # calcul du placement vertical centré
        n_lines = len(liste_sprite_quete)
        total_h = n_lines * line_height + padding * 2
        start_y = max(20, window_h // 2 - total_h // 2)

        # affichage des quêtes (avec ombre noire)
        for i, sprite in enumerate(liste_sprite_quete):
            text_surf = sprite[1]

            text_x = start_x + padding
            text_y = start_y + padding + i * line_height

            # --- ombre noire ---
            shadow_surf = text_surf.copy()
            shadow_surf.fill((0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            fenetre.blit(shadow_surf, (text_x + 2, text_y + 2))
            fenetre.blit(text_surf, (text_x, text_y))




    pygame.display.flip()

# cleanup
if video_cap:
    video_cap.release()
pygame.quit()
sys.exit()

