#import anillo
import logging 
import threading

NON_PARTICIPANT = 0
PARTICIPANT = 1
LEADER = 2
WITHOUT_LEADER = -1
TIME_BETWEEN_ELECTIONS = 5.0

class LeaderElectionModule:
    def __init__(self, id):
        self.id = id
        self.state = NON_PARTICIPANT
        self.leader = WITHOUT_LEADER

    def begin(self):
        threading.Timer(TIME_BETWEEN_ELECTIONS, self.begin).start()
        self.startNewElection()    
    
    def startNewElection(self):
        print("Electing new world leader")
        newLeader = WITHOUT_LEADER
        while newLeader == WITHOUT_LEADER:
            if self.state == NON_PARTICIPANT:
                self.state = PARTICIPANT
                #ring.sendCandidate(id)
            #receivedId, candidate = ring.receive()
            if candidate:
                if receivedId == self.id:
                    newLeader = self.id
                    #ring.sendElectedLeader(newLeader)
                else:
                    retransmitId = receivedId if receivedId > self.id else self.id
                    #ring.send(retransmitId)
            else:
                newLeader = receivedId
                #rind.sendElectedLeader(newLeader)
        self.leader = newLeader    
