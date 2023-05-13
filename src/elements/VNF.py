import sys

from constant import *
import random
import os

path = os.path.dirname(os.path.abspath(__file__))


def generate_vnf_process_demand():
    f = open(os.path.dirname(path) + "\\data\\vnfprocess", 'w')
    for i in range(0, VNFAMOUNT):
        process = random.randint(1000, 1500)
        f.write(str(process) + '\n')
    f.close()


def get_vnf_process_demand():
    VNFprocess = []
    f = open(os.path.dirname(path) + "\\data\\vnfprocess", 'r')
    for i in range(0, VNFAMOUNT):
        process = int(f.readline())
        VNFprocess.append(process)
    f.close()
    return VNFprocess


def generate_vnf_cost():
    VNFcost = []
    f = open("../data/vnfcost", 'w')
    for i in range(0, VNFAMOUNT):
        process = random.randint(40, 50)
        VNFcost = VNFcost + [process]
        f.write(str(process)+'\n')
    f.close()
    return VNFcost

def get_vnf_cost():
    cost = []
    f = open("../data/vnfcost", 'r')
    for i in range(0, int(VNFAMOUNT)):
        cost.append(int(f.readline()))
    f.close()
    return cost


def get_placement_of_vnf(filepath):
    f = open(filepath, 'r')
    F = []
    while True:
        line = f.readline()
        if not line:
            break
        vnf = line.split()[0]
        F.append(vnf)
    return F


class vnf:
    def __init__(self, id=-1, user=-1, ecn=-1, type=-1, value=-1, capacity=-1,cost=-1):
        self.id = id
        self.user = user
        self.ecn = ecn
        self.type = type
        self.value = value
        self.capacity = capacity
        self.cost=cost
        self.requests = []

    def __lt__(self, other):
        return self.value > other.value

    def get_id(self):
        return self.id

    def get_value(self):
        return self.value

    def get_user(self):
        return self.user

    def get_type(self):
        return self.type

    def get_capacity(self):
        return self.capacity

    def is_available(self, demand):
        return self.capacity >= demand
    def get_ecn(self):
        return self.ecn
    def alloc_request(self, request_id, request_demand):
        self.capacity = self.capacity - request_demand
        self.requests.append(request_id)
    def set_type(self,type):
        self.type=type


def get_assignment_of_vnf(filepath):
    f = open(filepath, 'r')
    vnf_list = []
    for j in range(USERAMOUNT):
        line = f.readline().split()
        tmp = []
        for v in line:
            tmp.append(vnf(id=int(v), user=j, type=0))
        vnf_list.append(tmp)
    return vnf_list


if __name__ == "__main__":
    # generate_vnf_process_demand()
    generate_vnf_cost()