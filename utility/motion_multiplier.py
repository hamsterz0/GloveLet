# Author:       Joseph Tompkins
# Description:  This was an algorithm developed to adjust CV tracking motion, which
#               penalizes slow movements so that users have less gitter and finer
#               control, while rewarding faster movements so that users can move the cursor
#               across the screen quickly without accidentally exiting the frame and lose
#               tracking. This method was not used in the end, because it was found that
#               1-to-1 motion tracking felt more natural, and this algorithm would require
#               too much calibration to find a happy medium.
__all__ = ["motion_multiplier", "u", "delta_scale"]

from collections import Iterable


def u(dr, k_max=20, k_min=4, n=2, m=1):
    if dr < k_min:
        return -m
    elif dr > k_max:
        return n
    return ((n + m) * (dr - k_min) / (k_max - k_min)) - m


def motion_multiplier(prev_coord, delta_real_coord, k_max=20, k_min=4, n=2, m=1):
    """
    Multiplier that penalizes slow movements and rewards faster movements.\n
    :param prev_coord: The previously calculated coordinate. This will be the result of the last output of `motion_multiplier`
    and the initial value of `prev_coord` will be the value of the real frame coordinate.\t
    :param delta_real_coord: this is the change real frame coordinate, r - r_prev\t
    :param k_max: the upper-threshold value for delta_real_coord\t
    :param k_min: the lower-threshold value for delta_real_coord\t
    :param n: `int` the scale factor by which to scale values equal to or greater than `k_max`. Where `1` is `100%` scale factor.
    """
    return prev_coord + delta_scale(delta_real_coord, k_max, k_min, n, m)

def delta_scale(delta, k_max=20, k_min=4, n=2, m=1):
    res = None
    if isinstance(delta, Iterable):
        res = delta * [(1 + u(abs(dr), k_max, k_min, n, m)) for dr in delta]
    else:
        res = delta * (1 + u(abs(delta), k_max, k_min, n, m))
    return res
