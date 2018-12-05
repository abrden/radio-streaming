#import anillo
import logging 
import time 

from multiprocessing import Queue, Process

NON_PARTICIPANT = 0
PARTICIPANT = 1
LEADER = 3
WITHOUT_NEW_LEADER = -1
DELIMITER = ","
TIME_BETWEEN_ELECTIONS = 60.0

class LeaderElection(Process):
    def __init__(self, id, sendQueue, recvQueue):
        super(LeaderElection, self).__init__()
        self.lem = LeaderElectionModule(id, sendQueue, recvQueue)
        
    def run(self):
        self.lem.begin()

class LeaderElectionModule:
    def __init__(self, id, sendQueue, recvQueue, ):
        self.logger = logging.getLogger("LeaderElection")
        self.id = id
        self.sendQueue = sendQueue
        self.recvQueue = recvQueue
        self.state = NON_PARTICIPANT
        self.leader = WITHOUT_NEW_LEADER
        
    def begin(self):
        while True: #TODO: Fix sleep
            self.startNewElection()    
            time.sleep(TIME_BETWEEN_ELECTIONS)
    
    def getLeader(self):
        return self.leader

    def startNewElection(self):
        self.logger.info("Electing new world leader")
        newLeader = WITHOUT_NEW_LEADER
        firstIteration = True
        alreadyRetransmitted = False
        try:
            while newLeader == WITHOUT_NEW_LEADER:
                if firstIteration:
                    self.logger.info("Sending new vote " + str(self.id))
                    self.sendQueue.put(self.encodeElectionMessage(self.id, "VOTING"))
                    firstIteration = False
                if self.state != LEADER:
                    self.state = PARTICIPANT
                receivedId, msgType = self.decodeElectionMessage(self.recvQueue.get())
            
                if msgType == "VOTING":
                    if receivedId == self.id:
                        self.logger.info("Leader found, broadcasting")
                        self.sendQueue.put(self.encodeElectionMessage(self.id, "NEW_LEADER"))
                        newLeader = self.id
                        self.state = LEADER
                    else:
                        retransmitId = receivedId if receivedId > self.id else self.id
                        self.logger.info("Arrived id " + str(receivedId)+ " compared to " + str(self.id) + " REsutl.:"+str(retransmitId))
                        if retransmitId > self.id:
                            self.sendQueue.put(self.encodeElectionMessage(retransmitId, "VOTING"))
                            alreadyRetransmitted = True
                else:
                    newLeader = receivedId  
                    if newLeader != self.id:
                        #if self.state == LEADER: #TODO: ADD RUN ON FATHER FOR CLEAN UP
                        self.state = NON_PARTICIPANT
                        self.sendQueue.put(self.encodeElectionMessage(newLeader, "NEW_LEADER"))
        except:
            self.leader = WITHOUT_NEW_LEADER #TODO : It should only be set to no leader, if the leader fell, not anyone
            print("No world leader, playing game of thrones atm")
            return
        self.leader = newLeader
        print("New world leader is: " + str(self.leader))
    
    def encodeElectionMessage(self, id, type):
        return str(id) + DELIMITER + type

    def decodeElectionMessage(self, msg):
        id, msgType = msg.split(DELIMITER)
        return int(id), msgType