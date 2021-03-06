#import anillo
import logging 
import time 

from multiprocessing import Queue, Process

NON_PARTICIPANT = 0
PARTICIPANT = 1
LEADER = 3
WITHOUT_NEW_LEADER = -1
DELIMITER = ","
TIME_BETWEEN_ELECTIONS = 10.0
NUMBER_OF_REPLICAS = 3

class LeaderElection(Process):
    def __init__(self, id, sendQueue, recvQueue, newsQueue):
        super(LeaderElection, self).__init__()
        self.lem = LeaderElectionModule(id, sendQueue, recvQueue, newsQueue)
        
    def run(self):
        self.lem.begin()

class LeaderElectionModule:
    def __init__(self, id, sendQueue, recvQueue, newsQueue):
        self.logger = logging.getLogger("LeaderElection")
        self.id = id
        self.sendQueue = sendQueue
        self.recvQueue = recvQueue
        self.newsQueue = newsQueue
        self.state = NON_PARTICIPANT
        self.leader = WITHOUT_NEW_LEADER
        
    def begin(self):
        newMsg = None
        while True: #TODO: Fix sleep
            self.startNewElection(newMsg)
            self.newsQueue.put(self.leader)    
            try:
                newMsg = self.recvQueue.get(timeout=TIME_BETWEEN_ELECTIONS)
            except:
                self.logger.debug("Leader queue inactive for long time")
                self.leader = WITHOUT_NEW_LEADER
                newMsg = None
            #time.sleep(TIME_BETWEEN_ELECTIONS)
    def getLeader(self):
        return self.leader

    def startNewElection(self, msg):
        self.logger.info("Electing new world leader")
        newLeader = WITHOUT_NEW_LEADER
        firstIteration = True
        messagesRetransmitted = 0
        try:
            while newLeader == WITHOUT_NEW_LEADER:
                if msg is None:
                    if firstIteration:
                        self.logger.info("Sending new vote " + str(self.id))
                        self.sendQueue.put(self.encodeElectionMessage(self.id, "VOTING"))
                        firstIteration = False
                    receivedId, msgType = self.decodeElectionMessage(self.recvQueue.get(timeout=TIME_BETWEEN_ELECTIONS * 3))
                else:
                    receivedId, msgType = self.decodeElectionMessage(msg)
                    msg = None
                if self.state != LEADER:
                    self.state = PARTICIPANT
                if msgType == "VOTING":
                    if receivedId == self.id:
                        self.logger.info("Leader found, broadcasting")
                        self.sendQueue.put(self.encodeElectionMessage(self.id, "NEW_LEADER"))
                        newLeader = self.id
                        self.state = LEADER
                    else:
                        retransmitId = receivedId if receivedId > self.id else self.id
                        self.logger.info("Arrived id " + str(receivedId)+ " compared to " + str(self.id) + " REsutl.:"+str(retransmitId))
                        if retransmitId > self.id and messagesRetransmitted < NUMBER_OF_REPLICAS:
                            self.sendQueue.put(self.encodeElectionMessage(retransmitId, "VOTING"))
                            messagesRetransmitted += 1
                else:
                    newLeader = receivedId  
                    if newLeader != self.id:
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