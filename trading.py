from datetime import datetime
from itertools import cycle
import copy

class LeastSquares:

    def LoadPoints(self, points):
        self.sum_x = 0.0
        self.sum_y = 0.0
        self.sum_w = 0.0
        self.sum_xy = 0.0
        self.sum_x2 = 0.0
        for point in points:
            x = point[0]
            y = point[1]
            w = point[2] # weight
            self.sum_x += w * x
            self.sum_y += w * y 
            self.sum_w += w
            self.sum_x2 += w * x * x
            self.sum_xy += w * x * y

    def Compute(self):
        a = (self.sum_w * self.sum_xy - self.sum_x * self.sum_y) / \
            (self.sum_w * self.sum_x2 - self.sum_x * self.sum_x)
        b = (self.sum_y - a * self.sum_x) / self.sum_w
        return (a, b)

    def AppendPoint(self, point):
        x = point[0]
        y = point[1]
        w = point[2] # weight
        self.sum_x += w * x
        self.sum_y += w * y 
        self.sum_w += w
        self.sum_x2 += w * x * x
        self.sum_xy += w * x * y

    @staticmethod
    def ComputeFor(points):
        least_squares = LeastSquares()
        least_squares.LoadPoints(points)
        return least_squares.Compute()

# reads file and returns tuples array
def ReadFile(name):
    res = []
    header = True
    epoch = datetime(year = 2017, month = 1, day = 1)
    with open(name, 'r') as f:
        for line in f:
            if not header:
                parts = line.split(',')
                print(parts[2] + parts[3])
                dt = datetime.strptime(parts[2] + parts[3], "%Y%m%d%H%M%S")
                seconds = (dt - epoch).total_seconds()
                price = 0.0
                for i in range(4, 8):
                    price += float(parts[i])
                price /= 4
                volume = float(parts[8])
                print((seconds, price, volume))
                res.append((seconds, price, volume))
                if len(res) > 10:
                    break
            else:
                header = False
    return res

# data = ReadFile("/home/dulayev/Documents/BRF8 [Price].txt")
# print(len(data))         

def TestLeastSquares():
    gold_a = 3.0
    gold_b = 8.0
    count = 10
    data = [[x, gold_a * x + gold_b, 1] for x in range(count)]
    assert LeastSquares.ComputeFor(data) == (gold_a, gold_b) # correct for indeed linear sequence with weight == 1
    data1 = [(p[0], p[1], 10) for p in data]
    assert LeastSquares.ComputeFor(data1) == (gold_a, gold_b) # the same for another constant weight
    deltas = cycle((2, -2))
    for i in range(0, count // 4 * 2): # even number <= count / 2
        delta = next(deltas)
        data[i][1] += delta # add +/- 2 from beginning
        data[-1-i][1] += delta # add +/- 2 from the end
    assert LeastSquares.ComputeFor(data) == (gold_a, gold_b)

    data2 = copy.deepcopy(data)
    weight = 20
    data2[0][2] = weight # increase weight of 1st item

    for i in range(1, weight):
        data.append(data[0]) # duplicate 1st item (weight - 1) times

    assert len(data) != len(data2)
    assert LeastSquares.ComputeFor(data) == LeastSquares.ComputeFor(data2)


    
TestLeastSquares()

