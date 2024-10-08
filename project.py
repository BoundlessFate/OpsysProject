import sys
import os
import math
import copy
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
        self.burstTime = -1
    def addCPUBurst(self,time):
        self.cpuBursts.append(time)
    def addIOBurst(self,time):
        self.ioBursts.append(time)
    def removeCPUBurst(self):
        if len(self.cpuBursts) == 0:
            return -1
        firstIndex = self.cpuBursts[0]
        # If process hasnt been preempted, set the total time for the burst
        if self.burstTime == -1:
            self.burstTime = firstIndex
        return self.cpuBursts.pop(0)
    def removeIOBurst(self):
        if len(self.ioBursts) == 0:
            return -1
        self.burstTime = -1
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
    def getTimeForBurst(self):
        return self.burstTime
    def addBurstToFront(self, time):
        self.cpuBursts.insert(0, time)
        # If no time was removed while running, dont claim the process has run at all yet
        if (time == self.burstTime):
            self.burstTime = -1

class ContextSwitch:
    def __init__(self, cSt):
        self.cSt = int(cSt/2)
        self.timeExit = -1
        # Variable to check if one was recently completed
        self.completed = False
    def start(self, time):
        # Dont start it again if the current context switch hasnt finished
        if (self.timeExit > time):
            return
        self.completed = False
        self.timeExit = time+self.cSt
    def checkActive(self, curTime):
        if self.timeExit == -1:
            return False
        if (curTime >= self.timeExit):
            self.completed = True
            return False
        return True
    def getCompleted(self):
        return self.completed
    def reset(self):
        self.completed = False
        self.timeExit = -1

class CPU:
    def __init__(self, cSt):
        self.curBursting = None
        self.burstUntil = -1
        self.context = ContextSwitch(cSt)
    def burstCPU(self, process, time):
        self.curBursting = process
        self.burstUntil = time
    def startContextSwitch(self, time):
        self.context.start(time)
    def switchActive(self, time):
        return self.context.checkActive(time)
    def switchCompleted(self, time):
        self.context.checkActive(time)
        return self.context.getCompleted()
    def isBursting(self, time):
        return self.burstUntil > time
    def processInCPU(self):
        return self.curBursting != None
    def justFinishedBursting(self, time):
        return self.burstUntil == time
    def getProcess(self):
        return self.curBursting
    def stopBurst(self):
        self.curBursting = None
        self.burstUntil = -1
    def resetSwitch(self):
        self.context.reset()
    def getBurstUntil(self):
        return self.burstUntil

def getQueueStr(queue):
    returnStr = "[Q"
    if len(queue) == 0:
        return returnStr + " empty]"
    for i in queue:
        returnStr += f" {i.getId()}"
    returnStr += "]"
    return returnStr
# ----------------------- PT2 SIMOUT HANDLER ---------------------------------
def handleSimout(algorithm, totalTime, cpuUtilizedTime, cpuWaitTotal, ioWaitTotal, cpuTurnaroundTotal, ioTurnaroundTotal, cpuContext, ioContext, cpuPreemptions, ioPreemptions):
    f = open("simout.txt", "a")
    f.write(f"\nAlgorithm {algorithm}\n")
    f.write(f"-- CPU utilization: {math.ceil((cpuUtilizedTime/totalTime)*100*1000)/1000:.3f}%\n")
    if cpuContext == 0:
        f.write(f"-- CPU-bound average wait time: {0:.3f} ms\n")
    else:
        f.write(f"-- CPU-bound average wait time: {math.ceil(cpuWaitTotal/cpuContext*1000)/1000:.3f} ms\n")
    if ioContext == 0:
        f.write(f"-- I/O-bound average wait time: {0:.3f} ms\n")
    else:
        f.write(f"-- I/O-bound average wait time: {math.ceil(ioWaitTotal/ioContext*1000)/1000:.3f} ms\n")
    if cpuContext+ioContext == 0:
        f.write(f"-- CPU-bound average wait time: {0:.3f} ms\n")
    else:
        f.write(f"-- overall average wait time: {math.ceil((cpuWaitTotal+ioWaitTotal)/(cpuContext+ioContext)*1000)/1000:.3f} ms\n")
    if cpuContext == 0:
        f.write(f"-- CPU-bound average turnaround time: {0:.3f} ms\n")
    else:
        f.write(f"-- CPU-bound average turnaround time: {math.ceil(cpuTurnaroundTotal/cpuContext*1000)/1000:.3f} ms\n")
    if ioContext == 0:
        f.write(f"-- I/O-bound average turnaround time: {0:.3f} ms\n")
    else:
        f.write(f"-- I/O-bound average turnaround time: {math.ceil(ioTurnaroundTotal/ioContext*1000)/1000:.3f} ms\n")
    if cpuContext+ioContext == 0:
        f.write(f"-- CPU-bound average turnaround time: {0:.3f} ms\n")
    else:
        f.write(f"-- overall average turnaround time: {math.ceil((cpuTurnaroundTotal+ioTurnaroundTotal)/(cpuContext+ioContext)*1000)/1000:.3f} ms\n")
    f.write(f"-- CPU-bound number of context switches: {cpuContext}\n")
    f.write(f"-- I/O-bound number of context switches: {ioContext}\n")
    f.write(f"-- overall number of context switches: {cpuContext+ioContext}\n")
    f.write(f"-- CPU-bound number of preemptions: {cpuPreemptions}\n")
    f.write(f"-- I/O-bound number of preemptions: {ioPreemptions}\n")
    f.write(f"-- overall number of preemptions: {cpuPreemptions+ioPreemptions}\n")
    f.close()
def rrExtraSimout(cpuCompletedOneSlice, ioCompletedOneSlice, nCpuBound, nIoBound):
    f = open("simout.txt", "a")
    if nCpuBound == 0:
        f.write(f"-- CPU-bound percentage of CPU bursts completed within one time slice: {0:.3f}%\n")
    else:
        f.write(f"-- CPU-bound percentage of CPU bursts completed within one time slice: {math.ceil((cpuCompletedOneSlice/nCpuBound)*100*1000)/1000:.3f}%\n")
    if nIoBound == 0:
        f.write(f"-- I/O-bound percentage of CPU bursts completed within one time slice: {0:.3f}%\n")
    else:
        f.write(f"-- I/O-bound percentage of CPU bursts completed within one time slice: {math.ceil((ioCompletedOneSlice/nIoBound)*100*1000)/1000:.3f}%\n")
    if nCpuBound+nIoBound == 0:
        f.write(f"-- overall percentage of CPU bursts completed within one time slice: {0:.3f}%")
    else:
        f.write(f"-- overall percentage of CPU bursts completed within one time slice: {math.ceil(((cpuCompletedOneSlice+ioCompletedOneSlice)/(nCpuBound+nIoBound))*100*1000)/1000:.3f}%")
    f.close()
# Different because of preemptions with srt
def handleSimoutTwo(algorithm, totalTime, cpuUtilizedTime, cpuWaitTotal, ioWaitTotal, cpuTurnaroundTotal, ioTurnaroundTotal, cpuContext, ioContext, cpuPreemptions, ioPreemptions, numCPUBurst, numIOBurst):
    f = open("simout.txt", "a")
    f.write(f"\nAlgorithm {algorithm}\n")
    f.write(f"-- CPU utilization: {math.ceil((cpuUtilizedTime/totalTime)*100*1000)/1000:.3f}%\n")
    if cpuContext == 0:
        f.write(f"-- CPU-bound average wait time: {0:.3f} ms\n")
    else:
        f.write(f"-- CPU-bound average wait time: {math.ceil(cpuWaitTotal/numCPUBurst*1000)/1000:.3f} ms\n")
    if ioContext == 0:
        f.write(f"-- I/O-bound average wait time: {0:.3f} ms\n")
    else:
        f.write(f"-- I/O-bound average wait time: {math.ceil(ioWaitTotal/numIOBurst*1000)/1000:.3f} ms\n")
    if cpuContext+ioContext == 0:
        f.write(f"-- CPU-bound average wait time: {0:.3f} ms\n")
    else:
        f.write(f"-- overall average wait time: {math.ceil((cpuWaitTotal+ioWaitTotal)/(numCPUBurst+numIOBurst)*1000)/1000:.3f} ms\n")
    if numCPUBurst == 0:
        f.write(f"-- CPU-bound average turnaround time: {0:.3f} ms\n")
    else:
        f.write(f"-- CPU-bound average turnaround time: {math.ceil((cpuTurnaroundTotal/numCPUBurst)*1000)/1000:.3f} ms\n")
    if numIOBurst == 0:
        f.write(f"-- I/O-bound average turnaround time: {0:.3f} ms\n")
    else:
        f.write(f"-- I/O-bound average turnaround time: {math.ceil((ioTurnaroundTotal/numIOBurst)*1000)/1000:.3f} ms\n")
    if numCPUBurst+numIOBurst == 0:
        f.write(f"-- CPU-bound average turnaround time: {0:.3f} ms\n")
    else:
        f.write(f"-- overall average turnaround time: {math.ceil(((cpuTurnaroundTotal+ioTurnaroundTotal)/(numCPUBurst+numIOBurst))*1000)/1000:.3f} ms\n")
    f.write(f"-- CPU-bound number of context switches: {cpuContext}\n")
    f.write(f"-- I/O-bound number of context switches: {ioContext}\n")
    f.write(f"-- overall number of context switches: {cpuContext+ioContext}\n")
    f.write(f"-- CPU-bound number of preemptions: {cpuPreemptions}\n")
    f.write(f"-- I/O-bound number of preemptions: {ioPreemptions}\n")
    f.write(f"-- overall number of preemptions: {cpuPreemptions+ioPreemptions}\n")
    f.close()

# ------------------------------------------------------------ FCFS ALGORITHM -------------------------------------------------
def fcfs(n, allProcesses, tCs):
    cpuUtilizedTime=0
    cpuWaitTotal = 0 
    ioWaitTotal = 0
    cpuTurnaroundTotal = 0
    ioTurnaroundTotal = 0
    cpuStillRunning = 0
    ioStillRunning = 0
    cpuContext = 0
    ioContext = 0
    time = 0
    readyQueue = []
    waitingOnIo = []
    numTerminated = 0
    cpu = CPU(tCs)
    enteringCPU = None
    print(f"time {time}ms: Simulator started for FCFS {getQueueStr(readyQueue)}")
    arrivalTimesSet = set()
    for i in allProcesses:
        arrivalTimesSet.add(i.getArrivalTime())
    while(numTerminated < len(allProcesses) or not cpu.switchCompleted(time)):
        # CASE: CPU Burst Completion
        if (cpu.justFinishedBursting(time) and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            curBursting = cpu.getProcess()
            # End of process
            if curBursting.getNumIOBursts() == 0:
                print(f"time {time}ms: Process {curBursting.getId()} terminated {getQueueStr(readyQueue)}")
                if curBursting.isCpuBound():
                    cpuStillRunning -= 1
                else:
                    ioStillRunning -= 1
                numTerminated += 1
            # More to the process
            else:
                if (time <= 9999):
                    if (curBursting.getNumCPUBursts() == 1):
                        print(f"time {time}ms: Process {curBursting.getId()} completed a CPU burst; {curBursting.getNumCPUBursts()} burst to go {getQueueStr(readyQueue)}")
                    else:
                        print(f"time {time}ms: Process {curBursting.getId()} completed a CPU burst; {curBursting.getNumCPUBursts()} bursts to go {getQueueStr(readyQueue)}")
                curBursting.blockUntil(time+curBursting.removeIOBurst()+int(tCs/2))
                if (time <= 9999):
                    print(f"time {time}ms: Process {curBursting.getId()} switching out of CPU; blocking on I/O until time {curBursting.getBlockUntil()}ms {getQueueStr(readyQueue)}")
                waitingOnIo.append(curBursting)
        # CASE: Process Starts Using The CPU
        if (not cpu.processInCPU() and cpu.switchCompleted(time)):
                cpu.resetSwitch()
                # Was popped during the start of the context switch, so doesnt need to be popped again
                curBursting = enteringCPU
                curTime = curBursting.removeCPUBurst()
                if (time <= 9999):
                    print(f"time {time}ms: Process {curBursting.getId()} started using the CPU for {curTime}ms burst {getQueueStr(readyQueue)}")
                if curBursting.isCpuBound():
                    cpuContext += 1
                else:
                    ioContext += 1
                cpu.burstCPU(curBursting, time+curTime)
        # CONTEXT SWITCHES
        # Actions after leaving cpu context switch ends
        if (cpu.processInCPU() and cpu.switchCompleted(time)):
            cpu.stopBurst()
            cpu.resetSwitch()
        # CASE: I/O Burst Completions
        justFinishedIo = []
        for i in waitingOnIo:
            if time >= i.getBlockUntil():
                justFinishedIo.append(i)
        justFinishedIo = sorted(justFinishedIo, key=lambda p: (p.getId()))
        for i in justFinishedIo:
            waitingOnIo.remove(i)
            readyQueue.append(i)
            if (time <= 9999):
                print(f"time {time}ms: Process {i.getId()} completed I/O; added to ready queue {getQueueStr(readyQueue)}")
        # CASE: New Process Arrivals
        if time in arrivalTimesSet:
            # Append process to the ready queue
            for i in allProcesses:
                if i.getArrivalTime() == time:
                    readyQueue.append(i)
                    if (time <= 9999):
                        print(f"time {time}ms: Process {i.getId()} arrived; added to ready queue {getQueueStr(readyQueue)}")
                    if i.isCpuBound():
                        cpuStillRunning += 1
                    else:
                        ioStillRunning += 1
        # MORE CONTEXT SWITCHES
        # Actions to start context switch for entering cpu
        if (not cpu.processInCPU() and len(readyQueue) != 0 and not cpu.switchActive(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            enteringCPU = readyQueue.pop(0)
        if (cpu.processInCPU() and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            cpuUtilizedTime += 1
        for i in readyQueue:
            if i.isCpuBound():
                cpuWaitTotal += 1
            else:
                ioWaitTotal += 1
        for i in waitingOnIo:
            if i.isCpuBound():
                cpuTurnaroundTotal -= 1
            else:
                ioTurnaroundTotal -= 1
        cpuTurnaroundTotal += cpuStillRunning
        ioTurnaroundTotal += ioStillRunning
        time += 1
    print(f"time {time}ms: Simulator ended for FCFS {getQueueStr(readyQueue)}")
    cpuTurnaroundTotal += 2*cpuContext
    ioTurnaroundTotal += 2*ioContext
    handleSimout("FCFS", time, cpuUtilizedTime, cpuWaitTotal, ioWaitTotal, cpuTurnaroundTotal, ioTurnaroundTotal, cpuContext, ioContext, 0, 0)

# ---------------------------------------- SJF ALGORITHM ---------------------------------------------------
def sjf(n, allProcesses, tCs, alpha, lmda):
    cpuUtilizedTime=0
    cpuWaitTotal = 0 
    ioWaitTotal = 0
    cpuTurnaroundTotal = 0
    ioTurnaroundTotal = 0
    cpuStillRunning = 0
    ioStillRunning = 0
    cpuContext = 0
    ioContext = 0
    time = 0
    readyQueue = []
    waitingOnIo = []
    numTerminated = 0
    processTau = dict()
    cpu = CPU(tCs)
    enteringCPU = None
    print(f"time {time}ms: Simulator started for SJF {getQueueStr(readyQueue)}")
    arrivalTimesSet = set()
    # Create set of all arrival times and add processes to tao dict
    for i in allProcesses:
        arrivalTimesSet.add(i.getArrivalTime())
        processTau[i.getId()] = math.ceil(1/lmda)
    while(numTerminated < len(allProcesses) or not cpu.switchCompleted(time)):
        # CASE: CPU Burst Completion
        if (cpu.justFinishedBursting(time) and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            curBursting = cpu.getProcess()
            # End of process
            if curBursting.getNumIOBursts() == 0:
                print(f"time {time}ms: Process {curBursting.getId()} terminated {getQueueStr(readyQueue)}")
                if curBursting.isCpuBound():
                    cpuStillRunning -= 1
                else:
                    ioStillRunning -= 1
                numTerminated += 1
            # More to the process
            else:
                if (time <= 9999):
                    if (curBursting.getNumCPUBursts() == 1):
                        print(f"time {time}ms: Process {curBursting.getId()} (tau {processTau[curBursting.getId()]}ms) completed a CPU burst; {curBursting.getNumCPUBursts()} burst to go {getQueueStr(readyQueue)}")
                    else:
                        print(f"time {time}ms: Process {curBursting.getId()} (tau {processTau[curBursting.getId()]}ms) completed a CPU burst; {curBursting.getNumCPUBursts()} bursts to go {getQueueStr(readyQueue)}")
                # Recalculate Tau for next use
                oldTau = processTau[curBursting.getId()]
                processTau[curBursting.getId()] = math.ceil(alpha * (curBursting.getTimeForBurst()) + (1-alpha) * processTau[curBursting.getId()])
                if (time <= 9999):
                    print(f"time {time}ms: Recalculated tau for process {curBursting.getId()}: old tau {oldTau}ms ==> new tau {processTau[curBursting.getId()]}ms {getQueueStr(readyQueue)}")
                curBursting.blockUntil(time+curBursting.removeIOBurst()+int(tCs/2))
                if (time <= 9999):
                    print(f"time {time}ms: Process {curBursting.getId()} switching out of CPU; blocking on I/O until time {curBursting.getBlockUntil()}ms {getQueueStr(readyQueue)}")
                waitingOnIo.append(curBursting)
        # CASE: Process Starts Using The CPU
        if (not cpu.processInCPU() and cpu.switchCompleted(time)):
                cpu.resetSwitch()
                # Was popped during the start of the context switch, so doesnt need to be popped again
                curBursting = enteringCPU
                curTime = curBursting.removeCPUBurst()
                if (time <= 9999):
                    print(f"time {time}ms: Process {curBursting.getId()} (tau {processTau[curBursting.getId()]}ms) started using the CPU for {curTime}ms burst {getQueueStr(readyQueue)}")
                cpu.burstCPU(curBursting, time+curTime)
                if curBursting.isCpuBound():
                    cpuContext += 1
                else:
                    ioContext += 1
        # CONTEXT SWITCHES
        # Actions after leaving cpu context switch ends
        if (cpu.processInCPU() and cpu.switchCompleted(time)):
            cpu.stopBurst()
            cpu.resetSwitch()
        # CASE: I/O Burst Completions
        justFinishedIo = []
        for i in waitingOnIo:
            if time >= i.getBlockUntil():
                justFinishedIo.append(i)
        justFinishedIo = sorted(justFinishedIo, key=lambda p: (p.getId()))
        for i in justFinishedIo:
            waitingOnIo.remove(i)
            readyQueue.append(i)
            readyQueue = sorted(readyQueue, key=lambda p: (processTau[p.getId()], p.getId()))
            if (time <= 9999):
                print(f"time {time}ms: Process {i.getId()} (tau {processTau[i.getId()]}ms) completed I/O; added to ready queue {getQueueStr(readyQueue)}")
        # CASE: New Process Arrivals
        if time in arrivalTimesSet:
            # Append process to the ready queue
            for i in allProcesses:
                if i.getArrivalTime() == time:
                    readyQueue.append(i)
                    readyQueue = sorted(readyQueue, key=lambda p: (processTau[p.getId()], p.getId()))
                    if (time <= 9999):
                        print(f"time {time}ms: Process {i.getId()} (tau {processTau[i.getId()]}ms) arrived; added to ready queue {getQueueStr(readyQueue)}")
                    if i.isCpuBound():
                        cpuStillRunning += 1
                    else:
                        ioStillRunning += 1
        # MORE CONTEXT SWITCHES
        # Actions to start context switch for entering cpu
        if (not cpu.processInCPU() and len(readyQueue) != 0 and not cpu.switchActive(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            enteringCPU = readyQueue.pop(0)
        if (cpu.processInCPU() and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            cpuUtilizedTime += 1
        for i in readyQueue:
            if i.isCpuBound():
                cpuWaitTotal += 1
            else:
                ioWaitTotal += 1
        for i in waitingOnIo:
            if i.isCpuBound():
                cpuTurnaroundTotal -= 1
            else:
                ioTurnaroundTotal -= 1
        cpuTurnaroundTotal += cpuStillRunning
        ioTurnaroundTotal += ioStillRunning
        time += 1
    print(f"time {time}ms: Simulator ended for SJF {getQueueStr(readyQueue)}")
    cpuTurnaroundTotal += 2*cpuContext
    ioTurnaroundTotal += 2*ioContext
    handleSimout("SJF", time, cpuUtilizedTime, cpuWaitTotal, ioWaitTotal, cpuTurnaroundTotal, ioTurnaroundTotal, cpuContext, ioContext, 0, 0)

# ---------------------------------------- SRT ALGORITHM ---------------------------------------------------
def remainingTime(remaining, start, now):
    return remaining-(now-start)
def srt(n, allProcesses, tCs, alpha, lmda):
    cpuWaitTotal = 0
    ioWaitTotal = 0
    cpuPreemptions = 0
    ioPreemptions = 0
    numCPUBursts=0
    numIOBursts = 0
    cpuUsageTotal = 0
    ioUsageTotal = 0
    cpuUtilizedTime=0
    cpuTurnaroundTotal = 0
    ioTurnaroundTotal = 0
    cpuStillRunning = 0
    ioStillRunning = 0
    cpuContext = 0
    ioContext = 0
    time = 0
    readyQueue = []
    waitingOnIo = []
    numTerminated = 0
    processTau = dict()
    processRemaining = dict()
    cpu = CPU(tCs)
    enteringCPU = None
    processInitTime = 0
    preempted = False
    print(f"time {time}ms: Simulator started for SRT {getQueueStr(readyQueue)}")
    arrivalTimesSet = set()
    # Create set of all arrival times and add processes to tao dict
    for i in allProcesses:
        arrivalTimesSet.add(i.getArrivalTime())
        processTau[i.getId()] = math.ceil(1/lmda)
        processRemaining[i.getId()] = math.ceil(1/lmda)
        if i.isCpuBound():
            numCPUBursts += i.getNumCPUBursts()
        else:
            numIOBursts += i.getNumCPUBursts()
    while(numTerminated < len(allProcesses) or not cpu.switchCompleted(time)):
        # CASE: CPU Burst Completion
        if (cpu.justFinishedBursting(time) and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            curBursting = cpu.getProcess()
            # End of process
            if curBursting.getNumIOBursts() == 0:
                print(f"time {time}ms: Process {curBursting.getId()} terminated {getQueueStr(readyQueue)}")
                numTerminated += 1
                if curBursting.isCpuBound():
                    cpuStillRunning -= 1
                else:
                    ioStillRunning -= 1
            # More to the process
            else:
                if (time <= 9999):
                    if (curBursting.getNumCPUBursts() == 1):
                        print(f"time {time}ms: Process {curBursting.getId()} (tau {processTau[curBursting.getId()]}ms) completed a CPU burst; {curBursting.getNumCPUBursts()} burst to go {getQueueStr(readyQueue)}")
                    else:
                        print(f"time {time}ms: Process {curBursting.getId()} (tau {processTau[curBursting.getId()]}ms) completed a CPU burst; {curBursting.getNumCPUBursts()} bursts to go {getQueueStr(readyQueue)}")
                # Recalculate Tau for next use
                oldTau = processTau[curBursting.getId()]
                processTau[curBursting.getId()] = math.ceil(alpha * (curBursting.getTimeForBurst()) + (1-alpha) * processTau[curBursting.getId()])
                processRemaining[curBursting.getId()] = processTau[curBursting.getId()]
                if (time <= 9999):
                    print(f"time {time}ms: Recalculated tau for process {curBursting.getId()}: old tau {oldTau}ms ==> new tau {processTau[curBursting.getId()]}ms {getQueueStr(readyQueue)}")
                curBursting.blockUntil(time+curBursting.removeIOBurst()+int(tCs/2))
                if (time <= 9999):
                    print(f"time {time}ms: Process {curBursting.getId()} switching out of CPU; blocking on I/O until time {curBursting.getBlockUntil()}ms {getQueueStr(readyQueue)}")
                waitingOnIo.append(curBursting)
        # CASE: Process Starts Using The CPU
        if (not cpu.processInCPU() and cpu.switchCompleted(time)):
                cpu.resetSwitch()
                curBursting = enteringCPU
                enteringCPU = None
                curTime = None
                if (curBursting.getTimeForBurst() != -1):
                    curTime = curBursting.removeCPUBurst()
                    if (time <= 9999):
                        print(f"time {time}ms: Process {curBursting.getId()} (tau {processTau[curBursting.getId()]}ms) started using the CPU for remaining {curTime}ms of {curBursting.getTimeForBurst()}ms burst {getQueueStr(readyQueue)}")
                else:
                    curTime = curBursting.removeCPUBurst()
                    if (time <= 9999):
                        print(f"time {time}ms: Process {curBursting.getId()} (tau {processTau[curBursting.getId()]}ms) started using the CPU for {curTime}ms burst {getQueueStr(readyQueue)}")
                cpu.burstCPU(curBursting, time+curTime)
                if curBursting.isCpuBound():
                    cpuContext += 1
                else:
                    ioContext += 1
                # Set the initial time for the running process to get the difference later for time spent
                processInitTime = time
        # CASE: WEIRD EDGE CASE PREEMPTION
        curBursting = cpu.getProcess()
        if not preempted and curBursting and len(readyQueue) != 0 and processRemaining[readyQueue[0].getId()] < remainingTime(processRemaining[curBursting.getId()], processInitTime, time) and curBursting.getTimeForBurst()+processInitTime-time > 0:
                if (time <= 9999):
                    print(f"time {time}ms: Process {readyQueue[0].getId()} (tau {processTau[readyQueue[0].getId()]}ms) will preempt {curBursting.getId()} {getQueueStr(readyQueue)}")
                processRemaining[curBursting.getId()] = remainingTime(processRemaining[curBursting.getId()], processInitTime, time)
                curBursting.addBurstToFront(cpu.getBurstUntil()-time)
                cpu.startContextSwitch(time)
                preempted = True
        # CASE: I/O Burst Completions
        justFinishedIo = []
        for i in waitingOnIo:
            if time >= i.getBlockUntil():
                justFinishedIo.append(i)
        justFinishedIo = sorted(justFinishedIo, key=lambda p: (p.getId()))
        curBursting = cpu.getProcess()
        for i in justFinishedIo:
            waitingOnIo.remove(i)
            # Before appending this, cur process running will be the shortest remaining
            # If this new process is shorter than cur process it will be inherently be in the start of the queue
            # Preempt if this scary looking expression is true
            # If currently bursting something on the cpu
            # and if the process just added to the queue is hass less estimated time than the estimated remaining time of the process in the cpu
            # and the cpu process doesnt have 0 time remaining
            readyQueue.append(i)
            readyQueue = sorted(readyQueue, key=lambda p: (processRemaining[p.getId()], p.getId()))
            if not preempted and curBursting and processRemaining[i.getId()] < remainingTime(processRemaining[curBursting.getId()], processInitTime, time) and curBursting.getTimeForBurst()+processInitTime-time > 0:
                if (time <= 9999):
                    print(f"time {time}ms: Process {i.getId()} (tau {processTau[i.getId()]}ms) completed I/O; preempting {curBursting.getId()} (predicted remaining time {remainingTime(processRemaining[curBursting.getId()], processInitTime, time)}ms) {getQueueStr(readyQueue)}")
                # Set remaining time for currently bursting process and add back to ready queue
                processRemaining[curBursting.getId()] = remainingTime(processRemaining[curBursting.getId()], processInitTime, time)
                curBursting.addBurstToFront(cpu.getBurstUntil()-time)
                cpu.startContextSwitch(time)
                preempted = True
            else:
                if (time <= 9999):
                    print(f"time {time}ms: Process {i.getId()} (tau {processTau[i.getId()]}ms) completed I/O; added to ready queue {getQueueStr(readyQueue)}")
        # CASE: New Process Arrivals
        if time in arrivalTimesSet:
            # Append process to the ready queue
            for i in allProcesses:
                if i.getArrivalTime() == time:
                    readyQueue.append(i)
                    readyQueue = sorted(readyQueue, key=lambda p: (processTau[p.getId()], p.getId()))
                    # Before appending this, cur process running will be the shortest remaining
                    # If this new process is shorter than cur process it will be inherently be in the start of the queue
                    # Preempt if this scary looking expression is true
                    # If currently bursting something on the cpu
                    # and if the process just added to the queue is hass less estimated time than the estimated remaining time of the process in the cpu
                    # and the cpu process doesnt have 0 time remaining
                    curBursting = cpu.getProcess()
                    if not preempted and curBursting and processRemaining[readyQueue[0].getId()] < remainingTime(processRemaining[curBursting.getId()], processInitTime, time) and curBursting.getTimeForBurst()+processInitTime-time > 0:
                        rem = remainingTime(processRemaining[curBursting.getId(), processInitTime, time])
                        if (time <= 9999):
                            print(f"time {time}ms: Process {i.getId()} (tau {processTau[i.getId()]}ms) arrived; preempting {curBursting.getId()} (predicted remaining time {rem}ms) {getQueueStr(readyQueue)}")
                        # Set remaining time for currently bursting process and add back to ready queue
                        processRemaining[curBursting.getId()] = rem
                        curBursting.addBurstToFront(cpu.getBurstUntil()-time)
                        cpu.startContextSwitch(time)
                        preempted = True
                    else:
                        if (time <= 9999):
                            print(f"time {time}ms: Process {i.getId()} (tau {processTau[i.getId()]}ms) arrived; added to ready queue {getQueueStr(readyQueue)}")
                    if i.isCpuBound():
                        cpuStillRunning += 1
                    else:
                        ioStillRunning += 1
        # CONTEXT SWITCHES
        # Actions after leaving cpu context switch ends
        if (cpu.processInCPU() and cpu.switchCompleted(time)):
            if preempted:
                if cpu.getProcess().isCpuBound():
                    cpuPreemptions += 1
                else:
                    ioPreemptions += 1
                readyQueue.append(cpu.getProcess())
                readyQueue = sorted(readyQueue, key=lambda p: (processRemaining[p.getId()], p.getId()))
                preempted = False
            cpu.stopBurst()
            cpu.resetSwitch()
        # MORE CONTEXT SWITCHES
        # Actions to start context switch for entering cpu
        if (not cpu.processInCPU() and len(readyQueue) != 0 and not cpu.switchActive(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            enteringCPU = readyQueue.pop(0)
        if (cpu.processInCPU() and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            cpuUtilizedTime += 1
            if cpu.getProcess().isCpuBound():
                cpuUsageTotal += 1
            else:
                ioUsageTotal += 1
        for i in readyQueue:
            if i.isCpuBound():
                cpuWaitTotal += 1
            else:
                ioWaitTotal += 1
        for i in waitingOnIo:
            if i.isCpuBound():
                cpuTurnaroundTotal -= 1
            else:
                ioTurnaroundTotal -= 1
        cpuTurnaroundTotal += cpuStillRunning
        ioTurnaroundTotal += ioStillRunning
        time += 1
    print(f"time {time}ms: Simulator ended for SRT {getQueueStr(readyQueue)}")
    cpuWaitTotal = cpuTurnaroundTotal-cpuUsageTotal-2*(cpuContext+cpuPreemptions)
    ioWaitTotal = ioTurnaroundTotal-ioUsageTotal-2*(ioContext+ioPreemptions)
    cpuTurnaroundTotal += 2*cpuContext - cpuPreemptions*2
    ioTurnaroundTotal += 2*ioContext - ioPreemptions*2
    handleSimoutTwo("SRT", time, cpuUtilizedTime, cpuWaitTotal, ioWaitTotal, cpuTurnaroundTotal, ioTurnaroundTotal, cpuContext, ioContext, cpuPreemptions, ioPreemptions, numCPUBursts, numIOBursts)
# ------------------------------------------------------------ RR ALGORITHM -------------------------------------------------
def rr(n, allProcesses, tCs, tSlice):
    cpuOneSlice = 0
    ioOneSlice = 0
    cpuPreemptions = 0
    ioPreemptions = 0
    cpuWaitTotal = 0
    ioWaitTotal = 0
    numCPUBursts=0
    numIOBursts = 0
    cpuUsageTotal = 0
    ioUsageTotal = 0
    cpuUtilizedTime=0
    cpuTurnaroundTotal = 0
    ioTurnaroundTotal = 0
    cpuStillRunning = 0
    ioStillRunning = 0
    cpuContext = 0
    ioContext = 0
    time = 0
    readyQueue = []
    waitingOnIo = []
    numTerminated = 0
    cpu = CPU(tCs)
    curSlice = -1
    preempted = False
    enteringCPU = None
    print(f"time {time}ms: Simulator started for RR {getQueueStr(readyQueue)}")
    arrivalTimesSet = set()
    # Create set of all arrival times and add processes to tao dict
    for i in allProcesses:
        arrivalTimesSet.add(i.getArrivalTime())
        if i.isCpuBound():
            numCPUBursts += i.getNumCPUBursts()
        else:
            numIOBursts += i.getNumCPUBursts()
    while(numTerminated < len(allProcesses) or not cpu.switchCompleted(time)):
        # CASE: CPU Burst Completion
        if (cpu.justFinishedBursting(time) and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            curBursting = cpu.getProcess()
            # End of process
            if curBursting.getNumIOBursts() == 0:
                print(f"time {time}ms: Process {curBursting.getId()} terminated {getQueueStr(readyQueue)}")
                numTerminated += 1
                if curBursting.isCpuBound():
                    cpuStillRunning -= 1
                else:
                    ioStillRunning -= 1
            # More to the process
            else:
                if (time <= 9999):
                    if (curBursting.getNumCPUBursts() == 1):
                        print(f"time {time}ms: Process {curBursting.getId()} completed a CPU burst; {curBursting.getNumCPUBursts()} burst to go {getQueueStr(readyQueue)}")
                    else:
                        print(f"time {time}ms: Process {curBursting.getId()} completed a CPU burst; {curBursting.getNumCPUBursts()} bursts to go {getQueueStr(readyQueue)}")
                curBursting.blockUntil(time+curBursting.removeIOBurst()+int(tCs/2))
                if (time <= 9999):
                    print(f"time {time}ms: Process {curBursting.getId()} switching out of CPU; blocking on I/O until time {curBursting.getBlockUntil()}ms {getQueueStr(readyQueue)}")
                waitingOnIo.append(curBursting)
        # CASE: Process Starts Using The CPU
        if (not cpu.processInCPU() and cpu.switchCompleted(time)):
                # Reset the tSlice component
                curSlice = tSlice
                cpu.resetSwitch()
                # Was popped during the start of the context switch, so doesnt need to be popped again
                curBursting = enteringCPU
                curTime = None
                if (curBursting.getTimeForBurst() != -1):
                    curTime = curBursting.removeCPUBurst()
                    if (time <= 9999):
                        print(f"time {time}ms: Process {curBursting.getId()} started using the CPU for remaining {curTime}ms of {curBursting.getTimeForBurst()}ms burst {getQueueStr(readyQueue)}")
                else:
                    curTime = curBursting.removeCPUBurst()
                    if (time <= 9999):
                        print(f"time {time}ms: Process {curBursting.getId()} started using the CPU for {curTime}ms burst {getQueueStr(readyQueue)}")
                    if curTime <= tSlice:
                        if curBursting.isCpuBound():
                            cpuOneSlice += 1
                        else:
                            ioOneSlice += 1
                cpu.burstCPU(curBursting, time+curTime)
                if curBursting.isCpuBound():
                    cpuContext += 1
                else:
                    ioContext += 1
        # CASE: Preemption
        if (cpu.processInCPU() and not cpu.switchActive(time) and not cpu.switchCompleted(time) and curSlice == 0):
            if (len(readyQueue) == 0):
                if (time <= 9999):
                    print(f"time {time}ms: Time slice expired; no preemption because ready queue is empty {getQueueStr(readyQueue)}")
                # Reset curSlice
                curSlice = tSlice                
            else:
                if (time <= 9999):
                    print(f"time {time}ms: Time slice expired; preempting process {curBursting.getId()} with {cpu.getBurstUntil()-time}ms remaining {getQueueStr(readyQueue)}")
                curBursting.addBurstToFront(cpu.getBurstUntil()-time)
                cpu.startContextSwitch(time)
                preempted = True
        # CONTEXT SWITCHES
        # Actions after leaving cpu context switch ends
        if (cpu.processInCPU() and cpu.switchCompleted(time)):
            # If preempted, it goes back to ready queue
            if preempted:
                if cpu.getProcess().isCpuBound():
                    cpuPreemptions += 1
                else:
                    ioPreemptions += 1
                readyQueue.append(cpu.getProcess())
                preempted = False
            cpu.stopBurst()
            cpu.resetSwitch()
        # CASE: I/O Burst Completions
        justFinishedIo = []
        for i in waitingOnIo:
            if time >= i.getBlockUntil():
                justFinishedIo.append(i)
        justFinishedIo = sorted(justFinishedIo, key=lambda p: (p.getId()))
        for i in justFinishedIo:
            waitingOnIo.remove(i)
            readyQueue.append(i)
            if (time <= 9999):
                print(f"time {time}ms: Process {i.getId()} completed I/O; added to ready queue {getQueueStr(readyQueue)}")
        # CASE: New Process Arrivals
        if time in arrivalTimesSet:
            # Append process to the ready queue
            for i in allProcesses:
                if i.getArrivalTime() == time:
                    readyQueue.append(i)
                    if (time <= 9999):
                        print(f"time {time}ms: Process {i.getId()} arrived; added to ready queue {getQueueStr(readyQueue)}")
                    if i.isCpuBound():
                        cpuStillRunning += 1
                    else:
                        ioStillRunning += 1
        # MORE CONTEXT SWITCHES
        # Actions to start context switch for entering cpu
        if (not cpu.processInCPU() and len(readyQueue) != 0 and not cpu.switchActive(time)):
            # Start context switch
            cpu.startContextSwitch(time)
            enteringCPU = readyQueue.pop(0)
        if (cpu.processInCPU() and not cpu.switchActive(time) and not cpu.switchCompleted(time)):
            cpuUtilizedTime += 1
            if cpu.getProcess().isCpuBound():
                cpuUsageTotal += 1
            else:
                ioUsageTotal += 1
        for i in readyQueue:
            if i.isCpuBound():
                cpuWaitTotal += 1
            else:
                ioWaitTotal += 1
        for i in waitingOnIo:
            if i.isCpuBound():
                cpuTurnaroundTotal -= 1
            else:
                ioTurnaroundTotal -= 1
        cpuTurnaroundTotal += cpuStillRunning
        ioTurnaroundTotal += ioStillRunning
        time += 1
        curSlice -= 1
    print(f"time {time}ms: Simulator ended for RR {getQueueStr(readyQueue)}")
    cpuWaitTotal = cpuTurnaroundTotal-cpuUsageTotal-2*(cpuContext+cpuPreemptions)
    ioWaitTotal = ioTurnaroundTotal-ioUsageTotal-2*(ioContext+ioPreemptions)
    cpuTurnaroundTotal += 2*cpuContext - cpuPreemptions*2
    ioTurnaroundTotal += 2*ioContext - ioPreemptions*2
    handleSimoutTwo("RR", time, cpuUtilizedTime, cpuWaitTotal, ioWaitTotal, cpuTurnaroundTotal, ioTurnaroundTotal, cpuContext, ioContext, cpuPreemptions, ioPreemptions, numCPUBursts, numIOBursts)
    rrExtraSimout(cpuOneSlice, ioOneSlice, numCPUBursts, numIOBursts)

def partTwo(n, allProcesses, tCs, alpha, tSlice, lmda):
    print("\n<<< PROJECT PART II")
    print(f"<<< -- t_cs={tCs}ms; alpha={alpha:.2f}; t_slice={tSlice}ms")
    fcfs(n, copy.deepcopy(allProcesses), tCs)
    print()
    sjf(n, copy.deepcopy(allProcesses), tCs, alpha, lmda)
    print()
    srt(n, copy.deepcopy(allProcesses), tCs, alpha, lmda)
    print()
    rr(n, copy.deepcopy(allProcesses), tCs, tSlice)

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
    if i.isCpuBound():
        if i.getNumCPUBursts() == 1:
            print(f"CPU-bound process {id}: arrival time {i.getArrivalTime()}ms; 1 CPU burst")
        else:
            print(f"CPU-bound process {id}: arrival time {i.getArrivalTime()}ms; {i.getNumCPUBursts()} CPU bursts")
    else:
        if i.getNumCPUBursts() == 1:
            print(f"I/O-bound process {id}: arrival time {i.getArrivalTime()}ms; 1 CPU burst")
        else:
            print(f"I/O-bound process {id}: arrival time {i.getArrivalTime()}ms; {i.getNumCPUBursts()} CPU bursts")
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
    f.write(f"-- overall average I/O burst time: {0:.3f} ms\n\n")
else:
    f.write(f"-- overall average I/O burst time: {math.ceil((cpuTotalIO+ioTotalIO)/(totalNumIOBurstsFromCPU+totalNumIOBurstsFromIO)*1000)/1000:.3f} ms\n")
f.close()
partTwo(n, allProcesses, tCs, alpha, tSlice, lmda)