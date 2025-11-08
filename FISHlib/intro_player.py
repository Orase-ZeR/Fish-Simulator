import pygame
from typing import List, Optional

class Intro:
    @staticmethod
    def load_font(path: str, size: int) -> pygame.font.Font:
        try:
            return pygame.font.Font(path, size)
        except Exception as e:
            print(f"[Intro] Impossible de charger la police '{path}': {e}. Utilisation d'un fallback.")
            return pygame.font.Font(None, size)

    @staticmethod
    def render_multiline(surface: pygame.Surface, font: pygame.font.Font, lines: List[str],
                         color=(255,255,255), start_y=None, center_vertical=False, reserved_top=0):
        w, h = surface.get_size()
        rendered = [font.render(line, True, color) for line in lines]
        spacing = max(6, font.get_height() // 6)
        total_h = sum(s.get_height() for s in rendered) + spacing * (len(rendered)-1)

        if center_vertical:
            y = reserved_top + (h - reserved_top - total_h) // 2
        elif start_y is not None:
            y = start_y
        else:
            y = (h - total_h) // 2

        for surf in rendered:
            x = (w - surf.get_width()) // 2
            surface.blit(surf, (x, y))
            y += surf.get_height() + spacing

    @staticmethod
    def intro_start(screen: Optional[pygame.Surface] = None,
                    pages: Optional[List[List[str]]] = None,
                    font_path: str = r"assets/DTM-Sans.otf",
                    font_size: int = 48,
                    title: Optional[str] = None,
                    title_font_size: int = 72,
                    allow_fullscreen_if_no_screen: bool = True) -> None:

        if pages is None:
            pages = [["test", "ligne 2", "ligne 3"]]

        created_screen = False
        if screen is None:
            if not allow_fullscreen_if_no_screen:
                raise ValueError("screen is None and allow_fullscreen_if_no_screen is False")
            pygame.display.init()
            screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
            created_screen = True

        clock = pygame.time.Clock()
        page_idx = 0
        total_pages = len(pages)

        font = Intro.load_font(font_path, font_size)
        title_font = Intro.load_font(font_path, title_font_size)
        small_font = Intro.load_font(font_path, max(14, font_size // 3))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE,):
                        running = False
                    elif event.key in (pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN):
                        page_idx += 1
                        if page_idx >= total_pages:
                            running = False
                    elif event.key == pygame.K_LEFT:
                        page_idx = max(0, page_idx - 1)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in (1,):
                        page_idx += 1
                        if page_idx >= total_pages:
                            running = False

            screen.fill((0,0,0))

            # titre en haut
            reserved_top = 0
            if title:
                title_surf = title_font.render(title, True, (255,255,255))
                screen_width = screen.get_width()
                reserved_top = 50 + title_surf.get_height() + 20
                screen.blit(title_surf, ((screen_width - title_surf.get_width()) // 2, 50))

            # texte centré sous titre
            cur_lines = pages[page_idx] if page_idx < total_pages else []
            Intro.render_multiline(screen, font, cur_lines, center_vertical=True, reserved_top=reserved_top)

            # petit texte bas
            w, h = screen.get_size()
            page_text = f"Page {page_idx+1}/{total_pages} - [clic / espace / suivant]"
            page_surf = small_font.render(page_text, True, (180,180,180))
            screen.blit(page_surf, ((w - page_surf.get_width())//2, h - page_surf.get_height() - 20))

            pygame.display.flip()
            clock.tick(60)

        # fermer proprement si écran temporaire créé
        if created_screen:
            pygame.display.quit()
