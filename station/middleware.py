import zmq

class StationMiddleware:
    def __init__(self):
        context = zmq.Context()
        
        #Init frontend (XSUB)
        self.frontend = context.socket(zmq.XSUB)
        self.frontend.setsockopt(zmq.LINGER, -1)
        self.frontend.bind("tcp://*:6000")

        #Init backend (XPUB)
        self.backend = context.socket(zmq.XPUB)
        self.backend.setsockopt(zmq.LINGER, -1)
        self.backend.bind("tcp://*:6001")
        
        zmq.proxy(self.frontend, self.backend)

    def close(self):
        self.frontend.close()
        self.backend.close()
        # TODO Proper closure