import sys
import numpy

max_trust: int = 100
boost_angle_threshold = 15
boost_distance_threshold = 1000
checkpoint_radius_sqr = 360000.0


class Point:
    def __init__(self, coordinate_x, coordinate_y):
        self.x = coordinate_x
        self.y = coordinate_y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, k: int):
        return Point(k * self.x, k * self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def dist_sqr(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2


class CheckpointManager:
    def __init__(self):
        self.checkpoints = []
        self.currentLap = 0
        self.checkpoint_index = -1
        self.best_boost_index = None

    def should_use_boost(self):
        return self.checkpoint_index == self.best_boost_index

    def update(self, next_cp):
        if next_cp not in self.checkpoints:
            self.checkpoints.append(next_cp)
            self.checkpoint_index += 1
        elif next_cp == self.checkpoints[0]:
            if self.currentLap == 0:
                self.compute_best_boost_index()
            if len(self.checkpoints) > 1:
                self.currentLap += 1
            self.checkpoint_index = 0
        else:
            self.checkpoint_index = self.checkpoints.index(next_cp)

        print('Lap: ', self.currentLap, 'CpIndex: ', self.checkpoint_index, 'Boost index: ',
              self.best_boost_index, file=sys.stderr, flush=True)

    def compute_best_boost_index(self):
        longest_dist = 0
        for i in range(len(self.checkpoints)):
            j = i + 1 if i + 1 < len(self.checkpoints) else 0
            if i != j:
                current_dist = self.checkpoints[i].dist_sqr(checkpoints[j])
                if current_dist > longest_dist:
                    self.best_boost_index = j
                    longest_dist = current_dist


can_boost = True
checkpoints = CheckpointManager()
preposition = Point(-1, -1)
init = False

while True:
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in
                                                                                               input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    position = Point(x, y)
    checkpoint = Point(next_checkpoint_x, next_checkpoint_y)
    angle = abs(next_checkpoint_angle)

    if preposition == Point(-1, -1):
        preposition = position

    checkpoints.update(checkpoint)

    target = checkpoint
    thrust = max_trust
    use_boost = False
    if angle < 1:
        thrust = max_trust
        use_boost = can_boost and checkpoints.should_use_boost()
    else:
        d_pos = position - preposition
        target = checkpoint - (d_pos * 3)
        dist_to_cp_sqr = position.dist_sqr(checkpoint)
        dist_slowdown_factor = numpy.clip(dist_to_cp_sqr / (checkpoint_radius_sqr * 4), 0, 1)
        angle_slowdown_factor = 1 - numpy.clip(angle / 90, 0, 1)
        print('Slowdown: distance - ', dist_slowdown_factor, ' angle - ', angle_slowdown_factor,
              file=sys.stderr, flush=True)
        thrust = max_trust * dist_slowdown_factor * angle_slowdown_factor
    preposition = position
    if use_boost:
        can_boost = False

    thrust_str = 'BOOST' if use_boost else f'{thrust}'
    print(f'{target.x} {target.y} {thrust_str}')
