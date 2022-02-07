import numpy as np
import math
from numpy import random

# init values
N = 100  # Number of passengers
max_floors = 100  # Number of floors
threshold = 3000  # Min value to stop looping at. would change based on N ?
init_ann_threshold = 100  # Annealing threshold. might change based on N
perc_ann = .0015          # Percentage of annealing threshold for variable
trials = 1

trial_max = 10000  # limit of how many times while loop runs because I wasn't sure about the threshold values tbh
trial_current = 0

# MC parameters
X = int(np.random.randint(1, 100, size=1))
a = 167339
C = 1245821689
m = 45972398567


def random(N, a, c, m, X):
    results_def = []
    for i in range(N + 1):
        if i == 0:
            X = (a * X + c) % m
            continue
        X = (a * X + c) % m
        results_def.append(X / m)
    return results_def


def d_trav(order):
    distance = 0
    current_floor = 0
    for floor in order:
        distance += abs(floor - current_floor)
        current_floor = floor
    return distance


def heads_tails():
    prob = np.array(random(2, a, C, m, X))
    if prob[0] <= .5:
        x_ = "f"
    else:
        x_ = "i"
    if prob[1] <= .5:
        y_ = "f"
    else:
        y_ = "i"

    return x_, y_


def switch(first, second, pass1, pass2):  # because python doesn't have switch cases
    if (first == "i" and second == "i"):
        if (pass1.ii < pass2.fi) and (pass2.ii < pass1.fi):
            return 1
    elif (first == "i" and second == "f"):
        if (pass1.ii > pass2.ii) and (pass2.fi < pass1.fi):
            return 2
    elif (first == "f" and second == "i"):
        if (pass1.fi < pass2.fi) and (pass2.ii > pass1.ii):
            return 3
    elif (first == "f" and second == "f"):
        if (pass1.fi > pass2.ii) and (pass2.fi > pass1.ii):
            return 4
    return -1


def swap_indices(pass1, pass2, num, order, indices, passengers,
                 dtot):  # a maybe-overly-complicated way to swap two floors
    temporder = order.copy()
    if num == 1:
        order[pass1.ii] = pass2.i
        order[pass2.ii] = pass1.i

        temp_pass1_ii = pass1.ii
        pass1.ii = pass2.ii
        pass2.ii = temp_pass1_ii
    elif num == 2:
        order[pass1.ii] = pass2.f
        order[pass2.fi] = pass1.i

        temp_pass1_ii = pass1.ii
        pass1.ii = pass2.fi
        pass2.fi = temp_pass1_ii
    elif num == 3:
        order[pass1.fi] = pass2.i
        order[pass2.ii] = pass1.f

        temp_pass1_fi = pass1.fi
        pass1.fi = pass2.ii
        pass2.ii = temp_pass1_fi
    elif num == 4:
        order[pass1.fi] = pass2.f
        order[pass2.fi] = pass1.f

        temp_pass1_fi = pass1.fi
        pass1.fi = pass2.fi
        pass2.fi = temp_pass1_fi

    dtemp = d_trav(order)
    if dtemp < dtot or abs(dtemp - dtot) <= ann_threshold:
        # to remove annealing, get rid of the or condition
        # for completely random, remove if line and else & order = temporder also
        passengers[indices[0]] = pass1
        passengers[indices[1]] = pass2
    else:
        order = temporder
    return order, passengers


class Pass:  # Passenger object because I couldn't think of a better way to keep the floors in order lol
    def __init__(self, i, f, ii, fi):
        self.i = i  # initial floor
        self.f = f  # final floor
        self.ii = ii  # initial floor global index
        self.fi = fi  # final floor global index


totresults = []

for i in range(trials):
    results = []
    N = 100  # Number of passengers
    max_floors = 100  # Number of floors
    ann_threshold = init_ann_threshold  # might change based on N

    trial_max = 10000  # limited because I wasn't sure about the threshold values tbh
    trial_current = 0

    # MC parameters
    a = 167339
    C = 1245821689
    m = 45972398567
    X = int(np.random.randint(1, 100, size=1))

    floors = np.array(random(2 * N, a, C, m, X))
    floors *= max_floors  # Floors up to some number
    floors = floors.astype(int)

    passengers = []
    order = []  # "Global" order; the elevator goes to these floors in this order
    dtot = 0

    for x in range(0, N * 2, 2):
        if floors[x] == floors[x + 1]:
            if floors[x] == 0:
                floors[x + 1] += x
            else:
                floors[x + 1] = int(floors[x + 1] / 2)
        order.append(floors[x])
        order.append(floors[x + 1])
        # Naive order of picking up each passenger individually and bringing them to their destination
        # without picking up/dropping off anyone else

        currPass = Pass(floors[x], floors[x + 1], x, x + 1)  # create a passenger object for each N passenger
        passengers.append(currPass)

    dtot = d_trav(order)

    # minimum tracker init
    order_min = order.copy()
    passengers_min = passengers.copy()
    min_d = dtot

    while dtot > threshold and trial_current < trial_max:
        X = int(np.random.randint(1, 100, size=1))

        indices = np.array(random(2, a, C, m, X))  # Get two passengers indices
        indices *= N
        indices = indices.astype(int)

        if indices[0] != indices[1]:
            pass1 = passengers[indices[0]]
            pass2 = passengers[indices[1]]
            first, second = heads_tails()  # Determine if switching the passengers' initial/final floors
            num = switch(first, second, pass1, pass2)
            # Checks to see if moving would be physically possible (num != -1), i.e. making sure that
            # passenger initial floor comes before their final floor if indices were changed

            if num != -1:
                order, passengers = swap_indices(pass1, pass2, num, order, indices, passengers, dtot)

            if d_trav(order) < min_d:  # updates minimum if needed
                min_d = d_trav(order)
                order_min = order.copy()
                passengers_min = passengers.copy()

            dtot = d_trav(order)
        trial_current += 1
        results.append(dtot)
        ann_threshold = perc_ann * dtot # Comment this out for constant threshold
    totresults.append(results)

# print("Min value:", min_d)
# print("Min passenger order:")
# for x in passengers_min:
#     print(x.i, x.f, x.ii, x.fi)
# print("Min order:", order)

for x in totresults:
    print(x)

# for x in passengers:
#     print(x.i, x.f, x.ii, x.fi)
