import networkx as nx

from BSP import *

import math
from os.path import split

import numpy as np
from matplotlib.pyplot import connect

np.random.seed(0)
from networkx import Graph

FULL_OBS = -2 # The cell is completely in an obstacle
PART_OBS1 = -1 # The cell's center is in an obstacle
PART_OBS2 = 0 # Part of the cell might be in an obstacle
NO_OBS = 1 # None of the cell is in an obstacle



class DiskObs:
    def __init__(self, x, y, rad):
        self.x: float = x
        self.y: float = y
        self.rad: float = rad

    # Checks to see the distance from a point to the DiskObs
    def dist(self, xp, yp):
        return math.sqrt((xp - self.x)**2 + (yp - self.y)**2) - self.rad

    # Takes in an origin and direction for a line segment and checks to see if that segment
    def path_intersect(self, x1, y1, dx, dy, a):
        b = 2 * (dx * (x1 - self.x) + dy * (y1 - self.y))
        c = (x1 - self.x) ** 2 + (y1 - self.y) ** 2 - self.rad ** 2
        disc = b ** 2 - 4 * a * c

        # If there are no real roots than the path and disk do not intersect
        if disc < 0:
            return False

        # Calculate the first root, if it is within [0, 1] (i.e. the root lies on the line segment) then the path and
        # disk intersect at t1, else if, do the same for the second root, if neither point is within [0, 1] than the
        # disk intersects with the line extended from the line segment, but not the segment itself.
        sqrt_disc = math.sqrt(disc)
        t = (-b - sqrt_disc) / (2 * a)
        if 0 <= t <= 1:
            return True
        t = (-b + sqrt_disc) / (2 * a)
        if 0 <= t <= 1:
            return True

        return False


class DiskWorld:
    # half_dist is half the size of the world space (x and y range from [-half_dist, half_dist])
    # num_obs is the number of disk obstacles to place in the world
    def __init__(self, half_dist, obs):
        self.half_dist: float = half_dist
        self.obs = obs
        self.bsp = BSP(rad=half_dist)

        # The pessimistic is made using only vertices of free space, the optimistic may use the vertices of the part
        # space
        self.pessimistic = nx.Graph()
        self.optimistic = nx.Graph()

        # Lists of cells which are either fully in obstacles, fully in free space, or may be partially in an obstacle
        # Cell 0 is the first cell and it is added to part for now
        self.obs = []
        self.free = []
        self.part = [0]

    # check_cell takes in the values for a square cell centered at where the bounds are
    # [x or y - half_cell, x or y + half_cell) and returns if a cell is valid or not This basic implementation just
    # checks if the distance to any obstacles < the distance from the center of the cell to the corners
    def check_cell(self, x, y, half_cell):
        corner_dist = math.sqrt(2 * half_cell ** 2)

        # If the cell is found to be neither partially nor fully inside an obstacle then any further subdivisions of
        # that cell would also not be inside an obstacle so checks can be stopped for that cell. Since this is the
        # loosest assumption it acts as the base value before any checks with obstacles are done.
        ret = NO_OBS
        for obs in self.obs:
            # obs.dist returns the signed distance to the obstacle being checked
            obs_dist = obs.dist(x, y)
            # If obst dist < -corner dist than the cell is fully inside an obstacle and the checks for that cell can be
            # stopped, since all further subdivisions would also be in that obstacle
            if obs_dist < - corner_dist:
                return FULL_OBS

            # 0 < obs dist < corner dist then the center of the cell is outside the obstacle but a part of the cell
            # could be inside the obstacle so it should be used for optimistic planning and should be subdivided further
            # If it was already determined that part of the cell/the center of the cell is inside an obstacle than
            # the rest does not need to be checked
            if obs_dist < corner_dist:
                ret = PART_OBS2

        return ret

    # check_path takes in the start and end nodes of a path and checks it against every obstacle
    def check_path(self, x1, y1, x2, y2):
        # Precalculate dx, dy, and a since they do not change for the same path
        dx = x2-x1
        dy = y2-y1
        a = dx ** 2 + dy ** 2

        for obs in self.obs:
            if obs.path_intersect(x1, y1, dx, dy, a):
                return True

        return False

    # Needed:
    # - Start and end locations, [x, y]
    # Stored in class
    # - A BSP of the space
    # - A list of all cells with no obstacles
    # - A list of all cells with only obstacle
    # - A list of cells which are partially full, also to be used for further subdivision
    # - An optimistic graph, connect vertex cells of clear cells, Recalculated at each step
    # - A pessimistic graph, add paths connecting vertices of partially full cells
    def path(self, sx, sy, ex, ey):
        start_cell = self.bsp.search(sx, sy)
        end_cell = self.bsp.search()



