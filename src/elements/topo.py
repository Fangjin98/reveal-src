import random
from constant import *
import math
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))


def user_not_in_area(x, y):
    for j in range(ECNAMOUNT):
        if math.sqrt(pow(x - ecnx[j], 2) + pow(y - ecny[j], 2)) <= ecnr:
            return False
    return True


def generate_user_pos(filename):
    file = open(filename, "w")
    for i in range(USERAMOUNT):
        userx = 0
        usery = 0
        while user_not_in_area(userx, usery):
            userx = random.randint(0, X)
            usery = random.randint(0, Y)
        file.write(str(i) + " " + str(userx) + " " + str(usery) + "\n")
    file.close()


def get_user_pos(filename, useramount=USERAMOUNT):
    file = open(filename, "r")
    user = dict()
    for i in range(useramount):
        line = file.readline().split()
        user[line[0]] = [int(line[1]), int(line[2])]
    file.close()
    return user


if __name__ == "__main__":
    generate_user_pos("../data/user_" + str(USERAMOUNT) + "_position")
