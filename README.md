# radio-streaming

Make sure you've installed the following requirements
```
pip3 install zmq pyaudio
```
Open a console in the radio-streaming dir and run
```
$ python3 -m station 1 2 station_1:6003 station_2:6003
```
Open a console in the radio-streaming dir and run
```
$ python3 -m transmitter AR 100 glitch-mob.wav
```
Open another console in the radio-streaming dir and run
```
$ python3 -m receiver AR 100
```
---
### Ports
* 6000, 6001 Station XPUB-XSUB
* 6002 Station heartbeat
* 6003, 6004 Stations "are you alive?"