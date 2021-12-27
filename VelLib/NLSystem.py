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
        lat, lon = self.valueCheck(lat, lon)
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

    def nearestNodeSearch(self, lat, lon):
        min_nodename = None
        min_dist = math.inf
        min_lat = None
        min_lon = None
        for node in self.getNodes(lat, lon):
            nlat, nlon = self.nodes[node]
            dist = self.calculateDistance(lat, lon, nlat, nlon)
            if dist < min_dist:
                min_dist = dist
                min_nodename = node
                min_lat = nlat
                min_lon = nlon
        return {"name":min_nodename, "dist":min_dist, 'lat':min_lat, 'lon':min_lon}

    def valueCheck(self, lat, lon):
        if not isinstance(lat, float):
            try:
                lat = float(lat)
            except Exception:
                raise(TypeError, "lat value must be float.")
        if not isinstance(lon, float):
            try:
                lon = float(lon)
            except Exception:
                raise(TypeError, "lon value must be float.")
        return lat, lon