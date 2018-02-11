from datetime import datetime
from itertools import cycle

#
def LeastSquares(points):
    sum_x = 0.0
    sum_y = 0.0
    sum_w = 0.0
    sum_xy = 0.0
    sum_x2 = 0.0
    n = len(points)
    for point in points:
        x = point[0]
        y = point[1]
        w = point[2] # weight
        sum_x += w * x
        sum_y += w * y 
        sum_w += w
        sum_x2 += w * x * x
        sum_xy += w * x * y
    a = (sum_w * sum_xy - sum_x * sum_y) / (sum_w * sum_x2 - sum_x * sum_x)
    b = (sum_y - a * sum_x) / sum_w
    return (a, b)

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
    assert LeastSquares(data) == (gold_a, gold_b) # correct for indeed linear sequence with weight == 1
    data1 = [(p[0], p[1], 10) for p in data] 
    assert LeastSquares(data1) == (gold_a, gold_b) # the same for another constant weight
    deltas = cycle((2, -2))
    for i in range(0, count // 4 * 2): # even number <= count / 2
        delta = next(deltas)
        data[i][1] += delta # add +/- 2 from beginning
        data[-1-i][1] += delta # add +/- 2 from the end
    assert LeastSquares(data) == (gold_a, gold_b)

    data2 = data1 = data
    weight = 20
    data2[0][2] = weight # increase weight of 1st item

    for i in range(1, weight):
        data1.append(data1[0]) # duplicate 1st item (weight - 1) times
    assert LeastSquares(data1) == LeastSquares(data2)
    
TestLeastSquares()
