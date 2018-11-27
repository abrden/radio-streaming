import zmq
import logging 

class StationMiddleware:
    def __init__(self):
        self.context = zmq.Context()
        self.logger = logging.getLogger("StationMiddleware")

        #Init frontend (XSUB)
        self.frontend = self.context.socket(zmq.XSUB)
        self.frontend.setsockopt(zmq.LINGER, -1)
        self.frontend.bind("tcp://*:6000")
        
        #Init backend (XPUB)
        self.backend = self.context.socket(zmq.XPUB)
        self.backend.setsockopt(zmq.LINGER, -1)
        self.backend.bind("tcp://*:6001")

        poller = zmq.Poller()
        poller.register(self.frontend, zmq.POLLIN)
        poller.register(self.backend, zmq.POLLIN)
        
        while True: # TODO Graceful quit
            events = dict(poller.poll(1000))
            if self.frontend in events:
                message = self.frontend.recv_multipart()
                print("[XSUB] Message arrived: {}".format(message))
                self.backend.send_multipart(message)
            if self.backend in events:
                message = self.backend.recv_multipart()
                print("[XPUB] Message arrived: {}".format(message))
                self.frontend.send_multipart(message)

    def close(self):
        self.frontend.close()
        self.backend.close()
        # TODO Proper closure        
