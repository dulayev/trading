from datetime import datetime
from itertools import cycle
import copy
import collections
import math

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

    def RemovePoint(self, point):
        LeastSquares.AppendPoint(self, (point[0], point[1], -point[2]))

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

    least_squares = LeastSquares()
    least_squares.LoadPoints(data)
    extra_point = [22, 10, 5]
    least_squares.AppendPoint(extra_point)
    assert least_squares.Compute() == LeastSquares.ComputeFor(data + [extra_point])
    least_squares.RemovePoint(extra_point)
    assert least_squares.Compute() == LeastSquares.ComputeFor(data)

def Variance(linear_model, points, part):

    def Delta(point):
        x = point[0]
        real_y = point[1]
        linear_y = linear_model[0] * x + linear_model[1]
        return abs(real_y - linear_y)

    delta_points = [(p, Delta(p)) for p in points]
    
    delta_points.sort(key = lambda dp : dp[1], reverse = True)

    total_weight = sum(p[2] for p in points)
    goal_weight = total_weight * part

    delta = 0.0
    current = total_weight
    for p in delta_points:
        current -= p[0][2]
        if current < goal_weight:
            delta = p[1]
            break
    return delta

def TestVariance():
    a = 2.0
    b = 5.0
    count = 20
    data = [[x, a * x + b, 1] for x in range(count)]
    linear_model = (a, b)
    assert Variance(linear_model, data, 1.0) == 0.0
    assert Variance(linear_model, data, 0.5) == 0.0
    assert Variance(linear_model, data, 0.0) == 0.0
    
    data.append([0, 0, 20])
    assert Variance(linear_model, data, 0.4) == 0.0
    assert Variance(linear_model, data, 0.5) == 0.0
    assert Variance(linear_model, data, 0.51) == 5.0
    assert Variance(linear_model, data, 1.0) == 5.0
                  
    data.insert(0, [0, 20, 10])
    assert Variance(linear_model, data, 0.3) == 0.0
    assert Variance(linear_model, data, 0.6) == 5.0
    assert Variance(linear_model, data, 0.9) == 15.0

Stats = collections.namedtuple("Stats", ["deal_count", "volume", "gain", "leftover"])
Strategy = collections.namedtuple("Strategy", ["trend_len", "enter", "fix", "drop", "max_count"])

def OvertakeTrend(linear_model, point):
    trend_up = linear_model[0] >= 0
    actual_price = point[1]
    modeled_price = linear_model[0] * point[0] + linear_model[1]
    above_trend = actual_price >= modeled_price

    return trend_up == above_trend

def TestOvertakeTrend():
    trend_up = (0.5, 1)
    assert OvertakeTrend(trend_up, (1.0, 1.6))
    assert OvertakeTrend(trend_up, (1.0, 1.5))
    assert not OvertakeTrend(trend_up, (1.0, 1.4))
    trend_down = (-0.5, 1)
    assert OvertakeTrend(trend_down, (1.0, 0.4))
    assert not OvertakeTrend(trend_down, (1.0, 0.5))
    assert not OvertakeTrend(trend_down, (1.0, 0.6))

def ExceedDelta(linear_model, delta, point):
    actual_price = point[1]
    modeled_price = linear_model[0] * point[0] + linear_model[1]
    return abs(actual_price - modeled_price) > delta    

def TestExceedDelta():
    trend = (1, 2)
    assert not ExceedDelta(trend, delta = 0.5, point = (1.0, 3.0))
    assert not ExceedDelta(trend, delta = 0.5, point = (1.0, 3.5))
    assert not ExceedDelta(trend, delta = 0.5, point = (1.0, 2.5))
    assert not ExceedDelta(trend, delta = 0.5, point = (1.0, 3.4))
    assert not ExceedDelta(trend, delta = 0.5, point = (1.0, 2.6))
    assert ExceedDelta(trend, delta = 0.5, point = (1.0, 3.6))
    assert ExceedDelta(trend, delta = 0.5, point = (1.0, 2.4))

def Simulate(points, strategy):


    stats = Stats(deal_count = 0, volume = 0.0, gain = 0.0, leftover = 0)

    trend_points = []
    trend_ready = False

    for point in points:

        if not trend_ready:
            trend_points.append(point)

            if trend_points[-1][0] - trend_points[0][0] < strategy.trend_len:
                continue

            least_squares = LeastSquares()
            least_squares.LoadPoints(trend_points)
            trend_ready = True        
            continue
        else:
            trend = least_squares.Compute()
            print("trend")
            print(trend)
            if stats.leftover == 0:
                # look for enter
                if not OvertakeTrend(trend, point):
                    delta = Variance(trend_points, strategy.enter)

                    if ExceedDelta(trend, delta, point):
                        stats.deal_count += 1
                        stats.leftover += max_count
                        stats.volume += max_count * point[1]

    return stats

def TestSimulate():
    a = 2.0
    b = 5.0
    count = 20
    data = [[x, a * x + b, 1] for x in range(count)]
    data.insert(10, (10, 0, 1))
    strategy = Strategy(trend_len = 10, enter = 0.8, fix = 0.8, drop = 1.0, max_count = 1)

    stats = Simulate(data, strategy)
    print(stats)
    assert stats == Stats(deal_count = 1, volume = 1.0, gain = 0.0, leftover = 1)
    
TestLeastSquares()
TestVariance()
TestOvertakeTrend()
TestExceedDelta()
TestSimulate()

data = ReadFile("/home/dulayev/Documents/BRF8 [Price].txt")
print(len(data))         
print(data[0])



trend_len = 7 * 24 * 3600 # seconds in week
strategy = Strategy(trend_len, enter = 0.8, fix = 0.8, drop = 0.8, max_count = 1)

#stats = Simulate(data, strategy)
#print(stats)
