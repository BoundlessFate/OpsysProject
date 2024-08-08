import sys
import os
import math
letters = {0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z"}
# Process class to hopefully simplify all the logic in the algorithms
class process:

    def __init__(self, arrivalTime, id, cpuBound):
        self.arrivalTime = arrivalTime
        self.id = id
        self.cpuBound = cpuBound
        self.cpuBursts = []
        self.ioBursts = []
        self.blockingUntil = -1
    def addCPUBurst(self,time):
        self.cpuBursts.append(time)
    def addIOBurst(self,time):
        self.ioBursts.append(time)
    def removeCPUBurst(self):
        if len(self.cpuBursts) == 0:
            return -1
        firstIndex = self.cpuBursts[0]
        return self.cpuBursts.pop(0)
    def removeIOBurst(self):
        if len(self.ioBursts) == 0:
            return -1
        firstIndex = self.ioBursts[0]
        return self.ioBursts.pop(0)
    def getNumCPUBursts(self):
        return len(self.cpuBursts)
    def getNumIOBursts(self):
        return len(self.ioBursts)
    def getArrivalTime(self):
        return self.arrivalTime
    def getId(self):
        return letters[math.floor(self.id/10)]+str(self.id%10)
    def isCpuBound(self):
        return self.cpuBound
    def blockUntil(self, time):
        self.blockingUntil = time
    def getBlockUntil(self):
        return self.blockingUntil
    
def getQueueStr(queue):
    returnStr = "[Q"
    if len(queue) == 0:
        return returnStr + " empty]"
    for i in queue:
        returnStr += f" {i}"
    returnStr += "]"
    return returnStr
def getProcess(allProcesses, p):
    for i in allProcesses:
        if i.getId == p:
            return i

def fcfs(n, allProcesses, letters, tCs):
    time = 0
    readyQueue = []
    waitingOnIo = []
    numTerminated = 0
    cpuBusyUntil = -1
    curBursting = None
    context = 0
    print(f"time {time}ms: Simulator started for FCFS {getQueueStr(readyQueue)}")
    arrivalTimesSet = set()
    for i in allProcesses:
        arrivalTimesSet.add(i.getArrivalTime())
    while(numTerminated < len(allProcesses)):
        # If a new process is arriving at this time
        if time in arrivalTimesSet:
            # Append process to the ready queue
            count = 0
            while(allProcesses[count].getArrivalTime() != time):
                count += 1
            id = allProcesses[count].getId()
            readyQueue.append(id)
            print(f"time {time}ms: Process {id} added to ready queue {getQueueStr(readyQueue)}")
        justFinishedIo = []
        for i in waitingOnIo:
            if time <= i.getBlockUntil():
                justFinishedIo.append(i)
        for i in justFinishedIo:
            waitingOnIo.remove(i)
            readyQueue.append(i)
            print(f"time {time}ms: Process {i.getId()} completed I/O; added to ready queue {getQueueStr(readyQueue)}")


        if cpuBusyUntil <= time and context == 0:
            # If process is in action
            if (cpuBusyUntil != -1):
                cpuBusyUntil = -1
                if curBursting.getNumIOBursts == 0:
                    print(f"time {time}ms: Process {curBursting.getId()} terminated {getQueueStr(readyQueue)}")
                    numTerminated += 1
                    continue
                if (curBursting.getNumCPUBursts() == 1):
                    print(f"time {time}ms: Process {curBursting.getId()} completed a CPU burst; {curBursting.getNumCPUBursts()} burst to go {getQueueStr(readyQueue)}")
                else:
                    print(f"time {time}ms: Process {curBursting.getId()} completed a CPU burst; {curBursting.getNumCPUBursts()} bursts to go {getQueueStr(readyQueue)}")
                print(f"time {time}ms: Process {curBursting.getId()} switching out of CPU; blocking on I/O until time {curBursting.getBlockUntil()}ms {getQueueStr(readyQueue)}")
                context = tCs
                curBursting.blockUntil(time+curBursting.removeIOBurst())
                waitingOnIo.append(curBursting)
                continue
            if len(readyQueue) != 0:
                curBursting = readyQueue.pop(0)
                curTime = curBursting.removeCPUBurst()
                print(f"time {time}ms:Process {curBursting.getId()} started using the CPU for {curTime}ms burst {getQueueStr(readyQueue)}")
                cpuBusyUntil = time + curTime
        context -= 1
        time += 1

def partTwo(n, allProcesses, tCs, alpha, tSlice):


    print("\n<<< PROJECT PART II")
    print(f"<<< -- t_cs={tCs}ms; alpha={alpha:.2f}; t_slice={tSlice}ms")
    fcfs(n, allProcesses, letters, tCs)

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
#sys.stdout = open('stdout.txt', 'w')

numArgs = len(sys.argv)
if (numArgs < 9):
    sys.stderr.write("ERROR: wrong number of inputs given")
    sys.stderr.close() # Close not needed on submit
    os.abort()
    # python project.py 3 1 32 0.001 1024 4 0.75 256 > p2output02.txt
    # 3 - n
    # 1 - nCpu
    # 32 - seed
    # 0.001 - lmda
    # 1024 - upBound
    # 4 - tCs
    # 0.75 - alpha
    # 256 - tSlice
    # > p2output02.txt - piping output to a file
n = int(sys.argv[1])
nCpu = int(sys.argv[2])
seed = int(sys.argv[3])
lmda = float(sys.argv[4])
upBound = int(sys.argv[5])
tCs = int(sys.argv[6])
alpha = float(sys.argv[7])
tSlice = int(sys.argv[8])
if (n <= 0 or nCpu < 0 or seed < 0 or lmda <= 0 or upBound <= 0 or tCs <= 0 or (tCs%2 != 0) or alpha < 0 or alpha > 1 or tSlice <= 0):
    sys.stderr.write("ERROR: inputs do not fit bounds")
    os.abort()
rand = rand48()
rand.srand48(seed)
allProcesses = []
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
    newProcess = process(initProcessArrivalTime,i,i<nCpu)
    #3
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
        newProcess.addCPUBurst(CPUBurstTime)
        if IOBurstTime != 0:
            newProcess.addIOBurst(IOBurstTime)
    allProcesses.append(newProcess)

# Final outputs to terminal after everything is calculated
print("<<< PROJECT PART I")
if (nCpu == 1):
    print(f"<<< -- process set (n={n}) with 1 CPU-bound process")
else:
    print(f"<<< -- process set (n={n}) with {nCpu} CPU-bound processes")
print(f"<<< -- seed={seed}; lambda={lmda:.6f}; bound={upBound}")
for i in allProcesses:
    id = i.getId()
    if i.isCpuBound:
        if i.getNumCPUBursts() == 1:
            print(f"CPU-bound process {id}: arrival time {i.getArrivalTime()}ms; 1 CPU burst:")
        else:
            print(f"CPU-bound process {id}: arrival time {i.getArrivalTime()}ms; {i.getNumCPUBursts()} CPU bursts:")
    else:
        if i.getNumCPUBursts() == 1:
            print(f"I/O-bound process {id}: arrival time {i.getArrivalTime()}ms; 1 CPU burst:")
        else:
            print(f"I/O-bound process {id}: arrival time {i.getArrivalTime()}ms; {i.getNumCPUBursts()} CPU bursts:")
# SIMOUT STUFF FOR PART 1
f = open("simout.txt", "w")
f.write(f"-- number of processes: {n}\n")
f.write(f"-- number of CPU-bound processes: {nCpu}\n")
f.write(f"-- number of I/O-bound processes: {n-nCpu}\n")
if (totalNumCPUBurstsFromCPU == 0):
    f.write(f"-- CPU-bound average CPU burst time: {0:.3f} ms\n")
else:
    f.write(f"-- CPU-bound average CPU burst time: {math.ceil(cpuTotalCpu/totalNumCPUBurstsFromCPU*1000)/1000:.3f} ms\n")
if (totalNumCPUBurstsFromIO == 0):
    f.write(f"-- I/O-bound average CPU burst time: {0:.3f} ms\n")
else:
    f.write(f"-- I/O-bound average CPU burst time: {math.ceil(ioTotalCpu/totalNumCPUBurstsFromIO*1000)/1000:.3f} ms\n")
if (totalNumCPUBurstsFromCPU+totalNumCPUBurstsFromIO == 0):
    f.write(f"-- overall average CPU burst time: {0:.3f} ms\n")
else:
    f.write(f"-- overall average CPU burst time: {math.ceil((cpuTotalCpu+ioTotalCpu)/(totalNumCPUBurstsFromCPU+totalNumCPUBurstsFromIO)*1000)/1000:.3f} ms\n")
if totalNumIOBurstsFromCPU == 0:
    f.write(f"-- CPU-bound average I/O burst time: {0:.3f} ms\n")
else:
    f.write(f"-- CPU-bound average I/O burst time: {math.ceil(cpuTotalIO/totalNumIOBurstsFromCPU*1000)/1000:.3f} ms\n")
if totalNumIOBurstsFromIO == 0:
    f.write(f"-- I/O-bound average I/O burst time: {0:.3f} ms\n")
else:
    f.write(f"-- I/O-bound average I/O burst time: {math.ceil(ioTotalIO/totalNumIOBurstsFromIO*1000)/1000:.3f} ms\n")
if totalNumIOBurstsFromCPU+totalNumIOBurstsFromIO == 0:
    f.write(f"-- overall average I/O burst time: {0:.3f} ms")
else:
    f.write(f"-- overall average I/O burst time: {math.ceil((cpuTotalIO+ioTotalIO)/(totalNumIOBurstsFromCPU+totalNumIOBurstsFromIO)*1000)/1000:.3f} ms")
f.close()
partTwo(n, allProcesses, tCs, alpha, tSlice)