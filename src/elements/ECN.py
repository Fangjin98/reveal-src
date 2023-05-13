import random
from constant import *

RANGE = 150


def generate_capacity_for_ecn():
    f = open(r"../data/ecncapcaity", 'w')
    for i in range(0, ECNAMOUNT):
        capacity = random.randint(20000, 50000)
        f.write(str(capacity) + '\n')
    f.close()


def get_ecn_capacity():
    ECNCapacity = []
    f = open(r"../data/ecncapcaity", 'r')
    for i in range(ECNAMOUNT):
        ECNCapacity.append(int(f.readline()))
    f.close()
    return ECNCapacity


class ecn:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.vnf = []

    def install_vnf(self, v_id, v_cost):
        self.vnf.append(v_id)
        self.capacity = self.capacity - v_cost

    def is_useable(self, cost):
        return self.capacity >= cost

    def get_id(self):
        return self.id

    def get_vnfs(self):
        return self.vnf

    def get_capacity(self):
        return self.capacity


if __name__ == "__main__":
    generate_capacity_for_ecn()
