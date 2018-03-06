# coding UTF-8
# start with standard Producer/Consumer Threading Pattern

import Queue
from multiprocessing import Pool
#  start really simple
def job(x):
    return x*x
def multi():
    p = Pool(8)
    res = p.map(job, range(655355))
    print res

if __name__ == '__main__':
    multi()