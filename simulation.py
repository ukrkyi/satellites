from math import copysign
from random import randint


class Satellite:
    def __init__(self, lat, lon, vel, max_w, max_d):
        self.lat = lat
        self.lon = lon
        self.vel = vel
        self.max_w = max_w
        self.max_d = max_d
        self.turn = 0
        self.d = [0, 0]

    def calc_position(self, turn):
        diff_turn = turn - self.turn
        self.lon = (self.lon + 648000 - 15 * diff_turn) % 1296000 - 648000
        self.lat += copysign((diff_turn * abs(self.vel)) % 1296000, self.vel)
        while not (-324000 <= self.lat <= 324000):  # Maybe we will miss 1 somewhere in this loop
            if self.lat > 324000:
                self.lat = 648000 - self.lat
            else:
                self.lat = -648000 - self.lat
            self.vel = -self.vel
            self.lon = self.lon % 1296000 - 648000
        self.turn = turn

    def can_take(self, turn, location):
        self.calc_position(turn)
        if self.lat + self.d[0] - min(self.max_w, self.max_d) < location[0] < self.lat + + self.d[0] + min(self.max_w, self.max_d)\
                and self.lon + + self.d[1] - min(self.max_d, self.max_w) < location[1] < self.lon + self.d[1] + min(self.max_d, self.max_w):
                return True
        return False

    def take_photo(self, turn, location):
        if self.can_take(turn, location):
            self.d[0] = location[0] - self.lat
            self.d[1] = location[1] - self.lon
            return True

    def __str__(self):
        return " ".join([str(i) for i in [self.lat, self.lon, self.vel, self.max_w, self.max_d]])

    __repr__ = __str__


class Collection:
    def __init__(self, val, loc, ranges):
        self.value = val
        self.locations = loc
        self.ranges = ranges

    def time_suitable(self, turn):
        for r in self.ranges:
            if r[0] <= turn <= r[1]:
                return True
        return False

    def __str__(self):
        return "Locations: " + str(self.locations) + ", Ranges: " + str(self.ranges) + ", Value: " + str(self.value)

    def is_empty(self):
        return len(self.locations) == 0

    def get_rand_photo(self):
        return self.locations[0]

    __repr__ = __str__


class Simulation:
    def __init__(self, duration, satellites, collections):
        self.duration = int(duration)
        self.satellites = satellites
        self.collections = collections
        self.score = 0
        self.current = 0

    def take_photo(self, col, ind, turn, sat):
        if sat.can_take(turn, self.collections[col][ind]):
            sat.take_photo(turn, self.collections[col][ind])
            self.collections[col].pop(ind)
            if self.collections[col].is_empty():
                self.score += collections[col].value
                self.collections.pop(col)

    def simulate_full(self):
        while self.current < self.duration:
            for col in range(len(self.collections)):
                for sat in self.satellites:
                    if sat.can_take(self.current, self.collections[col].get_rand_photo()):
                        print('Can take')
                        self.take_photo(col, 0, self.current, sat)
                        break
            self.current += 1
        print(self.score)


with open("final_round_2016.in/final_round_2016.in/forever_alone.in") as f:
    duration = f.readline()
    satellites = []
    for i in range(int(f.readline())):
        satellites.append(Satellite(*[int(i) for i in f.readline().strip().split()]))

    num_collections = int(f.readline())
    collections = [None for i in range(num_collections)]
    for i in range(num_collections):
        collection_chr = f.readline().strip().split()
        value = collection_chr[0]
        num_locations = int(collection_chr[1])
        num_ranges = int(collection_chr[2])
        locations = [[int(i) for i in f.readline().strip().split()] for j in range(num_locations)]
        ranges = [[int(i) for i in f.readline().strip().split()] for i in range(num_ranges)]
        collections[i] = Collection(value, locations, ranges)


s_alone = Simulation(duration, satellites, collections)
s_alone.simulate_full()



