import zmq
import logging 

class StationMiddleware:
    def __init__(self):
        context = zmq.Context()
        self.logger = logging.getLogger("StationMiddleware")

        #Init frontend (XSUB)
        self.frontend = context.socket(zmq.XSUB)
        self.frontend.bind("tcp://*:6000")
        #self.frontend.setsockopt(zmq.SUBSCRIBE, b"")

        #Init backend (XPUB)
        self.backend = context.socket(zmq.XPUB)
        self.backend.bind("tcp://*:6001")
        
        while True: # TODO Graceful quit
            [topic, data] = self.frontend.recv_multipart()
            self.logger.debug("Received message with topic %r", topic)
            # do stuff
            self.backend.send_multipart([topic,data])         

    def close(self):
        self.frontend.close()
        self.backend.close()
        # TODO Proper closure
