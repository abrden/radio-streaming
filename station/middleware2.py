import zmq
import logging 

class StationMiddleware:
    def __init__(self):
        context = zmq.Context()
        self.logger = logging.getLogger("StationMiddleware")

        #Init frontend (XSUB)
        self.frontend = context.socket(zmq.XSUB)
        self.frontend.setsockopt(zmq.LINGER, -1)
        self.frontend.bind("tcp://*:6000")
        
        #Init backend (XPUB)
        self.backend = context.socket(zmq.XPUB)
        self.backend.setsockopt(zmq.LINGER, -1)
        self.backend.bind("tcp://*:6001")
        
        while True: # TODO Graceful quit
            [topic, data] = self.frontend.recv_multipart()
            self.logger.debug("Received message with topic " + topic)
            self.backend.send_multipart([topic,data])         

    def close(self):
        self.frontend.close()
        self.backend.close()
        # TODO Proper closure
