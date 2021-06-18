import numpy as np


from aletheia.scenario_search.loss import belief_loss, donate_loss, token_loss


def futarchy_loss(expect, actual, origin, after, truth_index, false_index, alpha=0.05):
    return belief_loss(expect, actual) + alpha * token_loss(origin, after, truth_index, false_index)


def qf_loss(expect, actual):
    return donate_loss(expect, actual)