import numpy as np


def belief_loss(expect, actual):
    expect = set(expect)
    actual = set(actual)
    
    inter_set = expect & actual
    or_set = expect | actual
    return float(len(inter_set)/len(or_set))

def donate_loss(expect, actual):
    dist = np.sqrt(np.sum(np.square(expect - actual)))
    return dist

def token_loss(origin, after, truth_index, false_index):
    truth_wealth = [[origin[index], after[index]] for index in truth_index]
    false_wealth = [[origin[index], after[index]] for index in false_index]
    
    if len(truth_wealth) == 0:
        value1 = 0
    else:
        value1 = sum([x[0] - x[1] for x in truth_wealth])/len(truth_wealth)
    if len(false_wealth) == 0:
        value2 = 0
    else:
        value2 = sum([x[0] - x[1] for x in false_wealth])/len(false_wealth)

    return value1 - value2