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
def next_exp():
    num = -math.log(rand.drand48())/lmda
    if num > upBound:
        return next_exp()
    return num

# USE THIS CODE BELOW ONLY FOR TESTING!!! WILL REDIRECT STDERR
#sys.stderr = open('err.txt', 'w')
sys.stdout = open('stdout.txt', 'w')

numArgs = len(sys.argv)
if (numArgs != 6):
    sys.stderr.write("ERROR: wrong number of inputs given")
   # sys.stderr.close() # Close not needed on submit
    os.abort()
n = int(sys.argv[1])
nCpu = int(sys.argv[2])
seed = int(sys.argv[3])
lmda = float(sys.argv[4])
upBound = int(sys.argv[5])
if (n <= 0 or nCpu <= 0 or seed <= 0 or lmda <= 0 or upBound <= 0):
    sys.stderr.write("ERROR: wrong number of inputs given")
    os.abort()
rand = rand48()
rand.srand48(seed)
arrivalTimes = []
CPUBurstTimes = []
IOBurstTimes = []
numCPUBurst = []
# total time spent doing io/cpu bursts for io/cpu bound processes
cpuTotalCpu = 0
ioTotalCpu = 0
cpuTotalIO = 0
ioTotalIO = 0
# Total number of bursts for io/cpu for io/cpu bound processes
totalNumCPUBurstsFromCPU = 0
totalNumIOBurstsFromCPU = 0
totalNumCPUBurstsFromIO = 0
totalNumIOBurstsFromIO = 0
#pseudo random numbers and predictability
# for each process
for i in range(0,n):
    #1
    initProcessArrivalTime = math.floor(next_exp())
    #2
    numCPUBursts = math.ceil(rand.drand48() * 32)
    numCPUBurst.append(numCPUBursts)
    #3
    cburstTimes = []
    iburstTimes = []
    # Add total num of bursts
    if i < nCpu:
        totalNumCPUBurstsFromCPU += numCPUBursts
        totalNumIOBurstsFromCPU += numCPUBursts - 1
    else:
        totalNumCPUBurstsFromIO += numCPUBursts
        totalNumIOBurstsFromIO += numCPUBursts - 1

    for j in range(0,numCPUBursts):
        CPUBurstTime = math.ceil(next_exp())
        IOBurstTime = 0
        # If not last burst, calculate a io burst time
        if j != numCPUBursts-1:
            IOBurstTime = math.ceil(next_exp())
        # CPU bound process
        if i < nCpu:
            CPUBurstTime *= 4
            cpuTotalCpu += CPUBurstTime
            cpuTotalIO += IOBurstTime
        # IO Bound process
        else:
            IOBurstTime *= 8
            ioTotalCpu += CPUBurstTime
            ioTotalIO += IOBurstTime
        cburstTimes.append(CPUBurstTime)
        iburstTimes.append(IOBurstTime)
    arrivalTimes.append(initProcessArrivalTime)
    CPUBurstTimes.append(cburstTimes)
    IOBurstTimes.append(iburstTimes)
letters = {0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z"}

# Final outputs to terminal after everything is calculated
print("<<< PROJECT PART I")
if (nCpu == 1):
    print(f"<<< -- process set (n={n}) with 1 CPU-bound process")
else:
    print(f"<<< -- process set (n={n}) with {nCpu} CPU-bound processes")
print(f"<<< -- seed={seed}; lambda={lmda:.6f}; bound={upBound}")
for i in range(0,len(arrivalTimes)):
    id = letters[math.floor(i/10)]+str(i%10)
    if i < nCpu:
        if numCPUBurst[i] == 1:
            print(f"CPU-bound process {id}: arrival time {arrivalTimes[i]}ms; 1 CPU burst:")
        else:
            print(f"CPU-bound process {id}: arrival time {arrivalTimes[i]}ms; {numCPUBurst[i]} CPU bursts:")
    else:
        if numCPUBurst[i] == 1:
            print(f"I/O-bound process {id}: arrival time {arrivalTimes[i]}ms; 1 CPU burst:")
        else:
            print(f"I/O-bound process {id}: arrival time {arrivalTimes[i]}ms; {numCPUBurst[i]} CPU bursts:")
    for j in range (0, len(CPUBurstTimes[i])):
        curStr = "==> CPU burst " + str(CPUBurstTimes[i][j]) + "ms"
        if (IOBurstTimes[i][j] != 0):
            curStr += " ==> I/O burst " + str(IOBurstTimes[i][j]) + "ms"
        print(curStr)
f = open("simout.txt", "w")
f.write(f"-- number of processes: {n}\n")
f.write(f"-- number of CPU-bound processes: {nCpu}\n")
f.write(f"-- number of I/O-bound processes: {n-nCpu}\n")
# Dont need to check these because num cpu bursts is ceiling
f.write(f"-- CPU-bound average CPU burst time: {math.ceil(cpuTotalCpu/totalNumCPUBurstsFromCPU*1000)/1000:.3f} ms\n")
f.write(f"-- I/O-bound average CPU burst time: {math.ceil(ioTotalCpu/totalNumCPUBurstsFromIO*1000)/1000:.3f} ms\n")
f.write(f"-- overall average CPU burst time: {math.ceil((cpuTotalCpu+ioTotalCpu)/(totalNumCPUBurstsFromCPU+totalNumCPUBurstsFromIO)*1000)/1000:.3f} ms\n")
# Need to check these because it is num cpu bursts - 1 so can be 0
if totalNumIOBurstsFromCPU == 0:
    f.write(f"-- CPU-bound average I/O burst time: {0:.3f} ms\n")
else:
    f.write(f"-- CPU-bound average I/O burst time: {math.ceil(cpuTotalIO/totalNumIOBurstsFromCPU*1000)/1000:.3f} ms\n")
if totalNumIOBurstsFromIO == 0:
    f.write(f"-- I/O-bound average I/O burst time: {0:.3f} ms\n")
else:
    f.write(f"-- I/O-bound average I/O burst time: {math.ceil(ioTotalIO/totalNumIOBurstsFromIO*1000)/1000:.3f} ms\n")
# Dont need to check because works with ceiling function to be at min 1
f.write(f"-- overall average I/O burst time: {math.ceil((cpuTotalIO+ioTotalIO)/(totalNumIOBurstsFromCPU+totalNumIOBurstsFromIO)*1000)/1000:.3f} ms")
f.close()
sys.stdout.close()