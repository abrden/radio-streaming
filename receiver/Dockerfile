FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
RUN apt-get install -y ffmpeg libav-tools

RUN pip3 install zmq pyaudio

WORKDIR /receiver

COPY ./receiver /receiver/receiver
COPY ./common /receiver/common

ENTRYPOINT [ "python3" ]

CMD [ "-u", "-m", "receiver" ]