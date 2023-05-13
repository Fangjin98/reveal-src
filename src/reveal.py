import math
import random
import pulp as pl

from constant import *
from elements import VNF
from elements import ECN
from elements import USER


def min_sum_id(k, knapsack):
    minvalue = 10000000
    id = 0
    for i in range(k):
        if not knapsack[i]:
            return i
        value = sum(knapsack[i])
        if value < minvalue:
            minvalue = value
            id = i
    return id


def random_pick(knapsack, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    index = -1
    for it, item_probability in zip(knapsack, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            index = knapsack.index(it)
            break
    return index


def solve_lp1(request_num, _K=kk, _P=pp):
    """
    x[i][j]: decision variables determine if VNF j installs in ECN i or not.
    y[i][j][k]: decision variables determine if user k acquire VNF j from ECN i or not.
    r[i][j][k]: the proportion of traffic amount
    """

    x = [
        [
            pl.LpVariable(
                "x^n" + str(i) + "_f" + str(j),
                lowBound=0,
                upBound=1,
                cat=pl.LpContinuous,
            )
            for j in range(VNFAMOUNT)
        ]
        for i in range(ECNAMOUNT)
    ]
    y = [
        [
            [
                pl.LpVariable(
                    "y^n" + str(i) + "_u" + str(k) + "_f" + str(j),
                    lowBound=0,
                    upBound=1,
                    cat=pl.LpContinuous,
                )
                for k in range(USERAMOUNT)
            ]
            for j in range(VNFAMOUNT)
        ]
        for i in range(ECNAMOUNT)
    ]

    c = VNF.get_vnf_cost()
    p = VNF.get_vnf_process_demand()
    P = ECN.get_ecn_capacity()
    G, t = USER.get_user_requests_traffic(
        "../data/user_" + str(20) + "_requests_" + str(30), request_num
    )
    phi = USER.get_unaccessible_ecn("../data/user_" + str(USERAMOUNT) + "_position")

    prob = pl.LpProblem("RVPA", pl.LpMinimize)
    prob += pl.lpSum(
        [x[i][j] * c[j] for i in range(ECNAMOUNT) for j in range(VNFAMOUNT)]
    )

    for i in range(ECNAMOUNT):
        for j in range(VNFAMOUNT):
            for k in range(USERAMOUNT):
                prob += y[i][j][k] <= x[i][j]

    for j in range(VNFAMOUNT):
        for k in range(USERAMOUNT):
            prob += pl.lpSum([y[i][j][k] for i in phi[k]]) == 0

    for j in range(VNFAMOUNT):
        prob += pl.lpSum([x[i][j] for i in range(ECNAMOUNT)]) <= 1

    for k in range(USERAMOUNT):
        prob += (
            pl.lpSum([y[i][j][k] for i in range(ECNAMOUNT) for j in range(VNFAMOUNT)])
            <= _K
        )

    for j in range(VNFAMOUNT):
        prob += (
            pl.lpSum([y[i][j][k] for i in range(ECNAMOUNT) for k in range(USERAMOUNT)])
            <= _P
        )
    for k in range(USERAMOUNT):
        prob += (
            pl.lpSum([y[i][j][k] for i in range(ECNAMOUNT) for j in range(VNFAMOUNT)])
            == 1
        )
    for i in range(ECNAMOUNT):
        prob += pl.lpSum([x[i][j] * p[j] for j in range(VNFAMOUNT)]) <= P[i]

    for j in range(VNFAMOUNT):
        prob += pl.lpSum([y[i][j][k] * t[k] for k in range(USERAMOUNT)]) <= p[j]

    prob.solve(pl.get_solver("CPLEX_PY"))
    print("objective =", pl.value(prob.objective))

    f = open(
        "../data/lp1_x_user_"
        + str(USERAMOUNT)
        + "_request_"
        + str(request_num)
        + "_k_"
        + str(_K)
        + "_p_"
        + str(_P),
        "w",
    )
    f.write(str(pl.value(prob.objective)) + "\n")
    for i in range(ECNAMOUNT):
        for j in range(VNFAMOUNT):
            f.write(str(pl.value(x[i][j])) + " ")
        f.write("\n")
    f.close()

    f = open(
        "../data/lp1_y_user_"
        + str(USERAMOUNT)
        + "_request_"
        + str(request_num)
        + "_k_"
        + str(_K)
        + "_p_"
        + str(_P),
        "w",
    )
    for i in range(ECNAMOUNT):
        for j in range(VNFAMOUNT):
            for k in range(USERAMOUNT):
                f.write(str(pl.value(y[i][j][k])) + " ")
            f.write("\n")
    f.close()

    xres = [[pl.value(x[i][j]) for j in range(VNFAMOUNT)] for i in range(ECNAMOUNT)]
    yres = [
        [[pl.value(y[i][j][k]) for k in range(USERAMOUNT)] for j in range(VNFAMOUNT)]
        for i in range(ECNAMOUNT)
    ]
    return xres, yres


def alg1(useramount, t, cost, ecn_capacity, vnf_capacity, x, y, K, P):
    ecnlist = [ECN.ecn(i, ecn_capacity[i]) for i in range(ECNAMOUNT)]

    if useramount == 1000:
        factor = 2
    else:
        factor = 6

    # step2: VNF placement
    placement_of_vnf = dict()
    placement_cost = 0
    set_of_placed_VNF = []

    t_sum = sum([t[k] for k in range(useramount)])
    k_b = math.ceil(t_sum / 1000)
    count = 0
    knapsack = []
    knapsack_pos = []
    for i in range(k_b):
        knapsack.append([])
        knapsack_pos.append([[], []])
    for j in range(VNFAMOUNT):
        for i in range(ECNAMOUNT):
            id = min_sum_id(k_b, knapsack)
            knapsack[id].append(x[i][j])
            knapsack_pos[id][0].append(i)
            knapsack_pos[id][1].append(j)

    for i in range(k_b):
        z_a = sum(knapsack[i])
        if z_a == 0:
            continue
        probabilityies = [knapsack[i][j] / z_a for j in range(len(knapsack[i]))]
        count = count + 1
        res = random_pick(knapsack[i], probabilityies)
        ecn_id = knapsack_pos[i][0][res]
        vnf_id = knapsack_pos[i][1][res]
        ecnlist[ecn_id].install_vnf(vnf_id, vnf_capacity[vnf_id])
        set_of_placed_VNF.append(vnf_id)
        placement_of_vnf[vnf_id] = ecn_id
        placement_cost = placement_cost + cost[vnf_id]

    for i in range(VNFAMOUNT):
        if i not in set_of_placed_VNF:
            for ecn in ecnlist:
                if x[ecn.get_id()][i] != 0:
                    ecn_id = ecnlist.index(ecn)
                    ecnlist[ecn_id].install_vnf(i, vnf_capacity[i])
                    set_of_placed_VNF.append(i)
                    placement_of_vnf[i] = ecn_id
                    placement_cost = placement_cost + cost[i]
                    break
    # step3: VNF assignment
    count_vnf = [0 for i in range(VNFAMOUNT)]
    vnf_assigment = []
    for k in range(useramount):
        candidate_vnfs_of_u = []
        k_ub = K
        vnfs_of_ub = [
            VNF.vnf(id=j, ecn=placement_of_vnf[j], value=y[placement_of_vnf[j]][j][k])
            for j in set_of_placed_VNF
        ]
        knapsack = []
        knapsack_pos = []
        for i in range(k_ub):
            knapsack.append([])
            knapsack_pos.append([])
        for v in vnfs_of_ub:
            id = min_sum_id(k_ub, knapsack)
            knapsack[id] = knapsack[id] + [v.get_value()]
            knapsack_pos[id].append(v.get_id())

        for i in range(k_ub):
            vnf_id = -1
            z_a = sum(knapsack[i])
            if z_a == 0:
                for j in set_of_placed_VNF:
                    if j not in candidate_vnfs_of_u and count_vnf[j] < P * factor:
                        vnf_id = j
                        break
            else:
                probabilityies = [
                    knapsack[i][j] / (z_a) for j in range(len(knapsack[i]))
                ]
                res = random_pick(knapsack[i], probabilityies)
                vnf_id = knapsack_pos[i][res]
            if count_vnf[vnf_id] < P * factor:
                count_vnf[vnf_id] = count_vnf[vnf_id] + 1
                candidate_vnfs_of_u.append(vnf_id)
        vnf_assigment.append(candidate_vnfs_of_u)

    print("placement cost=" + str(placement_cost))
    return placement_of_vnf, vnf_assigment


def alg2(epsilon, G, t, F, p, placement_of_vnf, useramount):
    phi = 1 / epsilon
    request_list = []
    id = 0
    for k in range(useramount):
        for timestamp, traffic in zip(t[k], G[k]):
            request_list.append(USER.request(id, 0, k, timestamp, traffic))
            id = id + 1
    request_list.sort()

    beta = [0 for i in range(VNFAMOUNT)]

    acc_num = 0
    throughput = 0
    total_num = len(request_list)
    for request in request_list:
        u = request.get_user()
        v_id = -1
        maxbeta = 1
        for v in F[u]:  # select min cost of candidate vnf of user u
            if beta[v] <= maxbeta:
                v_id = v
                maxbeta = beta[v]
        if v_id == -1:
            request.set_vnf(-1)
            continue

        acc_num = acc_num + 1
        throughput = throughput + request.get_traffic()
        request.set_vnf(v_id)
        request.set_ecn(placement_of_vnf[v_id])
        beta[v_id] = beta[v_id] * (
            1 + request.get_traffic() / p[v_id]
        ) + request.get_traffic() / (phi * p[v_id])

    print("accept rate= " + str(acc_num) + "/" + str(total_num))
    print("throughput= " + str(throughput))
    return throughput, request_list


def run_alg(useramount, request_num, K, P):
    if useramount == 1000:
        filerequest = 30

    else:
        filerequest = 50

    Gamma, traffic = USER.get_user_requests_traffic(
        "../data/user_" + str(useramount) + "_requests_" + str(filerequest),
        request_num,
        useramount,
    )
    timestamp = USER.get_user_requests_timestamp(
        "../data/user_" + str(useramount) + "_requests_" + str(filerequest),
        request_num,
        useramount,
    )

    vnf_cost = VNF.get_vnf_cost()
    ecn_capacity = ECN.get_ecn_capacity()
    vnf_capacity = VNF.get_vnf_process_demand()

    # x, y = solve_lp1(request_num, K, P)
    # just read results from files
    x, y = [], []
    f = open(
        "../data/lp1_x_user_"
        + str(useramount)
        + "_request_"
        + str(request_num)
        + "_k_"
        + str(K)
        + "_p_"
        + str(P),
        "r",
    )
    f.readline()  # skip line 1, objective

    for i in range(ECNAMOUNT):
        line = f.readline().split()
        x.append(list(map(float, line)))
    f.close()

    f = open(
        "../data/lp1_y_user_"
        + str(useramount)
        + "_request_"
        + str(request_num)
        + "_k_"
        + str(K)
        + "_p_"
        + str(P),
        "r",
    )
    for i in range(ECNAMOUNT):
        tmp = []
        for j in range(VNFAMOUNT):
            line = f.readline().split()
            tmp.append(list(map(float, line)))
        y.append(tmp)
    f.close()

    placement, vnf_assigment = alg1(
        useramount, traffic, vnf_cost, ecn_capacity, vnf_capacity, x, y, K, P
    )
    throughput, request_list = alg2(
        0.05, Gamma, timestamp, vnf_assigment, vnf_capacity, placement, useramount
    )

    # f = open("../data/myalg_requestscheduling_user_" + str(useramount) + "_request_" + str(request_num), 'w')
    # f1 = open("../data/myalg_testbed" + "_request_" + str(request_num), 'w')
    # for request in request_list:
    #     f.write(str(request.get_id()) + ' ' + str(request.get_user()) + ' ' + str(request.get_vnf()) + ' ' + str(
    #         request.get_traffic()) + '\n')
    #     f1.write(str(request.get_id()) + ' ' + str(request.get_user()) + ' ' + str(request.get_ecn()) + ' ' + str(
    #         request.get_traffic()) + '\n')
    # f1.close()
    # f.close()

    return throughput, request_list


if __name__ == "__main__":
    request_per_user = [10, 12, 14, 16, 18]

    plist = [[10, 12, 14, 16], [50, 60, 70, 80]]
    klist = [[6, 8, 10, 12], [10, 12, 14, 16]]

    for num in request_per_user:
        run_alg(20, num, kk, pp)
