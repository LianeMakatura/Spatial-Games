# Heavily inspired by CS1 implementation of Conway's Game of Life
# written by Devin Balkcom, edits by Hany Farid and Tom Cormen
# Modified by Liane Makatura
# Winter 2017, CS76: Evolutionary Game Dynamics
# Final Project

from cell import Cell
from random import *
from math import *

class Colony:
    def __init__(self, rows, columns, cell_size, settings):
        self.rows = rows
        self.columns = columns
        self.cell_size = cell_size

        self.settings = settings # has COOP_COLOR, DEFECT_COLOR, threshold, stubbornness, payoff, silence, etc

        self.cells = []

        # create the cell data list
        for r in range(rows):
            y = r * cell_size
            for c in range(columns):
                x = c * cell_size
                cell = Cell(x, y, cell_size)
                self.cells.append(cell)

    def draw(self):
        for cell in self.cells:
            cell.draw(self.settings.COOP_COLOR, self.settings.DEFECT_COLOR)

    # compute the index of a cell at r,c in the grid
    def ci(self, r, c):
        r %= self.rows
        c %= self.columns
        index = r * self.columns + c
        return index

    # get the cell object at r, c
    def cell(self, r, c):
        index = self.ci(r, c)
        return self.cells[index]

    # count cooperating neighbors adjacent to r, c
    def count_coop_neighbors(self, r, c):
        coop_neighbors = 0

        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr != 0 or dc != 0:
                    nr = r + dr
                    nc = c + dc
                    if self.cell(nr, nc).coop:
                        coop_neighbors += 1

        return coop_neighbors

    '''
    Computes the next generation of cells using standard threshold
    threshold - the minimum number of defecting neighbors required for this neighbor to defect
    '''
    def next_generation_threshold(self):
        # create a temporary list to store status of cells
        # for the next generation
        lnext = [True] * len(self.cells)

        # Use the threshold to update the temporary list
        for r in range(self.rows):
            for c in range(self.columns):
                coop_n = self.count_coop_neighbors(r, c)
                def_n = 8 - coop_n

                if def_n >= self.settings.threshold:          #if you have enough defecting neighbors, you defect
                    cell_idx = self.ci(r, c)
                    lnext[cell_idx] = False

        # Use the temporary list to update cells,
        # moving into the next generation
        for i in range(len(self.cells)):
            self.cells[i].coop = lnext[i]

    '''
    Updates cell boolean "silent", whether a given individual is silent or not in a particular round
    '''
    def update_cell_silence(self):
        for cell in self.cells:
            rand = random()
            if rand <= self.settings.silence:
                cell.silent = True
            else:
                cell.silent = False

    '''
    Resets the silence map to all false, so no residual values interfere
    '''
    def reset_silence_map(self):
        for cell in self.cells:
            cell.silent = False

    '''
    establish payoff of each cell
    Params:
    r - row of central pixel
    c - col of central pixel
    '''
    def calc_cell_payoff(self, r, c, weight_func):
        p = 0
        strategy = self.cell(r, c).coop     # true if coop, false if defect

        for dr in range(-1, 2):         #only looks at -1, 0, 1
            for dc in range(-1, 2):     #only looks at -1, 0, 1
                if dr != 0 or dc != 0:  # don't look at central pixel
                    nr = (r + dr) % self.rows
                    nc = (c + dc) % self.columns

                    #compute payoff weighting (proportional to distance)
                    alpha = weight_func(r,c,nr,nc)

                    #if neighbor not silent, calculate their opinion
                    if not self.cell(nr, nc).silent:
                        if self.cell(nr, nc).coop:      #neighbor coop
                            if strategy:
                                p += alpha * self.settings.payoff[0]          #cc
                            else:
                                p += alpha * self.settings.payoff[2]          #dc
                        else:
                            if strategy:
                                p += alpha * self.settings.payoff[1]          #cd
                            else:
                                p += alpha * self.settings.payoff[3]          #dd
        #print(r, c, nr, nc, alpha)
        return p

    '''
    '''
    def irrational_neighbor_pick(self, r, c):
        n = randint(1,9) #from [1,8]
        if n == 1:
            return (-1,-1)
        elif n==2:
            return (-1, 0)
        elif n==3:
            return (-1, 1)
        elif n==4:
            return (0, -1)
        elif n==5:
            return (0, 1)
        elif n==6:
            return (1, -1)
        elif n==7:
            return (1, 0)
        else:
            return (1, 1)


    '''
    use best response to update cells for next generation
    Params:
    weight_func - function used to compute the weighting for degrees of influence
    '''
    def next_generation_best_response(self, weight_func, irrational=False):
        # create a temporary list to store status of cells
        # for the next generation
        lnext = [True] * len(self.cells)

        # update silent instances if necessary
        if self.settings.silence != 0:
            self.update_cell_silence()
        else:
            print("resetting")
            self.reset_silence_map()

        # calculate payoffs for all cells
        p_now = [0] * len(self.cells)
        for r in range(self.rows):
            for c in range(self.columns):
                cell_idx = self.ci(r, c)
                p_now[cell_idx] = self.calc_cell_payoff(r, c, weight_func)

        # Update strategy in temporary list
        for r in range(self.rows):
            for c in range(self.columns):
                cell_idx = self.ci(r, c)
                rand = random()     #random number in [0.0, 1.0)
                if rand < self.settings.stubbornness:
                    lnext[cell_idx] = self.cell(r, c).coop   # keep original strategy (too stubborn to switch)

                elif irrational:        # update using irrational best response
                    pa = p_now[cell_idx]                       # central cell payoff

                    # pick random neighbor
                    (n_dr, n_dc) = self.irrational_neighbor_pick(r, c)
                    n_r = (r + n_dr) % self.rows
                    n_c = (c + n_dc) % self.columns
                    n_index = self.ci(n_r, n_c)
                    if self.cells[n_index].silent:
                        lnext[cell_idx] = self.cell(r, c).coop                   # if neighbor silent, keep strategy
                        continue

                    pb = p_now[n_index]        # neighbor's payoff

                    # calculate prob of switching
                    power = -1*self.settings.beta*(pb - pa)
                    try:
                        prob_of_switch = 1.0 / (1 + exp(power))
                    except OverflowError:
                        if power < 0:
                            prob_of_switch = 1.0        #overflowed because exp was too small
                        else:
                            prob_of_switch = 0.0        # overflowed because exp was too big

                    # pick random number q in [0,1]
                    rand2 = random()
                    if rand2 < prob_of_switch:
                        lnext[cell_idx] = self.cell(n_r, n_c).coop   # adopt neighbor strategy
                    else:
                        lnext[cell_idx] = self.cell(r, c).coop      # keep original strategy

                # if we are rational and not too stubborn, compute best strategy -- perfect best response
                else:
                    best_strategy = self.cells[cell_idx].coop # mine is current best strategy
                    best_payoff = p_now[cell_idx]

                    # look at your neighbors responses (and your own); keep strategy of best one
                    for dr in range(-1, 2):         #only looks at -1, 0, 1
                        for dc in range(-1, 2):     #only looks at -1, 0, 1
                            nr = r + dr
                            nc = c + dc
                            ni = self.ci(nr, nc)

                            if p_now[ni] > best_payoff: #only if better than your current best response
                                best_payoff = p_now[ni]
                                best_strategy = self.cell(nr, nc).coop
                            if p_now[ni] == best_payoff:
                                if self.cells[ni].coop == self.cells[cell_idx].coop: # keep strategy similar to yours
                                    best_strategy = self.cell(nr, nc).coop              # if multiple best responses

                    lnext[cell_idx] = best_strategy         #adopt the best strategy



        # Update cell strategies for next generation
        for i in range(len(self.cells)):
            self.cells[i].coop = lnext[i]

    def irrational_best_response(self, weight_func):
        self.next_generation_best_response(weight_func, True)


    # Presets
    def preset_all_blue(self):
        for i in range(len(self.cells)):
            self.cells[i].coop = True

    # (r,c) coordinates of central pixel
    def preset_3x3(self, r, c):
        self.preset_all_blue()
        for dr in range(-1, 2):         #only looks at -1, 0, 1
            for dc in range(-1, 2):     #only looks at -1, 0, 1
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.columns
                self.cell(nr, nc).coop = False

    # (r,c) coordinates of central pixel
    def preset_5x5(self, r, c):
        self.preset_all_blue()

        for dr in range(-2, 3):         #only looks at -1, 0, 1
            for dc in range(-2, 3):     #only looks at -1, 0, 1
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.columns
                self.cell(nr, nc).coop = False

    def preset_vonNeumann(self, r, c):
        self.preset_all_blue()
        self.cell(r, c).coop = False
        self.cell(r-1, c).coop = False
        self.cell(r+1, c).coop = False
        self.cell(r, c-1).coop = False
        self.cell(r, c+1).coop = False

    def print_sil_map(self):
        for i in range(len(self.cells)):
            print(self.cells[i].silent)