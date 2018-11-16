#!/usr/bin/python

import sys

if (len(sys.argv) != 3):
    print "Usage: " + sys.argv[0]  + " test.in test.out"
    print "\ttest.in \tInput file"
    print "\ttest.out\tOutput file"
    sys.exit(1)

in_file  = open(sys.argv[1], "r")
out_file = open(sys.argv[2], "r")

class Satellite:
    def __init__(self, lat, lon, vel, max_w, max_d):
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
        # TODO

    def can_take(self):
        self.photos.sort(key=lambda x: x[2])
        for photo in self.photos:
            self.calc_position(photo[2])
            if not ((self.lat + self.d[0][0] <= photo[0] <= self.lat + self.d[0][1]) and
                    (self.lon + self.d[1][0] <= photo[1] <= self.lon + self.d[1][1])):
                return False
        return True

class Collection:
    def __init__(self, val, loc, ranges):
        self.value = val
        self.locations = loc
        self.ranges = ranges

    def add_photo(self, photo):
        time_ok = False
        for time in self.ranges:
            if time[0] <= photo[2] <= time[1]:
                time_ok = True
                break
        if not time_ok:
            return
        for i in range(0, len(locations)):
            if locations[i][0] == photo[0] and locations[i][1] == photo[1]:
                del locations[i]
                break

    def is_taken(self):
        return not locations

duration = int(in_file.readline())
s_num = int(in_file.readline())
sat = []
for i in range(0, s_num):
    n = [int(x) for x in in_file.readline().split()]
    sat.append(Satellite(n[0], n[1], n[2], n[3], n[4]))

cnt = int(in_file.readline())

col = []
for i in range(0, cnt):
    v, l, r = map(int,in_file.readline().split())
    locations = []
    for j in range(0, l):
        locations.append(map(int, in_file.readline().split()))
    times = []
    for j in range(0, r):
        times.append(map(int, in_file.readline().split()))
    col.append(Collection(v, locations, times))

num = int(out_file.readline())
for i in range(0, num):
    f, l, t, s = map(int, out_file.readline().split())
    sat[s].add_photo((t, f, l))
    for collection in col:
        collection.add_photo((t, f, l))

for satellite in sat:
    if not satellite.can_take():
        print "Satellites can not take such photos!"
        sys.exit(0)

pt = 0
for collection in col:
    if collection.is_taken():
        pt += collection.value

print "Total number of points: " + str(pt)
