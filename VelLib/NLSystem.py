import math

class NLSystem:
    def __init__(self, zlv:int = 18, area:int= 1):
        self.sq = 2**zlv
        self.z = zlv
        self.nodes = {}
        self.nlmap = {}
        self.amin = abs(area)*-1
        self.amax = abs(area)+1

    def deg2num(self, lat, lon):
        lat_rad = math.radians(lat)
        n = self.sq
        return int((lon + 180.0) / 360.0 * n), int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    def num2deg(self, xtile, ytile):
        lon_deg = xtile / self.sq * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / self.sq)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def getSample(self, lat, lon):
        x, y = self.deg2num(lat, lon)
        lat, lon = self.num2deg(x, y)
        lat2 = self.num2deg(x, y+1)
        lon2 = self.num2deg(x+1, y)
        latdiff = self.calculateDistance(lat, lon, lat2[0], lat2[1])
        londiff = self.calculateDistance(lat, lon, lon2[0], lon2[1])
        return latdiff, londiff

    def calculateDistance(self, lat1, lon1, lat2, lon2):
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371
        return c * r * 1000

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

if __name__ == "__main__":
    n = NLSystem(19)
    n.register(34.69381538515487, 135.26862338666018, "cross")
    print(n.nlmap)
    print(n.nodes)
    print(n.getNodes(34.69386730978066, 135.2690654567932))
    print(n.getNodes(34.69534343908719, 135.2666656474996))