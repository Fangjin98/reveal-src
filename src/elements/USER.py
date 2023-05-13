import math
import random
import os
import pandas as pd
from constant import *
from elements import topo

path = os.path.dirname(os.path.abspath(__file__))


def get_unaccessible_ecn(filepath, useramount=USERAMOUNT):
    upos = topo.get_user_pos(filepath, useramount)
    unaccess = []
    for i in range(useramount):
        m_unaccess = []
        for j in range(ECNAMOUNT):
            if math.sqrt(pow(upos[str(i)][0] - ecnx[j], 2) + pow(upos[str(i)][1] - ecny[j], 2)) > ecnr:
                m_unaccess.append(j)
        unaccess.append(m_unaccess)
    return unaccess


def generate_requests(request_num):  # request per type per user
    googledata = pd.read_json("C:\\Users\\Public\\instance_events.json", encoding="utf-8", lines=True, nrows=2000)
    print(googledata.keys())
    requestpool = [[], []]
    requesttime = [[], []]
    # print(googledata['resource_request'][0])
    for i in range(2000):
        if googledata['resource_request'][i]['cpus'] == 0.0:
            continue
        if 0.01 < googledata['resource_request'][i]['cpus'] < 0.02:
            requestpool[1].append(math.ceil(googledata['resource_request'][i]['cpus'] * 2500))
            requesttime[1].append(googledata['time'][i])
        elif 0.05 < googledata['resource_request'][i]['cpus'] < 0.07:
            requestpool[0].append(math.ceil(googledata['resource_request'][i]['cpus'] * 2500))
            requesttime[0].append(googledata['time'][i])

    # G = []

    f = open("../data/user_" + str(USERAMOUNT) + "_requests_" + str(request_num), 'w')
    for k in range(USERAMOUNT):
        # gamm = [[], []]
        # print("User " + str(k) + "'s requests number of each type are " + str(gamm_count[0]) + ' and ' + str(gamm_count[1]))
        f.write(str(request_num) + ' ' + str(request_num) + '\n')
        for b in range(2):
            for i in range(request_num):  # select size of request from request pool randomly
                id = random.randint(0, len(requestpool[b]) - 1)
                # gamm[b].append([requestpool[b][id],requesttime[b][id]])
                f.write(str(requestpool[b][id]) + ' ' + str(requesttime[b][id]) + '\n')
        # G.append(gamm)
    f.close()


def get_user_requests_traffic(filepath, request_num, useramount=USERAMOUNT):
    f = open(filepath, 'r')
    G = []  # per request traffic
    t = []  # per type traffic
    for k in range(useramount):
        count = f.readline().split()
        request = []
        traffic = 0
        for i in range(request_num):
            data = f.readline().split()
            request.append(int(data[0]))
            traffic = traffic + int(data[0])
        G.append(request)
        t.append(traffic)
    return G, t


def get_user_requests_timestamp(filepath, request_num, useramount=USERAMOUNT):
    f = open(filepath, 'r')
    t = []
    for k in range(useramount):
        count = f.readline().split()
        request_timestamp = []
        for i in range(request_num):
            data = f.readline().split()
            request_timestamp.append(int(data[1]))
        t.append(request_timestamp)
    return t


class request:
    def __init__(self, id=-1, type=-1, user=-1, timestamp=-1, traffic=-1, vnf=-1, ecn=-1):
        self.id = id
        self.time = timestamp
        self.type = type
        self.u = user
        self.t = traffic
        self.vnf = vnf
        self.ecn = ecn

    def __lt__(self, other):
        return self.time < other.time

    def set_vnf(self, vnf):
        self.vnf = vnf

    def set_ecn(self, ecn):
        self.ecn = ecn

    def get_id(self):
        return self.id

    def get_time(self):
        return self.time

    def get_user(self):
        return self.u

    def get_traffic(self):
        return self.t

    def get_type(self):
        return self.type

    def get_vnf(self):
        return self.vnf

    def get_ecn(self):
        return self.ecn


if __name__ == '__main__':
    request_per_user = [15, 25, 35, 45]
    # for num in request_per_user:
    #     generate_requests(num)
    # timestamp=get_user_requests_timestamp("../data/user_requests")
    # print(timestamp)
    generate_requests(30)
