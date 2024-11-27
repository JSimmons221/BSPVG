import heapq
import math
from heapq import heapify
import numpy as np
from numpy.random import random_sample
import networkx as nx
from networkx import Graph
from scipy.constants import point
from shapely import Point, LineString, Polygon
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.neighbors import KDTree

np.random.seed(0)

class Obstacle:
    def __init__(self, x, y, sx, sy, pad):
        self.x: float = x
        self.y: float = y
        self.sx: float = sx
        self.sy: float = sy
        cords = [
            [x - pad, y - pad],
            [x + sx + pad, y - pad],
            [x + sx + pad, y + sy + pad],
            [x - pad, y + sy + pad]
        ]
        self.padded: Polygon = Polygon(cords)

    def check_intersection(self, item):
        return self.padded.intersects(item)

    def distance(self, item):
        return self.padded.distance(item)

def random_obstacle(rx, ry, pad, max_ob):
    x = np.random.uniform(-rx, rx - max_ob)
    y = np.random.uniform(-ry, ry - max_ob)
    sx = np.random.uniform(0, min(rx/2, rx-x, max_ob))
    sy = np.random.uniform(0, min(ry/2, ry-y, max_ob))
    return Obstacle(x, y, sx, sy, pad)

class World:
    def __init__(self, n_obstacles, rx, ry, pad, max_ob):
        self.obstacles = []
        i = 0
        inter = False
        while i < n_obstacles:
            new_ob = random_obstacle(rx, ry, pad, max_ob)
            for ob in self.obstacles:
                if ob.check_intersection(new_ob.padded):
                    inter = True
                    break
            if not inter:
                self.obstacles.append(new_ob)
                i += 1

        self.rx = rx
        self.ry = ry
        self.pad = pad

    def check_intersection(self, item):
        for obs in self.obstacles:
            if obs.check_intersection(item):
                return True
        return False

    def check_inter_point(self, px, py):
        p = Point(px, py)
        return self.check_intersection(p)

    def check_inter_path(self, px1, py1, px2, py2):
        p = LineString([[px1, px2], [py1, py2]])
        return self.check_intersection(p)

    def sample_world(self):
        while True:
            x = np.random.uniform(-self.rx, self.rx)
            y = np.random.uniform(-self.ry, self.ry)
            if not self.check_inter_point(x, y):
                return x, y

    def plot_world(self, fig, ax):

        ax.spines['left'].set_position('center')
        ax.spines['bottom'].set_position('center')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        ax.set_xlim([-self.rx, self.rx])
        ax.set_ylim([-self.ry, self.ry])

        for ob in self.obstacles:
            obst = patches.Rectangle((ob.x - ob.sx/2, ob.y - ob.sy/2), ob.sx, ob.sy, facecolor='red', edgecolor='black')
            ax.add_patch(obst)
            obst = patches.Rectangle((ob.x - (ob.sx + 2 * self.pad)/2, ob.y - (ob.sy + 2 * self.pad)/2), ob.sx + 2 * self.pad, ob.sy + 2 * self.pad, facecolor='none', edgecolor='red')
            ax.add_patch(obst)

    def nearest_obs(self, p):
        smallest = math.inf
        for ob in self.obstacles:
            dist = ob.distance(p)
            if dist < smallest:
                smallest = dist
        return smallest


# This is probably more similar to like a batch PRM, but it seemed like a good tradeoff instead of creating a new KDTree
# every node as I could not figure out how to implement a dynamic KDTree
class PRMStar:
    def __init__(self, world, batches, bsize, sr):
        self.g: Graph = Graph()
        self.world: World = world
        self.nodes = {}
        self.tree: KDTree

        # Loop for the number of batches
        self.create_prm(batches, bsize, sr)
        self.polygonalize(bsize * batches)

        print(self.g)

    def create_prm(self, batches, bsize, sr):
        all_nodes = None
        for batch in range(batches):
            # Store the nodes created and calculate the radius size
            bnodes = []
            csr = sr * (1 - math.log2(batch/batches + 1))
            # Create bsize number of nodes
            for i in range(bsize):
                index = i + bsize * batch
                node = self.world.sample_world()
                self.nodes[index] = node
                bnodes.append(np.array(node))
                self.g.add_node(index)

            # If there are no nodes yet, set all nodes to the nodes created, else append bnodes to all nodes
            bnodes = np.array(bnodes)
            if all_nodes is None:
                all_nodes = bnodes
            else:
                all_nodes = np.vstack((all_nodes, bnodes))

            # Create a KDTree from all_nodes
            if batch == batches - 1:
                self.tree = KDTree(all_nodes)

    def polygonalize(self, n):
        found = []
        for ni in range(n):
            node = self.nodes[ni]
            p = (Point(node[0], node[1]))
            node = np.array(node)
            rad = self.world.nearest_obs(p)
            in_rad = self.tree.query_radius(node.reshape(1, -1), rad)

            dist1 = math.inf
            ind1 = -1
            dist2 = math.inf
            ind2 = -1
            for oni in in_rad:
                onode = self.nodes[oni]
                op = Point(onode[0], onode[1])
                dist = op.distance(p)

                if dist < dist1:
                    dist2 = dist1
                    ind2 = ind1
                    dist1 = dist
                    ind1 = oni
                elif dist < dist2:
                    dist2 = dist
                    ind2 = oni



        
