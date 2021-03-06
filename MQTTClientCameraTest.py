import time
import paho.mqtt.client as mqtt
import numpy as np
from pylepton.LeptonCamera import LeptonCamera

print('Starting...\n')

#initialize camera object
testName = 'test1'
pixel2Follow = {'First point' : [1,1]}
camera1 = LeptonCamera(testName, pixel2Follow)
saveLocally = False

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if (rc == 0):
        print('Code "0" indicates successful connection.  Waiting for messages...')
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("asset/andon1/state")
    #takeOneImg()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    msgRec = msg.payload
    eval(msg.payload)  # runs message string as if a cmd line entry

# Topics: mb12/asset/CameraCntrl, .../DataPts .../Imgs
client = mqtt.Client(client_id="FLIR1.1")
client.username_pw_set("FLIR1.1", password="GeorgeP@1927")
client.on_connect = on_connect
client.on_message = on_message

client.connect("18.208.90.243", 1883, 60)
# For listening for take img cmds:
client.subscribe("Asset/FLIR1/Cntrl")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

# create Camera object and construct with desired parameters
# camera1 = FLIR.Camera(refreshRate, imgReturn=yes/no, MQTTtopic)
# camera1.firstImg()
# camera1.pickAreas()


def arr2Str(tempArr):
    tempStr = ''
    for x in np.nditer(tempArr):
        tempStr = tempStr + ',' + str(x)
    tempStr = tempStr[1:len(tempStr) - 1]
    return tempStr

def setTestName(tn):
    testName = tn


def setPixel2Follow(p2f):
    pixel2Follow = p2f


def instantiateCamera():
    camera1 = LeptonCamera(testName, pixel2Follow)


def saveTextOnPi(saveOrNot):
    saveLocally = saveOrNot


def takeOneImg():
    camera1.takeImg()
    imgArr = camera1.getTempArr()
    imgStr = arr2Str(imgArr)
    client.publish("asset/FLIR1/Imgs", payload = imgStr, qos=0, retain=False)
    time.sleep(0.2) # delay needed for UKNOWN REASON

def streamImg(sleepSeconds = 5):
    try:
        while True:
            lastImgStr = ""
            imgArr = camera1.getTempArr()
            imgStr = arr2Str
            if imgStr != lastImgStr:
                client.publish("asset/FLIR1/Imgs", payload=imgStr,
                                qos=0, retain=False)
            else:
                client.publish(
                    "Asset/FLIR1/Imgs", payload="no new image to publish", qos=0, retain=False)
            lastImgStr = imgStr
            time.sleep(sleepSeconds)
    except KeyboardInterrupt:
            print('Process interrupted')


client.loop_forever()  # start listening in a thread and proceed
