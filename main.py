from time import sleep
import pygame as pg
from random import randint


""" Possibilité de changer la texture des blocs de 0 à 9 """

def create_texture_path() -> tuple[list[str], list[str]]:

    """ 
    Création de 2 listes :
    - Chemin des textures
    - Noms des textures  
    """

    cell_path = "ressources/textures/95/"
    smiley_path = "ressources/textures/smileys/"
    nb_path = "ressources/textures/numbers/"


    liste_textures = [
        "blast",
        "cell1",
        "cell2",
        "cell3",
        "cell4",
        "cell5",
        "cell6",
        "cell7",
        "cell8",
        "celldown",
        "flag",
        "mine",
        "cellup",
        "falsemine"
    ]

    liste_textures_smiley = [
        "smiley1",
        "smiley2",
        "smiley3"
    ]

    liste_textures_nbs = [
        "nb1",
        "nb2",
        "nb3",
        "nb4",
        "nb5",
        "nb6",
        "nb7",
        "nb8",
        "nb9",
        "nb0",
        "nb-",
        "nb-off"
    ]


    out_list_path = []
    for name in liste_textures:
        out_list_path.append(cell_path + name + ".png")
    for name in liste_textures_smiley:
        out_list_path.append(smiley_path + name + ".png")
    for name in liste_textures_nbs:
        out_list_path.append(nb_path + name + ".png")

    out_list_names = []
    out_list_names.extend(liste_textures)
    out_list_names.extend(liste_textures_smiley)
    out_list_names.extend(liste_textures_nbs)

    return out_list_path, out_list_names





def convert_to_pygame_texture(texture_path: str, name) -> pg.surface:
    """ Convertit une image en texture """
    img = pg.image.load(texture_path).convert_alpha()
    if name.startswith("nb"):
        dims = (40, 60)
    elif name.startswith("smiley"):
        dims  = (50, 50)
    else:
        dims = CELL_DIMS
    img = pg.transform.scale(img, dims)
    surface = pg.Surface(dims, pg.SRCALPHA)
    surface.blit(img, (0, 0))
    return surface



def load_textures(list_texture_path: list[str], list_texture_name: list[str]) -> dict[str, pg.Surface]:
    """ Convertit une liste d'images en textures """
    loc_dic_textures = {}

    for idx in range(len(list_texture_path)):
        current_loading_texture = convert_to_pygame_texture(list_texture_path[idx], liste_texture_name[idx])
        loc_dic_textures[list_texture_name[idx]] = current_loading_texture

    return loc_dic_textures



def create_random_binary_grid(rng) -> list[list[int]]:

    """ MAGNIFIQUE !!! >>> """

    nb_columns, nb_rows = GRID_DIMS

    return [

        [1 if randint(0, rng) > rng-1 else 0 for _ in range(nb_columns)]

        for _ in range(nb_rows)
    ]


def draw_grid(cells: list[list[int]], passive_cell_texture: pg.Surface) -> pg.Surface:

    """ Dessiner le cache de la grille """

    surface = pg.Surface(GAME_SCREEN)
    cell_width, cell_height = CELL_DIMS

    for row_idx, row in enumerate(cells):
        for col_idx in range(len(row)):
            x, y = col_idx * cell_width, row_idx * cell_height
            surface.blit(passive_cell_texture, (x, y))

    return surface


def create_nb_grid(liste_bombs: list[list[int]]) -> list[list[str]]:

    """ Créer la liste des densités de mines """

    nb_columns, nb_rows = GRID_DIMS
    liste_nb = [['' for _ in range(nb_columns)] for _ in range(nb_rows)]

    neighbors = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for row_idx in range(nb_rows):
        for column_idx in range(nb_columns):

            if liste_bombs[row_idx][column_idx] == 1:
                liste_nb[row_idx][column_idx] = 'x'
                continue

            nb_voisins_mines = 0
            for decalage_x, decalage_y in neighbors:
                neighbour_x, neighbour_y = row_idx + decalage_x, column_idx + decalage_y
                if 0 <= neighbour_x < nb_rows and 0 <= neighbour_y < nb_columns \
                        and liste_bombs[neighbour_x][neighbour_y] == 1:
                    nb_voisins_mines += 1
            liste_nb[row_idx][column_idx] = str(nb_voisins_mines)

    return liste_nb


def get_texture_name_with_cell_content(content: str) -> str:

    """ 1 partie du contenu de la cellule, obtient le nom de la texture """

    dic_content_to_color = {
        "x": "blast",
        "0": "celldown",
        "1": "cell1",
        "2": "cell2",
        "3": "cell3",
        "4": "cell4",
        "5": "cell5",
        "6": "cell6",
        "7": "cell7",
        "8": "cell8",
    }
    return dic_content_to_color[content]


def get_every_surrounding_cells_0(original_list: list, current_cell_pos: tuple[int, int], grid_nb: list):

    """ Fonction récursive pour trouver les cellules vides environnentes """

    # cell_pos : (x, y)
    nb_columns, nb_rows = GRID_DIMS
    neighbors = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for x, y in neighbors:
        neighbour_x, neighbour_y = current_cell_pos[0] + x, current_cell_pos[1] + y

        # Si pas dans la liste
        if not (0 <= neighbour_x < nb_columns and 0 <= neighbour_y < nb_rows):
            continue

        # Si le voisin n'est pas 0
        if grid_nb[neighbour_y][neighbour_x] != "0":

            original_list.append((neighbour_x, neighbour_y))
            continue

        if (neighbour_x, neighbour_y) not in original_list:
            original_list.append((neighbour_x, neighbour_y))
            original_list = get_every_surrounding_cells_0(
                original_list=original_list,
                current_cell_pos=(neighbour_x, neighbour_y),
                grid_nb=grid_nb
            )

    return original_list


def get_mouse_pos_in_cell() -> tuple[int, int]:

    """ Obtenir la position de la souris dans la grille de cellules """

    mouse_pos = pg.mouse.get_pos()
    cell_x, cell_y = (mouse_pos[0] - MARGE_LEFT) // CELL_DIMS[0], \
                     (mouse_pos[1] - MARGE_UP) // CELL_DIMS[1]
    return cell_x, cell_y


def get_nb_texture(current_time: int) -> pg.Surface:

    """ Obtenir la surface de temps restant """

    surface = pg.Surface((120, 60))
    str_time = str(current_time).zfill(3)
    idx = 0
    for char in str_time:
        surface.blit(dic_textures["nb" + char], (idx * 40, 0))
        idx += 1

    return surface


def get_smiley_face(state: int) -> pg.Surface:

    """ Retourne la texture du smiley selon son état """

    if state == 1:
        return dic_textures["smiley1"]
    if state == 2:
        return dic_textures["smiley2"]
    return dic_textures["smiley3"]


def draw_every_hidden_mines(surface: pg.Surface, liste: list[list[int]], blasted_mine_pos: tuple[int, int]) -> pg.Surface:

    """ Ajoute à la surface visible par le joueur toutes les positions des mines """

    for row_idx, row in enumerate(liste):
        for column_idx, column in enumerate(row):
            if column == 1:
                x = column_idx * CELL_DIMS[0]
                y = row_idx * CELL_DIMS[1]
                surface.blit(dic_textures["mine"], (x, y))

    surface.blit(dic_textures["blast"], (blasted_mine_pos[0] * CELL_DIMS[0], blasted_mine_pos[1] * CELL_DIMS[1]))

    return surface



RES = (800, 600)
pg.init()
pg.mixer.init()
pg.display.set_caption("Démineur")
SCREEN = pg.display.set_mode(RES)
clock = pg.time.Clock()

GREY = (120, 120, 120)

MARGE_UP, MARGE_DOWN = 80, 20
MARGE_RIGHT, MARGE_LEFT = 40, 40
GAME_SCREEN = (RES[0] - (MARGE_RIGHT + MARGE_LEFT), RES[1] - (MARGE_UP + MARGE_DOWN))

GRID_DIMS = (20, 16)
CELL_DIMS = (GAME_SCREEN[0] // GRID_DIMS[0], GAME_SCREEN[1] // GRID_DIMS[1])
GAME_SCREEN = (CELL_DIMS[0] * GRID_DIMS[0], CELL_DIMS[1] * GRID_DIMS[1]) # Recalculer pour plus de précisions

sound_start = pg.mixer.Sound("ressources/sfx/start.mp3")
sound_click = pg.mixer.Sound("ressources/sfx/click.mp3")
sound_lose = pg.mixer.Sound("ressources/sfx/lose_minesweeper.mp3")
sound_win = pg.mixer.Sound("ressources/sfx/win.mp3")
sound_flag = pg.mixer.Sound("ressources/sfx/flag.mp3")
sound_flag_remove = pg.mixer.Sound("ressources/sfx/flagremove.mp3")

liste_textures_path, liste_texture_name = create_texture_path()
dic_textures = load_textures(liste_textures_path, liste_texture_name)
RNG_MINES = 10

class Game:
    def __init__(self):
        self.liste_flag_pos = []
        self.revealed_cells = []
        self.binary_grid = create_random_binary_grid(RNG_MINES)
        self.total_nb_cells = GRID_DIMS[0] * GRID_DIMS[1]
        self.total_nb_mines = sum(column for row in self.binary_grid for column in row if column == 1)
        self.nb_remaining_flags = self.total_nb_mines
        self.grid = draw_grid(cells=self.binary_grid, passive_cell_texture=dic_textures["cellup"])
        self.nb_grid = create_nb_grid(liste_bombs=self.binary_grid)
        self.smiley = get_smiley_face(1)
        self.ticks = 0
        self.running = True
        self.mine_clicked = False
        self.blasted_mine = None
        self.update_remaining_flags = True
        SCREEN.fill(GREY)
        pg.mixer.Sound.play(sound_start)
    

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            self.handle_events()
            self.update_display()
            clock.tick(30)
            self.ticks += 1
            if not self.running:
                sleep(3)
    

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)


    def handle_mouse_click(self, event):
        mouse_cell_x, mouse_cell_y = get_mouse_pos_in_cell()
        if not (0 <= mouse_cell_x < GRID_DIMS[0] and 0 <= mouse_cell_y < GRID_DIMS[1]):
            return

        cell_clicked_content = self.nb_grid[mouse_cell_y][mouse_cell_x]

        if event.button == 1 and (mouse_cell_x, mouse_cell_y) not in self.liste_flag_pos:
            self.reveal_cells(mouse_cell_x, mouse_cell_y, cell_clicked_content)
        elif event.button == 3:
            self.toggle_flag(mouse_cell_x, mouse_cell_y)


    def reveal_cells(self, x, y, cell_content):
        new_cells_unlocked = []
        if cell_content == "0":
            new_cells_unlocked = get_every_surrounding_cells_0(new_cells_unlocked, (x, y), self.nb_grid)
        else:
            new_cells_unlocked.append((x, y))

        for cell_pos in new_cells_unlocked:
            if cell_pos in self.revealed_cells:
                continue
            cell_content = self.nb_grid[cell_pos[1]][cell_pos[0]]
            if cell_content == "x":
                self.mine_clicked = True
                self.blasted_mine = cell_pos

            texture_name = get_texture_name_with_cell_content(cell_content)
            texture = dic_textures[texture_name]
            self.grid.blit(texture, (cell_pos[0] * CELL_DIMS[0], cell_pos[1] * CELL_DIMS[1]))
            self.revealed_cells.append(cell_pos)
        
        pg.mixer.Sound.play(sound_click)

        if len(self.revealed_cells) >= self.total_nb_cells - self.total_nb_mines:
            self.win_game()


    def toggle_flag(self, x, y):
        if (x, y) in self.revealed_cells:
            return
        if (x, y) in self.liste_flag_pos:
            self.liste_flag_pos.remove((x, y))
            self.nb_remaining_flags += 1
            cell_content = dic_textures["cellup"]
            pg.mixer.Sound.play(sound_flag_remove)
        else:
            self.liste_flag_pos.append((x, y))
            self.nb_remaining_flags -= 1
            cell_content = dic_textures["flag"]
            pg.mixer.Sound.play(sound_flag)

        self.update_remaining_flags = True
        self.grid.blit(cell_content, (x * CELL_DIMS[0], y * CELL_DIMS[1]))


    def update_display(self):

        """ Teste les conditions de temps, de victoire et update le display """

        if self.ticks % 30 == 0:
            time_texture_display = get_nb_texture(self.ticks // 30)
            SCREEN.blit(time_texture_display, (MARGE_LEFT, 10))

        if self.mine_clicked:
            self.lose_game()

        if self.update_remaining_flags:
            self.display_remaining_flags()

        SCREEN.blit(self.smiley, (SCREEN.get_width()//2 - self.smiley.get_width()// 2, MARGE_UP// 2 - self.smiley.get_width()//2))
        SCREEN.blit(self.grid, (MARGE_LEFT, MARGE_UP))
        pg.display.update()


    def win_game(self):

        """ Change le smiley et arrête le jeu """

        self.smiley = get_smiley_face(3)
        pg.mixer.Sound.play(sound_win)
        self.running = False


    def lose_game(self):

        """ Change le smiley, montre les mines et arrête le jeu """

        self.smiley = get_smiley_face(2)
        pg.mixer.Sound.play(sound_lose)
        self.grid = draw_every_hidden_mines(self.grid, self.binary_grid, self.blasted_mine)
        self.running = False


    def display_remaining_flags(self):

        """ Update le display du nb de drapeaux restants """

        flag_remaining_display = get_nb_texture(self.nb_remaining_flags)
        SCREEN.blit(flag_remaining_display, (SCREEN.get_width() - flag_remaining_display.get_width() - 40, 10))
        self.update_remaining_flags = False





if __name__ == "__main__":
    while True:
        game = Game()
        game.run()