import math

def get_distance_from_point(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def get_snap_direction_from_angle(x1, y1, x2, y2):
    '''get the closest snap value to the angle'''

    dx = x2 - x1
    dy = y2 - y1

    angle = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle)

    possible_snap_values = [0, 45, -45, 90, -90, 135, -135, 180]
    snap_value_angle = min(possible_snap_values, key=lambda x:abs(x-angle_degrees))

    return snap_value_angle




