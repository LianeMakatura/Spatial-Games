# Heavily inspired by CS1 implementation of Conway's Game of Life
# written by Devin Balkcom, edits by Hany Farid and Tom Cormen
# Modified by Liane Makatura
# Winter 2017, CS76: Evolutionary Game Dynamics
# Final Project

from canvas import *

class Cell:
    def __init__(self, x, y, cell_size):
        self.coop = True
        self.x = x
        self.y = y
        self.size = cell_size
        self.silent = False                 # for use in the opt out via silence option

    def defect(self):
        self.coop = False

    def cooperate(self):
        self.coop = True

    def flip(self):
        self.coop = not self.coop

    def draw(self, c, d):
        set_fill_color(d[0], d[1], d[2])
        if self.coop:
            set_fill_color(c[0], c[1], c[2])

        draw_rectangle(self.x, self.y, self.size, self.size)