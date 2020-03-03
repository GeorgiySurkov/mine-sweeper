import pygame
import copy
import random
from collections import deque
import os


SCREEN_SIZE = (800, 600)
FPS = 120


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        size = self.cell_size
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                pygame.draw.rect(
                    screen,
                    pygame.color.Color('white'),
                    (self.left + x * size, self.top + y * size, size, size),
                    1
                )

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            self.on_click(cell)

    def on_click(self, cell_coords):
        cell_x, cell_y = cell_coords
        board_copy = copy.deepcopy(self.board)
        if self.board[cell_y][cell_x] == 0:
            board_copy[cell_y][cell_x] = self.turn + 1
            self.turn = (self.turn + 1) % 2
        self.board = board_copy

    def get_cell(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        mouse_x -= self.left
        mouse_y -= self.top
        if mouse_x < 0 or mouse_y < 0:
            return None
        x = mouse_x // self.cell_size
        y = mouse_y // self.cell_size
        if x > self.width - 1 or y > self.height - 1:
            return None
        return x, y


class MineSweeper(Board):
    def __init__(self, width, height, mines):
        super(MineSweeper, self).__init__(width, height)
        self.win = None
        self.flag = load_image('flag.png')
        self.bomb = load_image('bomb.png')
        self.font = pygame.font.Font(None, self.cell_size)
        self.board = [[-1] * width for _ in range(self.height)]
        mines = random.sample(range(self.width * self.height), mines)
        mines_coords = map(lambda mine: (mine % self.width, mine // self.width), mines)
        for mine_coords in mines_coords:
            x, y = mine_coords
            self.board[y][x] = 10

    def set_view(self, left, top, cell_size):
        super(MineSweeper, self).set_view(left, top, cell_size)
        self.font = pygame.font.Font(None, self.cell_size)

    # def get_cell_neighbors(self, cell_position):
    #     x, y = cell_position
    #     height = self.height
    #     width = self.width
    #     neighbors = (
    #         ((x + 1) % width, (y + 1) % height),
    #         ((x + 0) % width, (y + 1) % height),
    #         ((x - 1) % width, (y + 1) % height),
    #         ((x - 1) % width, (y + 0) % height),
    #         ((x - 1) % width, (y - 1) % height),
    #         ((x + 0) % width, (y - 1) % height),
    #         ((x + 1) % width, (y - 1) % height),
    #         ((x + 1) % width, (y + 0) % height),
    #     )
    #     return neighbors

    def get_cell_neighbors(self, cell_position):
        x, y = cell_position
        height = self.height
        width = self.width
        index_changes = (
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
            (1, 0)
        )
        neighbors = []
        for index_change in index_changes:
            x_change, y_change = index_change
            if 0 <= x + x_change <= width - 1 and 0 <= y + y_change <= height - 1:
                neighbors.append(
                    (x + x_change, y + y_change)
                )
        return neighbors

    def open_cell(self, cell_coords):
        # mines_around = sum(1 if self.board[neighbor[1]][neighbor[0]] == 10 else 0 for neighbor in neighbors)
        # self.board[y][x] = mines_around
        nodes_to_visit = deque()
        nodes_to_visit.append(cell_coords)
        visited = [[False] * self.width for _ in range(self.height)]
        visited[cell_coords[1]][cell_coords[0]] = True
        while len(nodes_to_visit) > 0:
            node = nodes_to_visit.popleft()
            x, y = node
            neighbors = self.get_cell_neighbors(node)
            mines_around = sum(1 if self.board[neighbor[1]][neighbor[0]] in (10, 12) else 0 for neighbor in neighbors)
            self.board[y][x] = mines_around
            if mines_around == 0:
                for neighbor in neighbors:
                    n_x, n_y = neighbor
                    if not visited[n_y][n_x] and neighbor not in nodes_to_visit and self.board[n_y][n_x] != 10:
                        nodes_to_visit.append(neighbor)
                        visited[n_y][n_x] = True

    def get_click(self, mouse_event):
        if self.win is not None:
            return
        cell = self.get_cell(mouse_event.pos)
        if cell is None:
            return
        elif mouse_event.button == 1:
            self.on_left_btn_click(cell)
        elif mouse_event.button == 3:
            self.on_right_btn_click(cell)

    def on_left_btn_click(self, cell_coords):
        x, y = cell_coords
        if self.board[y][x] < 10:
            self.open_cell(cell_coords)
        elif self.board[y][x] == 10:
            self.win = False

    def on_right_btn_click(self, cell_coords):
        x, y = cell_coords
        if self.board[y][x] == -1:
            self.board[y][x] = 11
        elif self.board[y][x] == 10:
            self.board[y][x] = 12
            self.check_win()
        elif self.board[y][x] == 11:
            self.board[y][x] = -1
        elif self.board[y][x] == 12:
            self.board[y][x] = 10


    def render(self):
        size = self.cell_size
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                # if cell == 10:
                #     pygame.draw.rect(
                #         screen,
                #         pygame.color.Color('red'),
                #         (self.left + x * size, self.top + y * size, size, size),
                #     )
                if self.win is not None:
                    if not self.win and cell == 10 or cell == 12:
                        screen.blit(self.bomb, (
                            (self.left + x * size, self.top + y * size)
                        ))
                    elif cell == 11:
                        screen.blit(self.flag, (
                            (self.left + x * size, self.top + y * size)
                        ))
                    elif 0 <= cell <= 9:
                        text = self.font.render(str(cell), 1, pygame.color.Color('red'))
                        screen.blit(text, (self.left + x * size, self.top + y * size))
                    pygame.draw.rect(
                        screen,
                        pygame.color.Color('white'),
                        (self.left + x * size, self.top + y * size, size, size),
                        1
                    )
                else:
                    if cell == 11 or cell == 12:
                        screen.blit(self.flag, (
                            (self.left + x * size, self.top + y * size)
                        ))
                    elif 0 <= cell <= 9:
                        text = self.font.render(str(cell), 1, pygame.color.Color('red'))
                        screen.blit(text, (self.left + x * size, self.top + y * size))
                    pygame.draw.rect(
                        screen,
                        pygame.color.Color('white'),
                        (self.left + x * size, self.top + y * size, size, size),
                        1
                    )
        if self.win is not None:
            if self.win:
                text = 'You win'
            else:
                text = 'You lose'
            rendered_text = self.font.render(text, 1, pygame.color.Color('red'))
            text_width = self.font.size(text)[0]
            screen.blit(rendered_text, (self.left + ((self.width * self.cell_size) - text_width) // 2, self.top - self.cell_size))

    def check_win(self):
        for row in self.board:
            for cell in row:
                if cell == 10:
                    return
        self.win = True


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    h = 10
    w = 10
    size = 50
    game = MineSweeper(w, h, 10)
    game.set_view(
        SCREEN_SIZE[0] // 2 - (w * size) // 2,
        SCREEN_SIZE[1] // 2 - (h * size) // 2,
        size
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.get_click(event)
        screen.fill((0, 0, 0))
        clock.tick(FPS)
        game.render()
        pygame.display.flip()