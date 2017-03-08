# Written by Liane Makatura
# Winter 2017, CS76: Evolutionary Game Dynamics
# Final Project

## Weighting functions/Parameters for distance (move into GUI)
# degrees of influence (primary/secondary sources have proportionally weighted influence; tertiary later)
# specify a distance/weighting function that takes two cell locations and computes a weighting for the influence

def inv_euclidean(r1, c1, r2, c2):
    dist = ((r2-r1) * (r2-r1)) + ((c2-c1) * (c2-c1))        # fix this so it's modular (respects torus)
    if dist != 0:
        return 1/dist
    return 0

def inv_manhattan(r1, c1, r2, c2):
    dist = abs(r2-r1) + abs(c2-c1)
    if dist != 0:
        return 1/dist
    return 0

def uniform_w(r1, c1, r2, c2):
    return 1
