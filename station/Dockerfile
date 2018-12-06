FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

RUN pip3 install zmq

WORKDIR /station

COPY ./station /station/station
COPY ./common /station/common

ENTRYPOINT [ "python3" ]

CMD [ "-u", "-m", "station" ]