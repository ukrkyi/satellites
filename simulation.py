#!/usr/bin/python3
from math import copysign
from random import randint


class Satellite:
    def __init__(self, lat, lon, vel, max_w, max_d):
        self.initial = lat, lon, vel
        self.lat = lat
        self.lon = lon
        self.vel = vel
        self.max_w = max_w
        self.max_d = max_d
        self.turn = 0
        self.photos = []
        self.d = ([0, 0], [0, 0])

    def add_photo(self, photo):
        self.photos.append(photo)

    def calc_position(self, turn):
        diff_turn = turn - self.turn
        self.lon = (self.lon + 648000 - 15 * diff_turn) % 1296000 - 648000
        self.lat += copysign((diff_turn * abs(self.vel)) % 1296000, self.vel)
        while not (-324000 <= self.lat <= 324000): # Maybe we will miss 1 somewhere in this loop
            if self.lat > 324000:
                self.lat = 648000 - self.lat
            else:
                self.lat = -648000 - self.lat
            self.vel = -self.vel
            self.lon = self.lon % 1296000 - 648000
        self.d[0][0] = max(self.d[0][0] - self.max_w*diff_turn, -self.max_d)
        self.d[0][1] = min(self.d[0][1] + self.max_w*diff_turn,  self.max_d)
        self.d[1][0] = max(self.d[1][0] - self.max_w*diff_turn, -self.max_d)
        self.d[1][1] = min(self.d[1][1] + self.max_w*diff_turn,  self.max_d)
        self.turn = turn

    def cannot_take(self):
        self.return_to_initial()
        self.photos.sort(key=lambda x: x[2])
        for photo in self.photos:
            self.calc_position(photo[2])
            if not ((self.lat + self.d[0][0] <= photo[0] <= self.lat + self.d[0][1]) and
                    (self.lon + self.d[1][0] <= photo[1] <= self.lon + self.d[1][1])):
                return photo
            self.d[0][1] = self.d[0][0] = photo[0] - self.lat
            self.d[1][0] = self.d[1][1] = photo[1] - self.lon
        return False

    def try_can_take(self, new_photo, turn):
        self.return_to_initial()
        self.photos.sort(key=lambda x: x[2])
        for photo in self.photos:
            if turn < photo[2]:
                self.calc_position(turn)
                if not ((self.lat + self.d[0][0] <= new_photo[0] <= self.lat + self.d[0][1]) and
                        (self.lon + self.d[1][0] <= new_photo[1] <= self.lon + self.d[1][1])):
                    return False
                self.d[0][1] = self.d[0][0] = new_photo[0] - self.lat
                self.d[1][0] = self.d[1][1] = new_photo[1] - self.lon
            self.calc_position(photo[2])
            if not ((self.lat + self.d[0][0] <= photo[0] <= self.lat + self.d[0][1]) and
                    (self.lon + self.d[1][0] <= photo[1] <= self.lon + self.d[1][1])):
                return False
            self.d[0][1] = self.d[0][0] = photo[0] - self.lat
            self.d[1][0] = self.d[1][1] = photo[1] - self.lon
        return True

    def remove_photo_byindex(self, photo_ind):
        self.photos.pop(photo_ind)

    def remove_photo_byvalue(self, photo):
        self.photos.remove(photo)

    def find_photo(self, photo):
        return self.photos.index(photo)

    def __str__(self):
        return " ".join([str(i) for i in [self.lat, self.lon, self.vel, self.max_w, self.max_d]])

    def return_to_initial(self):
        self.lat, self.lon, self.vel = self.initial
        self.turn = 0
        self.d = ([0, 0], [0, 0])

    __repr__ = __str__


class Collection:
    def __init__(self, val, loc, ranges, id):
        self.value = val
        self.locations = loc
        self.ranges = ranges
        self.id = id

    def __str__(self):
        return "Locations: " + str(self.locations) + ", Ranges: " + str(self.ranges) + ", Value: " + str(self.value)

    __repr__ = __str__

    def time_suitable(self, turn):
        for r in self.ranges:
            if r[0] <= turn <= r[1]:
                return True
        return False

    def get_rand_photo(self):
        return self.locations[randint(0, len(self.locations))]

    def total_time(self):
        return sum([i[1] - i[0] for i in self.ranges])

    def find_mean_value(self):
        lats = [lat[0] for lat in self.locations]
        lons = [lon[1] for lon in self.locations]
        return sum(lats) / len(lats), sum(lons) / len(lons)


class Simulation:
    def __init__(self, duration, satellites, collections):
        self.duration = int(duration)
        self.satellites = satellites
        self.collections = collections
        self.score = 0
        self.current = 0

    def take_photo(self, col, ind, turn, sat):
        if sat.can_take(turn, self.collections[col].locations[ind]):
            sat.take_photo(turn, self.collections[col].locations[ind])
            self.collections[col].taken += 1
            if self.collections[col].is_taken():
                self.score += self.collections[col].value

    def simulate_full(self):
        self.order_collection_value()
        while self.current < self.duration:
            self.check_for_second()
            self.current += 1
        print(self.score)

    def order_collection_value(self):
        self.collections.sort(key=lambda x: x.value, reverse=True)

    def order_collections_time(self):
        self.collections.sort(key=lambda x: x.total_time())

    def order_collections_qvalue(self):
        self.collections.sort(key=lambda x: x.value / len(x.locations), reverse=True)

    def order_colletions_tqvalue(self):
        self.collections.sort(key=lambda x: x.value / (len(x.locations) * x.total_time()))

    def check_for_second(self):
        for sat in self.satellites:
            for col in range(0, len(self.collections)):
                if self.collections[col].time_suitable(self.current):
                    for photo_try in range(0, len(self.collections[col].locations)):
                        if sat.can_take(self.current, self.collections[col].locations[photo_try]):
                            print(self.current, "collection #", col, "photo #", photo_try)
                            self.take_photo(col, photo_try, self.current, sat)
                            break

    def find_timeslot(self, location):
        current = 0
        while current < self.duration:
            for sat in range(len(self.satellites)):
                if self.satellites[sat].try_can_take(location, current):
                    photo = (location[0], location[1], current)
                    self.satellites[sat].add_photo(photo)
                    return sat, photo

    def greedy(self, path):
        states = {k: dict() for k in range(self.duration)}
        self.order_collections_qvalue()
        for col in range(len(self.collections)):
            for photo in range(len(self.collections[col].locations)):
                depth = 1
                try:
                    time, sat = self.find_timeslot(self.collections[col].locations[photo], depth)[-1]
                except IndexError:
                    continue
                while sat in states[time] or not self.collections[col].time_suitable(time):
                    try:
                        time, sat = self.find_timeslot(self.collections[col].locations[photo], depth + 1, start=time)[-1]
                    except IndexError:
                        continue
                states[time].update({sat: (col, photo)})
                for sat in states[time]:
                    f = open(path, 'a')
                    print(time, sat, self.collections[states[time][sat][0]].id, states[time][sat][1], file=f)
                    f.close()
            print("Collection ended")
        return states

    def simulate_greedy(self, path):
        states = self.greedy(path)
        for key in sorted(states):
            self.current = key
            for sat in states[key]:
                col, photo = states[key][sat]
                if self.collections[col].time_suitable(self.current) and self.satellites[sat].can_take(self.current, self.collections[col].locations[photo]):
                    self.take_photo(col, photo, self.current, self.satellites[sat])
        print(self.score)

    def final(self, path):
        self.order_collection_value()
        for col in range(len(self.collections)):
            taken_photos = []
            for ph in range(len(self.collections[col].locations)):
                print(taken_photos)
                res = self.find_timeslot(self.collections[col].locations[ph])
                if not res:
                    for tp in taken_photos:
                        self.satellites[tp[0]].remove_photo_byvalue(tp[1])
                    taken_photos = None
                    break
                else:
                    taken_photos.append(res)
            f = open(path, 'a')
            if taken_photos:
                for tp in taken_photos:
                    print(tp[1][0], tp[1][1], tp[1][2], tp[0], file=f)
            f.close()


def create_simulation(path):
    with open(path) as f:
        duration = f.readline()
        satellites = []
        for i in range(int(f.readline())):
            satellites.append(Satellite(*[int(i) for i in f.readline().strip().split()]))
        num_collections = int(f.readline())
        collections = [None for i in range(num_collections)]
        for i in range(num_collections):
            collection_chr = f.readline().strip().split()
            value = int(collection_chr[0])
            num_locations = int(collection_chr[1])
            num_ranges = int(collection_chr[2])
            locations = [[int(i) for i in f.readline().strip().split()] for j in range(num_locations)]
            ranges = [[int(i) for i in f.readline().strip().split()] for i in range(num_ranges)]
            collections[i] = Collection(value, locations, ranges, i)
        return Simulation(duration, satellites, collections)
