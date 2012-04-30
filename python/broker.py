import os
import settings
import  zmq
from zmq import devices


def main():
    taskQueueDevice = devices.ThreadDevice(zmq.STREAMER, zmq.PULL, zmq.PUSH)
    taskQueueDevice.bind_in(settings.FRONT_CMD)
    taskQueueDevice.bind_out(settings.BACK_CMD)
    taskQueueDevice.start()


    workerTopicDevice = devices.ThreadDevice(zmq.STREAMER, zmq.SUB, zmq.PUB)

    workerTopicDevice.bind_in(settings.BACK_RESULT)
    workerTopicDevice.bind_out(settings.FRONT_RESULT)
    workerTopicDevice.setsockopt_in(zmq.SUBSCRIBE, "")
    workerTopicDevice.start()

    workerTopicDevice.join()



if __name__ == "__main__":
    print("Brocker pid", os.getpid())
    main()
