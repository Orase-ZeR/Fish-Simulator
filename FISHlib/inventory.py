# program to create item inventory
from operator import length_hint
from signal import default_int_handler
import pygame
import os
from pygame.locals import *
import random
import re

SCREENWIDTH = 1430
SCREENHEIGHT = 800
FPS = 60
pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
new_path = os.path.dirname(BASE_DIR)

win = pygame.display.set_mode(
    (SCREENWIDTH, SCREENHEIGHT))  # sets size of the window
pygame.display.set_caption("TEST")  # title of project
clock = pygame.time.Clock()

FRAMES_DIR = "assets/Player/" 

def load_image(image_name):
    """
    Loads an image from a given file path.

    Args:
        image_name (str): the path to the image file

    Returns:
        pygame.Surface: the loaded image
    """
    return pygame.image.load(image_name).convert_alpha()

# frames par rareté (assets à créer : frame_common.png, frame_rare.png, ...)
RARITY_MAP = {
    "Commun": "common",
    "PeuCommun": "uncommon",
    "Rare": "rare",
    "Epic": "epic",
    "Legendaire": "legendary",
    # ajoute d'autres si nécessaire
}

FRAMES = {}
GENERIC_FRAME = None


def load_frames_from_folder(folder):
    global GENERIC_FRAME
    if not os.path.isdir(folder):
        print("Frames folder not found:", folder)
        return

    files = os.listdir(folder)

    # Exemple attendu : SpriteEmplacementInventaireRare2x2.png
    pattern = re.compile(
        r"SpriteEmplacementInventaire(Commun|PeuCommun|Rare|Epic|Legendaire)([0-9])x([0-9])\.png$",
        re.IGNORECASE
    )


    # Fallback : SpriteEmplacementInventaireRare.png ou SpriteEmplacementInventaire.png (→ 1x1)
    pattern_fallback = re.compile(
        r".*SpriteEmplacementInventaire(Commun|PeuCommun|Rare|Epic|Legendaire)?\.(png|jpg|bmp)$",
        re.IGNORECASE
    )

    for f in files:
        path = os.path.join(folder, f)

        # Match principal (avec taille explicite)
        m = pattern.match(f)
        if m:
            raw_rarity = m.group(1)
            w = int(m.group(2))
            h = int(m.group(3))
            rarity_key = RARITY_MAP.get(raw_rarity, raw_rarity.lower())

            try:
                surf = load_image(path)
                FRAMES[(rarity_key, w, h)] = surf
            except Exception as e:
                print("Failed to load frame", path, e)
            continue

        # Fallback : rareté sans taille (1x1)
        m2 = pattern_fallback.match(f)
        if m2:
            raw_rarity = m2.group(1)
            if raw_rarity:
                rarity_key = RARITY_MAP.get(raw_rarity, raw_rarity.lower())
                w, h = 1, 1
                try:
                    surf = load_image(path)
                    FRAMES[(rarity_key, w, h)] = surf
                except Exception as e:
                    print("Failed to load fallback frame", path, e)
            else:
                # Cas vraiment générique, sans rareté
                try:
                    GENERIC_FRAME = load_image(path)
                except Exception as e:
                    print("Failed to load generic frame", path, e)
            continue


# appel
load_frames_from_folder(FRAMES_DIR)
# fallback
if GENERIC_FRAME is None:
    GENERIC_FRAME = pygame.Surface((32, 32), pygame.SRCALPHA)
    GENERIC_FRAME.fill((255, 255, 255, 0))

def get_frame_image(rarity, w, h):
    # Traduit la rareté FR → EN si nécessaire
    if isinstance(rarity, str):
        r = RARITY_MAP.get(rarity, rarity).lower()
    else:
        r = rarity

    key = (r, w, h)
    if key in FRAMES:
        return FRAMES[key]

    # fallback sur variantes de taille
    for size_key in [(r, 1, 1), (r, w, 1), (r, 1, h)]:
        if size_key in FRAMES:
            return FRAMES[size_key]

    return GENERIC_FRAME



CELL = load_image("assets/gui/tile.jpg")
CELL_SELECTED = load_image("assets/gui/tile_selected.jpg")
BIN_CELL = load_image("assets/gui/tile_bin.jpg")
BIN_CELL_SELECTED = load_image("assets/gui/tile_bin_selected.jpg")
ITEM_TEXTURES = {
    "grass": load_image("assets/items/grass.png"),
    "string": pygame.transform.scale(pygame.image.load(new_path + "\\assets/items/string.png").convert_alpha(), (16, 16)),
    "Poisson_Blob": load_image("assets/fish/SpritePoissonBlob.png"),
    "Poisson_Bar": load_image("assets/fish/SpritePoissonBar.png"),
    "Poisson_Truite": load_image("assets/fish/SpritePoissonTruite.png"),
    "Poisson_Crevette": load_image("assets/fish/SpritePoissonCrevette.png"),
    "Poisson_Pieuvre": load_image("assets/fish/SpritePoissonPieuvre.png"),
    "Poisson_Espadon": load_image("assets/fish/SpritePoissonEspadon.png"),
    "Poisson_Rouge": load_image("assets/fish/SpritePoissonRouge.png"),
    "Poisson_Diable_Noir": load_image("assets/fish/SpritePoissonDiableNoir.png"),
    "Poisson_Monstre_Marin": load_image("assets/fish/SpritePoissonMonstreMarin.png"),
    "silver_arrow": load_image("assets/items/silver_arrow.png"),
    "amethyst_clump": load_image("assets/items/amethyst_clump.png"),
    "iron_bar": load_image("assets/items/iron_bar.png"),
    "silver_bar": load_image("assets/items/silver_bar.png"),
    "gold_bar": load_image("assets/items/gold_bar.png"),
    "stick": pygame.transform.scale(pygame.image.load(new_path + "\\assets/items/stick.png").convert_alpha(), (16, 16)),
    "diamond_clump": load_image("assets/items/diamond_clump.png"),
    "bone": load_image("assets/items/bone.png"),
    "flint": load_image("assets/items/flint.png"),
    "arrow": load_image("assets/items/arrow.png"),
    "book": load_image("assets/items/book.png"),
    "gold_sword": load_image("assets/items/gold_sword.png"),
    "iron_sword": load_image("assets/items/iron_sword.png"),
    "bow": load_image("assets/items/bow.png"),
    "gold_bow": load_image("assets/items/gold_bow.png"),
    "scythe": load_image("assets/items/scythe.png"),
    "poison": load_image("assets/items/poison.png"),
    "poison_arrow": load_image("assets/items/poison_arrow.png"),
    "health_potion": load_image("assets/items/health_potion.png"),
    "bronze_bar": load_image("assets/items/bronze_bar.png"),
    "bronze_sword": load_image("assets/items/bronze_sword.png"),
    "glass": load_image("assets/items/glass.png"),
    "glass_bottle": load_image("assets/items/glass_bottle.png"),
    "paper": load_image("assets/items/paper.png"),
    "rose": load_image("assets/items/rose.png"),
    "daisy": load_image("assets/items/daisy.png"),
    "amethyst_arrow": load_image("assets/items/amethyst_arrow.png"),
    "feather": load_image("assets/items/feather.png"),
    "bone_arrow": load_image("assets/items/bone_arrow.png"),
    # si tu veux big_fish -> ajoute l'image dans assets/items/big_fish.png
}
ITEMS = {
    "grass": {"name": "Grass", "description": "It's some grass."},
    "string": {"name": "String", "description": ""},
    "silver_arrow": {"name": "Silver Arrow", "description": "A stronger arrow made from silver. Suitable for hunting the supernatural."},
    "Poisson_Bar": {"name": "Poisson Bar", "description": "Un gros poisson."},
    "Poisson_Blob": {"name": "Poisson Blob", "description": "Un poisson étrange et visqueux mais fascinant."},
    "Poisson_Truite": {"name": "Poisson Truite", "description": "Un poisson d’eau douce très apprécié des pêcheurs."},
    "Poisson_Crevette": {"name": "Poisson Crevette", "description": "Une petite crevette parfaite pour l’apéro."},
    "Poisson_Pieuvre": {"name": "Poisson Pieuvre", "description": "Une pieuvre malicieuse ses tentacules bougent encore !"},
    "Poisson_Espadon": {"name": "Poisson Espadon", "description": "Un puissant poisson rapide et majestueux."},
    "Poisson_Rouge": {"name": "Poisson Rouge", "description": "Un petit poisson souvent gardé en bocal."},
    "Poisson_Diable_Noir": {"name": "Poisson Diable Noir", "description": "Un poisson abyssal terrifiant mais fascinant."},                    
    "Poisson_Monstre_Marin": {"name": "Monstre Marin", "description": "Une créature colossale rare et redoutée."}
    # ... (garde ton dictionnaire d'origine)
}

WEAPONS = {
    "gold_sword": {"name": "Gold Sword", "description": ""},
    "iron_sword": {"name": "Iron Sword", "description": ""},
    "bow": {"name": "Bone Arrow", "description": ""},
    "gold_bow": {"name": "Gold Bow", "description": ""},
    "scythe": {"name": "Scythe", "description": "Used for farming and combat!"},
    "bronze_sword": {"name": "Bronze Sword", "description": ""},
}
FONT = {
    "16": pygame.font.Font("assets/DTM-Sans.otf", 16),
    "24": pygame.font.Font("assets/DTM-Sans.otf", 24)
}
DUST = [load_image(f"assets/gui/dust_{x}.png") for x in range(6)]

CURSOR_ICONS = {
    "cursor": load_image("assets/gui/cursor.png"),
    "grab": load_image("assets/gui/cursor_grab.png"),
    "magnet": load_image("assets/gui/cursor_magnet.png"),
    "move": load_image("assets/gui/cursor_move.png"),
    "text": load_image("assets/gui/cursor_text.png"),
}
INVENTORY_SORTING_BUTTONS = {
    "name": load_image("assets/gui/sort_name.jpg"),
    "amount": load_image("assets/gui/sort_amount.jpg"),
    "type": load_image("assets/gui/sort_type.jpg"),
    "select": load_image("assets/gui/sort_select.png"),
}

# Search Bar assets
SEARCH_BAR = {
    "left": load_image("assets/gui/search_left.png"),
    "middle": load_image("assets/gui/search_middle.png"),
    "right": load_image("assets/gui/search_right.png"),
}
SEARCH_BAR_SELECTED = {
    "left": load_image("assets/gui/search_sel_left.png"),
    "middle": load_image("assets/gui/search_sel_middle.png"),
    "right": load_image("assets/gui/search_sel_right.png"),
}

class Dust():
    def __init__(self) -> None:
        self.life = 20
    def update(self, x, y, scale) -> None:
        self.life -= 1
        if self.life > 0:
            image = pygame.transform.scale(
                DUST[5 - (self.life // 4)], (16 * scale, 16 * scale))
            win.blit(image, (x + 2 * scale, y + 2 * scale))


class Cursor_Context_Box():
    def __init__(self, name, description, flip) -> None:
        self.name = name
        self.description = description
        self.flip = flip
    def update(self, x, y, scale) -> None:
        footer = False
        height = 0.55 * 20 * scale
        width = 4 * 20 * scale
        offset = {"x": 0, "y": 0}
        if x > SCREENWIDTH - width:
            offset["x"] = -width
        if y > SCREENHEIGHT - height:
            offset["y"] = -height
        desc = [""]
        line = 0
        words = self.description.split(' ')
        if len(words) > 1:
            height += 0.26 * 20 * scale
            footer = True
        for i, word in enumerate(words):
            if not len(word) + len(desc[line]) > 30:
                desc[line] += (" " if i != 0 else "") + word
            else:
                desc.append("")
                line += 1
                desc[line] += word
                height += 0.26 * 20 * scale
        if footer:
            height += 0.2 * 20 * scale
        pygame.draw.rect(
            win, (255, 255, 255), (x+12 + offset["x"], y+12 + offset["y"], width, height))
        pygame.draw.rect(
            win, (31, 31, 31), (x+15 + offset["x"], y+15 + offset["y"], width - 6, height - 6))
        inventory_title = FONT["24"].render(
            self.name, 1, (255, 255, 255))
        win.blit(inventory_title,
                 (x + 7 * 3 + offset["x"], y + 4 * 3 + offset["y"]))
        line = 0
        for d in desc:
            description = FONT["16"].render(d, 1, (180, 180, 180))
            win.blit(description, (x + 7 * 3 + offset["x"],
                     y + 1.5 * 20 + 4 * 3 + line * 5 + offset["y"]))
            line += 3


class Cursor():
    def __init__(self) -> None:
        self.item = None
        self.position = pygame.mouse.get_pos()
        self.box = pygame.Rect(*self.position, 1, 1)
        self.cooldown = 0
        self.pressed = None
        self.magnet = False
        self.move = False
        self.text = False
        self.context = None

    def update(self, keys, search_bar_pos, search_bar_scale) -> None:
        self.position = pygame.mouse.get_pos()
        self.box = pygame.Rect(*self.position, 1, 1)
        self.pressed = pygame.mouse.get_pressed()

        if self.item is not None:
            # draw held item at mouse (preview)
            if hasattr(self.item, "size"):
                w, h = self.item.size
                self.item.draw(self.position[0], self.position[1], 3, w, h)
            else:
                self.item.draw(*self.position, 3)

        if self.cooldown > 0:
            self.cooldown -= 1

        search_box = pygame.Rect(search_bar_pos[0], search_bar_pos[1] + 16 * search_bar_scale, 21 * 20 * search_bar_scale, 20 * search_bar_scale)
        self.text = self.box.colliderect(search_box)
        self.magnet = keys[K_LSHIFT] and self.item is not None
        self.move = keys[K_LSHIFT] and not self.magnet

        if self.context is not None:
            self.context.update(*self.position, 3)
            self.context = None

        if self.magnet:
            image = pygame.transform.scale(CURSOR_ICONS["magnet"], (9 * 3, 10 * 3))
        elif self.move:
            image = pygame.transform.scale(CURSOR_ICONS["move"], (9 * 3, 10 * 3))
        elif self.item is not None:
            image = pygame.transform.scale(CURSOR_ICONS["grab"], (9 * 3, 10 * 3))
        elif self.text:
            image = pygame.transform.scale(CURSOR_ICONS["text"], (9 * 3, 10 * 3))
        else:
            image = pygame.transform.scale(CURSOR_ICONS["cursor"], (9 * 3, 10 * 3))

        # draw cursor icon
        win.blit(image, (self.position[0], self.position[1]))

        # --- afficher "R" au-dessus du curseur dès qu'on tient un item (peu importe stackable) ---
        if self.item is not None:
            text_img = FONT["16"].render("R", True, (255, 255, 255))
            tw, th = text_img.get_size()
            cursor_w = 9 * 3  # largeur de l'icône de curseur telle qu'on l'a scalée plus haut
            # centrer le "R" horizontalement au-dessus du curseur et le placer légèrement au-dessus
            tx = self.position[0] + cursor_w // 2 - tw // 2
            ty = self.position[1] - th - 4
            win.blit(text_img, (tx, ty))

    def set_cooldown(self) -> None:
        self.cooldown = 10



class Item():
    def __init__(self, name, amount, size=(1,1), rarity="common", stackable=None) -> None:
        self.name = name
        self.amount = amount
        self.size = size  # (w,h) in cells
        self.rarity = rarity
        if stackable is None:
            self.stackable = True if size == (1,1) else False
        else:
            self.stackable = bool(stackable)
        self.type = "item"
        self.rotated = False   # <-- flag rotation

    def rotate(self) -> None:
        # rotate only if multi-cell (ou si w!=h) — inutile pour stackable 1x1
        if self.stackable:
            return
        w, h = self.size
        self.size = (h, w)
        self.rotated = not self.rotated

    def draw(self, x, y, scale, width_cells=1, height_cells=1) -> None:
        tex = ITEM_TEXTURES.get(self.name)
        if tex is None:
            return
        # si l'item a été tourné, on tourne la texture (90°)
        tex_to_draw = tex
        # Ne pas tourner les textures carrées, mais ça ne fait pas de mal non plus
        if self.rotated:
            tex_to_draw = pygame.transform.rotate(tex, 90)

        cell_box = 20 * scale
        w_px = int(cell_box * width_cells)
        h_px = int(cell_box * height_cells)
        img_w = max(1, w_px - 4 * scale)
        img_h = max(1, h_px - 4 * scale)

        image = pygame.transform.scale(tex_to_draw, (img_w, img_h))
        win.blit(image, (x + 2 * scale, y + 2 * scale))

        if self.amount > 1:
            item_count = FONT["24"].render(str(self.amount), 1, (255, 255, 255))
            win.blit(item_count, (x + img_w - 12 * scale, y + img_h - 14 * scale))

    def copy(self):
        new = Item(self.name, self.amount, size=self.size, rarity=self.rarity, stackable=self.stackable)
        new.rotated = self.rotated
        return new

    def get_name(self):
        return ITEMS.get(self.name, {}).get("name", self.name)

    def get_description(self):
        return ITEMS.get(self.name, {}).get("description", "")


class Weapon(Item):
    def __init__(self, name, amount) -> None:
        super().__init__(name, amount)
        self.stackable = False
        self.type = "weapon"
    def copy(self):
        return Weapon(self.name, self.amount)
    def get_name(self):
        return WEAPONS[self.name]["name"]
    def get_description(self):
        return WEAPONS[self.name]["description"]

class Occupier():
    def __init__(self, item, anchor_r, anchor_c, w, h):
        self.item = item
        self.anchor = (anchor_r, anchor_c)
        self.w = w
        self.h = h

class Cell():
    def __init__(self, item=None) -> None:
        self.item = item
        self.particles = []
        self.occupier = None

    def draw(self, scale, selected):
        match selected:
            case 1:
                image = pygame.transform.scale(CELL_SELECTED, (20 * scale, 20 * scale))
            case 0:
                image = pygame.transform.scale(CELL, (20 * scale, 20 * scale))
        return image

    def update(self, x, y, scale, stack_limit, inventory_id, inventory_list, cursor, row_idx, col_idx, inventory_ref) -> None:
        position = (x, y)
        cell_box = pygame.Rect(*position, 20 * scale, 20 * scale)

        # --- DRAW BACKGROUND (éviter d'écraser la frame d'un occupier non-ancre) ---
        if self.occupier is not None:
            occ = self.occupier
            anchor_r, anchor_c = occ.anchor
            if (row_idx, col_idx) == (anchor_r, anchor_c):
                if cursor.box.colliderect(cell_box):
                    image = self.draw(scale, 1)
                else:
                    image = self.draw(scale, 0)
                win.blit(image, position)
            else:
                # satellite cell : ne pas blitter la tile complète pour ne pas écraser la frame
                pass
        else:
            # cellule normale : dessiner fond sélectionné / non
            if cursor.box.colliderect(cell_box):
                image = self.draw(scale, 1)
            else:
                image = self.draw(scale, 0)
            win.blit(image, position)

        # particules
        if len(self.particles) > 0:
            for p in list(self.particles):
                p.update(x, y, scale)
                if p.life < 1:
                    try:
                        self.particles.remove(p)
                    except ValueError:
                        pass

        # --- si cette cellule fait partie d'un occupier multi-slot ---
        if self.occupier is not None:
            occ = self.occupier
            anchor_r, anchor_c = occ.anchor

            if (row_idx, col_idx) == (anchor_r, anchor_c):
                # draw frame first
                frame_img = get_frame_image(occ.item.rarity, occ.w, occ.h) if occ.item is not None else GENERIC_FRAME
                target_w = int(20 * scale * occ.w)
                target_h = int(20 * scale * occ.h)
                try:
                    frame_scaled = pygame.transform.scale(frame_img, (target_w, target_h))
                except Exception:
                    frame_scaled = pygame.transform.scale(GENERIC_FRAME, (target_w, target_h))
                win.blit(frame_scaled, (x, y))

                # then draw the item on top of the frame
                if occ.item is not None:
                    occ.item.draw(x, y, scale, occ.w, occ.h)

                else:
                    # satellite cell : ne rien dessiner (l'item et son cadre sont déjà gérés par l’ancre)
                    pass

            # interactions communes (clic sur n'importe quelle cellule de l'occupier)
# interactions communes (clic sur n'importe quelle cellule de l'occupier)
            if cursor.box.colliderect(cell_box):
                # show context tooltip (hover) for the whole occupier
                if occ.item is not None:
                    cursor.context = Cursor_Context_Box(occ.item.get_name(), occ.item.get_description(), 0)

                if cursor.cooldown != 0:
                    return
                if cursor.pressed[0] and cursor.item is None:
                    item_taken = inventory_ref.remove_item_at(anchor_r, anchor_c)
                    if item_taken is not None:
                        cursor.item = item_taken
                        self.particles.append(Dust())
                        cursor.set_cooldown()

            return

        # --- CELLULE SIMPLE (pas occupier) : logique originale pour item 1x1 ---
        # --- CELLULE SIMPLE (pas occupier) : logique originale pour item 1x1 ---
        if self.item is not None:
            # taille logique
            if hasattr(self.item, "size"):
                w, h = self.item.size
            else:
                w, h = (1, 1)

            # draw frame first (pour que le centre transparent du cadre ne masque pas l'icône)
            rarity = getattr(self.item, "rarity", "common")
            frame_img = get_frame_image(rarity, w, h)
            target_w = int(20 * scale * w)
            target_h = int(20 * scale * h)
            try:
                frame_scaled = pygame.transform.scale(frame_img, (target_w, target_h))
            except Exception:
                frame_scaled = pygame.transform.scale(GENERIC_FRAME, (target_w, target_h))
            win.blit(frame_scaled, (x, y))

            # then draw the item icon ON TOP of the frame
            if (w, h) == (1, 1):
                self.item.draw(*position, scale)
            else:
                self.item.draw(*position, scale, w, h)

            # interactions: si la souris n'est pas au-dessus, on sort
            if not cursor.box.colliderect(cell_box):
                return
            if cursor.cooldown != 0:
                return

            # --- si on tient un item et qu'on essaie de le déposer sur une cellule occupée ---
            if cursor.item is not None:
                # cas: on veut déposer un item multi-cell sur une cellule qui contient un 1x1
                if hasattr(cursor.item, "size") and cursor.item.size != (1, 1):
                    # tentative atomique de swap : on retire temporairement l'item existant,
                    # on essaye place_item_at; si ça réussit -> swap (le 1x1 passe dans la main),
                    # sinon on restaure l'ancienne cellule.
                    temp = self.item
                    self.item = None  # libère la cellule temporairement pour la vérif
                    placed = inventory_ref.place_item_at(cursor.item, row_idx, col_idx)
                    if placed:
                        # placement réussi : on récupère l'ancien item dans la main (swap)
                        cursor.item = temp
                        self.particles.append(Dust())
                        cursor.set_cooldown()
                        return
                    else:
                        # échec : restauration propre
                        self.item = temp
                        # pas de cooldown, pas de particule
                else:
                    # cas: on tient un 1x1 (ou stackable) et la cellule est occupée par un 1x1
                    # stacking possible ?
                    if hasattr(cursor.item, "size") and cursor.item.size == (1, 1) and self.item.stackable and cursor.item.name == self.item.name:
                        # stacking si possible
                        if self.item.amount + cursor.item.amount <= stack_limit:
                            self.item.amount += cursor.item.amount
                            cursor.item = None
                            self.particles.append(Dust())
                            cursor.set_cooldown()
                            return
                        else:
                            amount = stack_limit - self.item.amount
                            if amount > 0:
                                self.item.amount += amount
                                cursor.item.amount -= amount
                                self.particles.append(Dust())
                                cursor.set_cooldown()
                                return
                    # sinon swap simple entre main et cellule (1x1 <-> 1x1)
                    temp = cursor.item.copy()
                    cursor.item = self.item
                    self.item = temp
                    self.particles.append(Dust())
                    cursor.set_cooldown()
                    return

            # --- si on ne tient rien : interactions classiques (prendre / split / move) ---
            if cursor.item is None:
                cursor.context = Cursor_Context_Box(self.item.get_name(), self.item.get_description(), 0 if True else 1)
                if cursor.pressed[0] and cursor.move:
                    index = inventory_id
                    for i in range(len(inventory_list)):
                        index = index + 1 if index < len(inventory_list) - 1 else 0
                        if index == inventory_id:
                            break
                        if inventory_list[index].capacity != inventory_list[index].item_count:
                            break
                    temp = self.item.copy()
                    self.item = None
                    inventory_list[index].add_item(temp)
                    self.particles.append(Dust())
                    cursor.set_cooldown()
                elif cursor.pressed[0]:
                    cursor.item = self.item
                    self.item = None
                    self.particles.append(Dust())
                    cursor.set_cooldown()
                elif cursor.pressed[2] and self.item.amount > 1:
                    half = self.item.amount // 2
                    cursor.item = self.item.copy()
                    cursor.item.amount = half
                    self.item.amount -= half
                    self.particles.append(Dust())
                    cursor.set_cooldown()
            else:
                # on tient un item (déjà géré plus haut), mais ici on gère stacking / swap si nécessaire
                if cursor.cooldown != 0:
                    return
                if cursor.pressed[0] and cursor.item.name == self.item.name and self.item.amount + cursor.item.amount <= stack_limit and self.item.stackable:
                    self.item.amount += cursor.item.amount
                    cursor.item = None
                    self.particles.append(Dust())
                    cursor.set_cooldown()
                elif cursor.pressed[0] and cursor.item.name == self.item.name and self.item.stackable:
                    amount = stack_limit - self.item.amount
                    self.item.amount += amount
                    cursor.item.amount -= amount
                    self.particles.append(Dust())
                    cursor.set_cooldown()
                elif cursor.pressed[0]:
                    temp = cursor.item.copy()
                    cursor.item = self.item
                    self.item = temp
                    self.particles.append(Dust())
                    cursor.set_cooldown()

        # placement direct d'un item tenu dans une cellule vide
        elif cursor.item is not None and cursor.box.colliderect(cell_box) and cursor.cooldown == 0:
            if cursor.pressed[0]:
                if hasattr(cursor.item, "size") and cursor.item.size != (1,1):
                    r = row_idx
                    c = col_idx
                    placed = inventory_ref.place_item_at(cursor.item, r, c)
                    if placed:
                        cursor.item = None
                        self.particles.append(Dust())
                        cursor.set_cooldown()
                else:
                    # placer un 1x1 dans une case vide
                    self.item = cursor.item
                    cursor.item = None
                    self.particles.append(Dust())
                    cursor.set_cooldown()
            elif cursor.pressed[2] and cursor.item.stackable:
                if cursor.item.amount > 1:
                    half = cursor.item.amount // 2
                    self.item = cursor.item.copy()
                    self.item.amount = half
                    cursor.item.amount -= half
                else:
                    self.item = cursor.item
                    cursor.item = None
                self.particles.append(Dust())
                cursor.set_cooldown()


        # placement direct d'un item tenu (drop)
        elif cursor.item is not None and cursor.box.colliderect(cell_box) and cursor.cooldown == 0:
            if cursor.pressed[0]:
                if hasattr(cursor.item, "size") and cursor.item.size != (1,1):
                    r = row_idx
                    c = col_idx
                    placed = inventory_ref.place_item_at(cursor.item, r, c)
                    if placed:
                        cursor.item = None
                        self.particles.append(Dust())
                        cursor.set_cooldown()
                else:
                    self.item = cursor.item
                    cursor.item = None
                    self.particles.append(Dust())
                    cursor.set_cooldown()
            elif cursor.pressed[2] and cursor.item.stackable:
                if cursor.item.amount > 1:
                    half = cursor.item.amount // 2
                    self.item = cursor.item.copy()
                    self.item.amount = half
                    cursor.item.amount -= half
                else:
                    self.item = cursor.item
                    cursor.item = None
                self.particles.append(Dust())
                cursor.set_cooldown()


class Bin(Cell):
        def __init__(self, item=None) -> None:
            super().__init__(item)
        def draw(self, scale, selected):
            match selected:
                case 1:
                    image = pygame.transform.scale(
                        BIN_CELL_SELECTED, (20 * scale, 20 * scale))
                case 0:
                    image = pygame.transform.scale(
                        BIN_CELL, (20 * scale, 20 * scale))
            return image


class Inventory():
    class Inventory_Sorting_Button():
        def __init__(self, name, inv) -> None:
            self.name = name
            self.image = INVENTORY_SORTING_BUTTONS[name]
            self.parent = inv

        def update(self, x, y, scale, cursor) -> None:
            if not getattr(self.parent, "buttons_visible", False):
                return
            image = pygame.transform.scale(self.image, (10 * scale, 10 * scale))
            win.blit(image, (x, y))
            button_box = pygame.Rect(x, y, 10 * scale, 10 * scale)
            if cursor.box.colliderect(button_box):
                image = pygame.transform.scale(INVENTORY_SORTING_BUTTONS["select"], (10 * scale, 10 * scale))
                win.blit(image, (x, y))
                if cursor.pressed[0]:
                    match self.name:
                        case "name":
                            self.parent.sort_item_name()
                        case "amount":
                            self.parent.sort_item_amount()
                        case "type":
                            self.parent.sort_item_type()

    def __init__(self, name, rows, columns, x, y, scale=3, stack_limit=99, sorting_active=False, bin_active=False, search_active=False) -> None:
        self.name = name
        self.rows = rows
        self.columns = columns
        self.cells = [[Cell() for i in range(columns)] for j in range(rows)]
        self.position = (x, y)
        self.scale = scale
        self.stack_limit = stack_limit
        self.capacity = rows * columns
        self.bin = bin_active
        self.buttons_visible = sorting_active
        self.search_visible = search_active
        if self.capacity >= 6 and self.columns >= 3 and sorting_active:
            self.buttons = [ self.Inventory_Sorting_Button(x, self) for x in list(INVENTORY_SORTING_BUTTONS.keys()) if x != "select" ]
        else:
            self.buttons = []

    def can_place_at(self, start_row, start_col, w, h) -> bool:
        if start_row < 0 or start_col < 0 or start_row + h > self.rows or start_col + w > self.columns:
            return False
        for r in range(start_row, start_row + h):
            for c in range(start_col, start_col + w):
                cell = self.cells[r][c]
                if cell.occupier is not None or cell.item is not None:
                    # debug: print what's blocking
                    # supprime/ commente cette ligne une fois le bug trouvé
                    print(f"can_place_at blocked at {(r,c)} item={cell.item is not None} occupier={cell.occupier is not None}")
                    return False
        return True


    def place_item_at(self, item, start_row, start_col) -> bool:
        w, h = item.size
        if not self.can_place_at(start_row, start_col, w, h):
            return False
        occ = Occupier(item, start_row, start_col, w, h)
        # d'abord vérifier encore (sécurisé), puis écrire l'occ en une passe
        for r in range(start_row, start_row + h):
            for c in range(start_col, start_col + w):
                # ASSURE : on efface item OR occupier qui traînait (ne devrait pas être le cas)
                self.cells[r][c].item = None
                self.cells[r][c].occupier = occ
        return True


    def remove_item_at(self, anchor_row, anchor_col):
        cell = self.cells[anchor_row][anchor_col]
        if cell.occupier is None:
            return None
        occ = cell.occupier
        item_copy = occ.item.copy()
        for r in range(occ.anchor[0], occ.anchor[0] + occ.h):
            for c in range(occ.anchor[1], occ.anchor[1] + occ.w):
                # bien nettoyer TOUTES les cellules
                self.cells[r][c].occupier = None
                self.cells[r][c].item = None
        return item_copy


    def find_space_for(self, item):
        w, h = item.size
        for r in range(self.rows):
            for c in range(self.columns):
                if self.can_place_at(r, c, w, h):
                    return (r, c)
        return None

    def add_item(self, item) -> bool:
        """
        Tente d'ajouter *tout* l'item dans l'inventaire.
        Retourne True si l'item a été entièrement placé,
        False si une partie ou la totalité n'a pas pu être placée.
        Comportement :
        - stackable: tente de remplir les stacks existants puis les cases vides
        - non-stackable 1x1: place dans première case vide
        - non-stackable multi-slot: recherche un emplacement et place
        Si placement partiel (stackable), la quantité restante est laissée dans item.amount.
        """
        # work on a mutable remaining amount for stackable items
        if getattr(item, "stackable", False):
            remaining = getattr(item, "amount", 1)

            # d'abord, essayer de compléter des stacks existants
            for row in self.cells:
                for cell in row:
                    if cell.item is not None and cell.item.name == item.name and getattr(cell.item, "stackable", False) and cell.occupier is None:
                        can_add = min(self.stack_limit - cell.item.amount, remaining)
                        if can_add > 0:
                            cell.item.amount += can_add
                            remaining -= can_add
                            if remaining == 0:
                                return True

            # ensuite, essayer de placer dans des cellules vides
            for row in self.cells:
                for cell in row:
                    if cell.item is None and cell.occupier is None:
                        place_amount = min(self.stack_limit, remaining)
                        # on crée une copie stockée dans la cellule pour représenter la pile
                        new_item = item.copy() if hasattr(item, "copy") else item
                        new_item.amount = place_amount
                        cell.item = new_item
                        remaining -= place_amount
                        if remaining == 0:
                            return True

            # si on arrive ici, on a placé quelque chose (peut-être) mais il reste des unités
            item.amount = remaining
            return False

        # non stackable 1x1
        if hasattr(item, "size") and item.size == (1, 1):
            for row in self.cells:
                for cell in row:
                    if cell.item is None and cell.occupier is None:
                        cell.item = item
                        return True
            return False

        # multi-slot non-stackable
        place = self.find_space_for(item)
        if place is not None:
            r, c = place
            self.place_item_at(item, r, c)
            return True

        return False


    def get_item_list(self) -> list:
        item_list = []
        for r, row in enumerate(self.cells):
            for c, cell in enumerate(row):
                if cell.occupier is not None:
                    occ = cell.occupier
                    # only add anchor once
                    if occ.anchor == (r, c):
                        item_list.append(occ.item.copy())
                elif cell.item is not None:
                    item_list.append(cell.item.copy())
        return item_list

    def get_item_count(self) -> int:
        item_count = 0
        counted_anchors = set()
        for r, row in enumerate(self.cells):
            for c, cell in enumerate(row):
                if cell.occupier is not None:
                    occ = cell.occupier
                    if occ.anchor not in counted_anchors:
                        counted_anchors.add(occ.anchor)
                        item_count += 1
                elif cell.item is not None:
                    item_count += 1
        return item_count

    def clear_inventory(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.item = None
                cell.occupier = None

    def sort_item_name(self) -> None:
        item_list = self.get_item_list()
        item_list.sort(key=lambda x: x.name)
        self.clear_inventory()
        for item in item_list:
            self.add_item(item)

    def sort_item_amount(self) -> None:
        item_list = self.get_item_list()
        item_list.sort(key=lambda x: x.amount)
        self.clear_inventory()
        for item in item_list:
            self.add_item(item)

    def sort_item_type(self) -> None:
        item_list = self.get_item_list()
        item_list.sort(key=lambda x: self.get_type_sort_key(x.type))
        self.clear_inventory()
        for item in item_list:
            self.add_item(item)

    def get_type_sort_key(self, type) -> int:
        match type:
            case "weapon":
                return 1
            case "item":
                return 2

    def update(self, inventory_id, inventory_list, cursor, text) -> None:
        self.item_count = self.get_item_count()
        pygame.draw.rect(
            win, (31, 31, 31), 
            (*self.position,
             self.columns * 20 * self.scale + 4 * self.scale,
             self.rows * 20 * self.scale + 18 * self.scale + (20 * self.scale if self.bin else 0))
        )

        inventory_title = FONT["24"].render(self.name, 1, (255, 255, 255))
        win.blit(inventory_title, (self.position[0] + 4 * self.scale, self.position[1] + 4 * self.scale))

        for i, b in enumerate(self.buttons):
            b.update(
                self.position[0] + 20 * self.columns * self.scale - 9 * self.scale - i * 12 * self.scale,
                self.position[1] + 4 * self.scale,
                self.scale,
                cursor
            )

        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                cell.update(
                    self.position[0] + (j * 20 * self.scale) + 2 * self.scale,
                    self.position[1] + (i * 20 * self.scale) + 16 * self.scale,
                    self.scale, self.stack_limit, inventory_id, inventory_list, cursor,
                    i, j, self
                )

        bin_cell = Bin()
        if self.bin:
            bin_cell.update(
                self.position[0] + ((len(self.cells[0]) - 1) * 20 * self.scale) + 2 * self.scale,
                self.position[1] + (len(self.cells) * 20 * self.scale) + 16 * self.scale,
                self.scale, self.stack_limit, inventory_id, inventory_list, cursor,
                -1, -1, self
            )

        # search shading / highlight
        if text != "":
            for i, row in enumerate(self.cells):
                for j, cell in enumerate(row):
                    if cell.item is not None and text in cell.item.name:
                        pygame.draw.rect(
                            win, (255, 0, 0),
                            (self.position[0] + (j * 20 * self.scale) + 2 * self.scale,
                             self.position[1] + (i * 20 * self.scale) + 16 * self.scale,
                             4 * self.scale, 4 * self.scale)
                        )
                    else:
                        shade = pygame.Surface((16 * self.scale, 16 * self.scale))
                        shade.set_alpha(128)
                        shade.fill((0, 0, 0))
                        win.blit(shade, (
                            self.position[0] + (j * 20 * self.scale) + 2 * self.scale + 2 * self.scale,
                            self.position[1] + (i * 20 * self.scale) + 16 * self.scale + 2 * self.scale
                        ))




class Inventory_Engine():
    def __init__(self, inventory_list) -> None:
        self.inventory_list = inventory_list
    def update(self, cursor, text) -> None:
        for i, inventory in enumerate(self.inventory_list):
            inventory.update(i, self.inventory_list, cursor, text)

        # cooldown global pour empêcher le swap continu
        if cursor.cooldown > 0:
            cursor.cooldown -= 1

# Search bar class *Xini
def debug_print_grid(inv, top_r=0, top_c=0, rows=6, cols=10):
    for r in range(top_r, min(inv.rows, top_r+rows)):
        line = []
        for c in range(top_c, min(inv.columns, top_c+cols)):
            cell = inv.cells[r][c]
            if cell.occupier is not None:
                line.append(f"O({cell.occupier.anchor})")
            elif cell.item is not None:
                line.append(f"I({cell.item.name})")
            else:
                line.append(" . ")
        print(" ".join(line))


class Search_Bar():
    def __init__(self, width, x, y, scale=3) -> None:
        self.width = width
        self.position = (x, y)
        self.scale = scale
        self.clicked = 0
        self.blink = 0
        self.text_pos = 0
        self.text = ""
    def draw(self, selected):
        images = [pygame.Surface] * self.width
        match selected:
            case 1:
                for i in range(self.width):
                    if i == 0:
                        images[i] = pygame.transform.scale(SEARCH_BAR_SELECTED["left"], (20 * self.scale, 20 * self.scale))
                    elif i == self.width - 1:
                        images[i] = pygame.transform.scale(SEARCH_BAR_SELECTED["right"], (20 * self.scale, 20 * self.scale))
                    else:
                        images[i] = pygame.transform.scale(SEARCH_BAR_SELECTED["middle"], (20 * self.scale, 20 * self.scale))
            case 0:
                for i in range(self.width):
                    if i == 0:
                        images[i] = pygame.transform.scale(SEARCH_BAR["left"], (20 * self.scale, 20 * self.scale))
                    elif i == self.width - 1:
                        images[i] = pygame.transform.scale(SEARCH_BAR["right"], (20 * self.scale, 20 * self.scale))
                    else:
                        images[i] = pygame.transform.scale(SEARCH_BAR["middle"], (20 * self.scale, 20 * self.scale))
        return images
    def update(self, cursor) -> None:
        pygame.draw.rect(
            win, (31, 31, 31), (*self.position, self.width * 20 * self.scale + 4 * self.scale, 20 * self.scale + 18 * self.scale))
        search_bar_title = FONT["24"].render(
            "Search:", 1, (255, 255, 255))
        win.blit(search_bar_title, (self.position[0] + 4 * self.scale, self.position[1] + 4 * self.scale))
        search_box = pygame.Rect(
            self.position[0], self.position[1] + 16 * self.scale, self.width * 20 * self.scale, 20 * self.scale)
        if cursor.box.colliderect(search_box):
            images = self.draw(1)
        else:
            images = self.draw(0)
        for i in range(len(images)):
            win.blit(images[i], (self.position[0] + (i * 20 * self.scale) + 2 * self.scale, self.position[1] + 16 * self.scale))
        text = FONT["24"].render(self.text, 1, (255, 255, 255))
        win.blit(text, (self.position[0] + 4 * self.scale + 3 * self.scale, self.position[1] + 16 * self.scale + 4 * self.scale, 4 * self.scale, self.scale))
        if self.blink == 60:
            self.blink = 0
        elif self.blink > 30:
            self.blink += 1
        elif self.clicked == 1:
            pygame.draw.rect(
                win, (255, 255, 255), (self.position[0] + 4 * self.scale + 3 * self.scale + self.text_pos * 4 * self.scale, self.position[1] + 16 * self.scale + 13 * self.scale, 4 * self.scale, self.scale))
            self.blink += 1
        if cursor.pressed is None:
            self.clicked = 0
        elif cursor.box.colliderect(search_box) and cursor.pressed[0]:
            self.clicked = 1
        elif cursor.pressed[0]:
            self.clicked = 0
    def handle_event(self, event) -> None:
        if self.clicked == 1:
            if event.key == pygame.K_BACKSPACE:
                if self.text_pos > 0:
                    self.text_pos -= 1
                    self.text = self.text[:-1]
            else:
                self.text_pos += 1
                self.text += event.unicode


def main():
    inventory_list = [
        Inventory("Large", 6, 10, 50, 100, 3, 99, bin_active=True),
        Inventory("3x3", 3, 3, 700, 100, 3, 99),
        Inventory("Small", 1, 3, 700, 400, 3, 99),
        Inventory("Tall", 6, 3, 930, 100, 3, 99),
        Inventory("Tall2", 6, 2, 1170, 100, 3, 99)
    ]
    inventory_engine = Inventory_Engine(inventory_list)
    search_bar = Search_Bar(21, 50, 600, 3)
    cursor = Cursor()

    # create a 2x2 fish example and add it to the first inventory (ensure ITEM_TEXTURES has "big_fish")
    # si tu n'as pas l'image big_fish: crée-la dans assets/items/big_fish.png
    if "big_fish" in ITEM_TEXTURES:
        big_fish = Item("big_fish", 1, size=(2,1), rarity="rare")
    if "Poisson_Monstre_Marin" in ITEM_TEXTURES:
       Poisson_Monstre_Marin = Item("Poisson_Monstre_Marin", 1, size=(4,4), rarity="legendary")        

    run = True
    while run:
        pygame.mouse.set_visible(False)
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                print("Program closed by user.")
                pygame.quit()
                os._exit(1)
            if event.type == pygame.KEYDOWN:
                search_bar.handle_event(event)
                if event.key == pygame.K_r:
                    # rotate only if an item is held and it's not stackable (or size != (1,1))
                    if cursor.item is not None and not getattr(cursor.item, "stackable", False):
                        cursor.item.rotate()                

        pygame.event.get()
        keys = pygame.key.get_pressed()
        if keys[K_c] and search_bar.clicked == 0:
            inventory_engine.inventory_list[0].add_item(
                Item(random.choice(list(ITEMS.keys())), 1))
        if keys[K_w] and search_bar.clicked == 0:
            inventory_engine.inventory_list[0].add_item(
                Weapon(random.choice(list(WEAPONS.keys())), 1))
        # dans la boucle principale, là où tu gères keys = pygame.key.get_pressed()
        if keys[K_b] and search_bar.clicked == 0:
            # crée une instance fraîche à chaque appui
            fish = Item("big_fish", 1, size=(2,1), rarity="rare", stackable=False)
            inventory_list[0].add_item(fish)
        if keys[K_d] and search_bar.clicked == 0:
            # crée une instance fraîche à chaque appui
            fish = Item("Poisson_Bar", 1, size=(1,1), rarity="Commun", stackable=False)
            inventory_list[0].add_item(fish)       
                 
    
        win.fill((0, 0, 0))
        search_bar.update(cursor)
        inventory_engine.update(cursor, search_bar.text)
        cursor.update(keys, search_bar.position, search_bar.scale)
        clock.tick(FPS)
        pygame.display.update()

if __name__ == "__main__":
    main()