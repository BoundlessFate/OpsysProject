import sys
import os
import math

# My version of srand48 and drand48 according to man pages
class rand48:
    Xn = 0
    @classmethod
    def srand48(obj, seed):
        obj.Xn = (seed << 16) | 0x330E
    @classmethod
    def drand48(obj):
        # Weird psuedorandom magic
        a = 0x5DEECE66D
        c = 0xB
        # m = 2^48
        m = 2 << 47
        obj.Xn = (a*obj.Xn + c) % m
        # Return value from 0 to 1
        return obj.Xn/m
    
# Precondition: rand.srand48() has already been called
def next_exp(rand, lmda, upBound):
    num = -math.log(rand.drand48())/lmda
    if num > upBound:
        return upBound
    return num

# USE THIS CODE BELOW ONLY FOR TESTING!!! WILL REDIRECT STDERR
sys.stderr = open('err.txt', 'w')

numArgs = len(sys.argv)
if (numArgs != 6):
    sys.stderr.write("ERROR: wrong number of inputs given")
    sys.stderr.close() # Close not needed on submit
    os.abort()
n = int(sys.argv[1])
nCpu = int(sys.argv[2])
seed = int(sys.argv[3])
lmda = float(sys.argv[4])
upBound = int(sys.argv[5])
rand = rand48()
rand.srand48(seed)
arrivalTimes = []
CPUBurstTimes = []
IOBurstTimes = []
for i in range(0,n):
    initProcessArrivalTime = math.floor(next_exp(rand, lmda, upBound))
    numCPUBursts = math.ceil(rand.drand48() * 32)
    cburstTimes = []
    iburstTimes = []
    for j in range(0,numCPUBursts):
        CPUBurstTime = next_exp(rand, lmda, upBound) 
        IOBurstTime = 0
        if i < nCpu - 1:
            IOBurstTime = next_exp(rand, lmda, upBound)
        if i < nCpu:
            CPUBurstTime *= 4
        else:
            IOBurstTime = next_exp(rand, lmda, upBound)
            IOBurstTime *= 8
        cburstTimes.append(CPUBurstTime)
        IOBurstTime.append(IOBurstTime)
    arrivalTimes.append(initProcessArrivalTime)
    CPUBurstTimes.append(cburstTimes)
    IOBurstTime.append(iburstTimes)

