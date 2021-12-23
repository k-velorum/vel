import math

class NLSystem:
    def __init__(self, zlv:int = 18, area:int= 1):
        self.sq = [2**x for x in range(25)]
        self.z = zlv
        self.nodes = {}
        self.nlmap = {}
        self.amin = abs(area)*-1
        self.amax = abs(area)+1

    def deg2num(self, lat, lon):
        lat_rad = math.radians(lat)
        n = self.sq[self.z]
        return int((lon + 180.0) / 360.0 * n), int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    def register(self, lat, lon, key):
        x, y = self.deg2num(lat, lon)
        for i in range(self.amin, self.amax):
            for j in range(self.amin, self.amax):
                if x+i not in self.nlmap:
                    self.nlmap[x+i] = {}
                if y+j not in self.nlmap[x+i]:
                    self.nlmap[x+i][y+j] = set()
                self.nlmap[x+i][y+j].add(key)
        self.nodes[key] = (lat, lon)

    def getNodes(self, lat, lon):
        x, y = self.deg2num(lat, lon)
        try:
            return self.nlmap[x][y]
        except KeyError:
            return {}