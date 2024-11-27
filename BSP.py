import math

def digits(idx):
    return math.floor(math.log(idx, 10)) + 1


class BSP:
    def __init__(self, x = 0.0, y = 0.0, half_dist = -1.0, vert = True, divide = -1.0, idx = 0):
        self.x: float = x
        self.y: float = y
        self.id: int = idx
        self.vert: bool = vert
        self.divide: float = divide
        self.half_dist: float = half_dist

        # If vertical divide, self.neg is left
        # If horizontal divide, self.neg is down
        self.neg = None
        self.pos = None

    def __str__(self):

        return f"BSP(ID={self.id}, {'Vertical' if self.vert else 'Horizontal'}, {'No divide' if self.divide == -1 else "Divide at " + str(self.divide)})"

    # If the node is split,
    def split(self):
        self.divide = self.x
        self.neg = BSP(vert=False, divide=self.y, idx=self.id)
        self.pos = BSP(vert=False, divide=self.y, idx=self.id)

        # Nodes will always be split in four, so the actual left and right don't matter and should never be choosen
        # Node IDs go Top Left - 1, Top Right - 2, Bottom Right - 3, Bottom Left, 4
        self.neg.pos = BSP(x=self.x - self.half_dist / 2, y=self.y + self.half_dist / 2, rad=self.half_dist / 2, vert=True, idx=self.id * 10 + 1)
        self.pos.pos = BSP(x=self.x + self.half_dist / 2, y=self.y + self.half_dist / 2, rad=self.half_dist / 2, vert=True, idx=self.id * 10 + 2)
        self.pos.neg = BSP(x=self.x + self.half_dist / 2, y=self.y - self.half_dist / 2, rad=self.half_dist / 2, vert=True, idx=self.id * 10 + 3)
        self.neg.neg = BSP(x=self.x - self.half_dist / 2, y=self.y - self.half_dist / 2, rad=self.half_dist / 2, vert=True, idx=self.id * 10 + 4)

        return [self.neg.pos, self.pos.pos, self.pos.neg, self.neg.neg]

    def get_corners(self, idx):
        if idx == 0 or self.divide == -1:
            return [[self.x - self.half_dist, self.y + self.half_dist],
                    [self.x + self.half_dist, self.y + self.half_dist],
                    [self.x + self.half_dist, self.y - self.half_dist],
                    [self.x - self.half_dist, self.y - self.half_dist]]

        digs = digits(idx) - 1
        highid = math.floor(idx / (10 ** digs))

        if highid == 1:
            return self.neg.pos.get_corners(idx % (10 ** digs))
        if highid == 2:
            return self.pos.pos.get_corners(idx % (10 ** digs))
        if highid == 3:
            return self.pos.neg.get_corners(idx % (10 ** digs))
        if highid == 4:
            return self.neg.neg.get_corners(idx % (10 ** digs))

    def get_center(self, idx):
        if idx == 0 or self.divide == -1:
            return [self.x, self.y]

        digs = digits(idx) - 1
        highid = math.floor(idx / (10 ** digs))

        if highid == 1:
            return self.neg.pos.get_center(idx % (10 ** digs))
        if highid == 2:
            return self.pos.pos.get_center(idx % (10 ** digs))
        if highid == 3:
            return self.pos.neg.get_center(idx % (10 ** digs))
        if highid == 4:
            return self.neg.neg.get_center(idx % (10 ** digs))


    def search(self, x, y):
        # If the node has no divide, it has not been split so no need to check further
        if self.id == 0 and self.half_dist != -1 and (abs(x) > self.half_dist or abs(y) > self.half_dist):
            return -1
        if self.divide == -1:
            return self.id

        if self.vert:
            if x < self.divide:
                return self.neg.search(x, y)
            else:
                return self.pos.search(x, y)
        else:
            if y < self.divide:
                return self.neg.search(x, y)
            else:
                return self.pos.search(x, y)