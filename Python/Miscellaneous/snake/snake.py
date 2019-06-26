"""A simple program to simulate the snake game on terminal"""
import curses
import os
import random
import signal
import sys

UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
MIN_DIMENSION = 5
INIT_SNAKE_LEN = 3
MAX_LEVEL = 7
LEVELS = [10, 8, 6, 4, 3, 2, 1]
APPLE_NUM = 3


class Snake(object):
    def __init__(self, init_body, init_direction):
        self.body = [(body[0]+1, body[1]+1) for body in init_body]
        self.direction = init_direction

    def take_step(self, position, grow=False):
        if not grow:
            self.body = self.body[1:] + [position]
        else:
            self.body += [position]

    def set_direction(self, direction):
        self.direction = direction

    @property
    def head(self):
        return self.body[-1]


class Apple(object):
    def __init__(self, height, width, snake_body):
        while True:
            x = random.randint(1, height)
            y = random.randint(1, width)
            if (x, y) not in snake_body:
                break;
        self.x = x
        self.y = y

    @property
    def position(self):
        return self.x, self.y


class Game(object):
    def __init__(self, height, width):
        self.height = max(height, MIN_DIMENSION)
        self.width = max(width, MIN_DIMENSION)
        self.score = 0
        # initialize the snake
        self.snake = Snake([(int(self.height/2), i) for i in range(INIT_SNAKE_LEN)], RIGHT)
        # initialize the apple
        self.apple = self.generate_apple()
        # initialize game level
        self.levels = LEVELS
        self.level = 0
        self.apple_need = APPLE_NUM
        self.win = False

    def generate_apple(self):
        return Apple(self.height, self.width, self.snake.body)

    def board_matrix(self):
        matrix = []
        # the first line
        row = ['+'] + ['-'] * self.width + ['+']
        matrix.append(row)
        # the middle rows
        matrix += [['|'] + [' '] * self.width + ['|'] for i in range(self.height)]
        # the last row
        matrix.append(row)
        # put the snake in it
        head = self.snake.head
        matrix[head[0]][head[1]] = 'X'
        for body in self.snake.body[:-1]:
            matrix[body[0]][body[1]] = 'O'
        # put the apple in it
        matrix[self.apple.position[0]][self.apple.position[1]] = '*'
        return matrix

    def render(self, stdscr):
        matrix = game.board_matrix()
        stdscr.addstr(0, 0, "Level: {}".format(self.level+1))
        stdscr.addstr(1, 0, "Score: {}".format(self.score))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                stdscr.addstr(i+2, j, matrix[i][j])

    def print_result(self, stdscr):
        message = "You win!!!" if self.win else "You died!!!"
        stdscr.addstr(self.height + 5, 0, message)

    def move(self, direction):
        if direction == 'w':
            direction = UP
        elif direction == 's':
            direction = DOWN
        elif direction == 'd':
            direction = RIGHT
        elif direction == 'a':
            direction = LEFT
        
        if direction in (UP, DOWN, RIGHT, LEFT):
            if not (direction[0] + self.snake.direction[0] == 0 and 
                    direction[1] + self.snake.direction[1] == 0):
                self.snake.set_direction(direction)

        next_x = self.snake.head[0] + self.snake.direction[0]
        next_y = self.snake.head[1] + self.snake.direction[1]
        # check whether it collides with the wall
        if next_x <= 0 or next_x > self.height or next_y <= 0 or next_y > self.width:
            return False
        # check whether it collides with snake
        next_position = (next_x, next_y)
        if next_position in self.snake.body:
            return False
        # check whether get the apple and take the step
        if next_position == self.apple.position:
            self.snake.take_step(next_position, grow=True)
            self.score += 1
            # check whether go to the next level
            if self.score % self.apple_need == 0:
                self.snake = Snake(
                        [(int(self.height/2), i) for i in range(INIT_SNAKE_LEN)], RIGHT
                        )
                self.level += 1
                if self.level >= MAX_LEVEL:
                    self.win = True
                    return False
                
            self.apple = self.generate_apple()
        else:
            self.snake.take_step(next_position)
        return True


def play(stdscr, game):
    while True:
        curses.halfdelay(game.levels[game.level])
        stdscr.clear()
        # render the game
        game.render(stdscr)
        stdscr.refresh()
        step = None
        try:
            step = stdscr.getkey()
        except:
            pass
        if not game.move(step):
            break

    game.print_result(stdscr)
    stdscr.refresh()
    curses.nocbreak()

    stdscr.getkey()
    stdscr.getkey()
    stdscr.getkey()


if __name__ == "__main__":
    height = input("Enter the height of the board: ")
    width = input("Enter the width of the board: ")
    game = Game(int(height), int(width))

    curses.wrapper(play, game)
