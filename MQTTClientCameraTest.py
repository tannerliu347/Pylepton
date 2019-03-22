import time
import paho.mqtt.client as mqtt
from pylepton.LeptonCamera import LeptonCamera
# FLIRModule has:
    # temp.... -- returns list temps
    # takeImg -- returns image array
    # takeData
        # calls temp... funcs or takeImg in some loop and returns values
    # Camera class with _init_() that takes
        # ask for test name (to be data header + date/time)
        # Provide frame, ask if view is OK
            # if not, ask for prompt to take new image once camera is physically repositioned
        # Ask for points of interest, and their names
        # Ask if thermocouples are connected, and their names
        # Ask what value(s) to display on the lcd panel
        # Ask if images files should be posted to MQTT topic
        # Wait for start recording command

print('Starting...\n')

pixel2Follow = {'First point' : [1,1]}
camera1 = LeptonCamera('test1', pixel2Follow)
camera1.takeImg()
#camera1.saveData()
imgArr = camera1.getTempArr()
imgStr = '\n'.join('\t'.join('%0.3f' %x for x in y) for y in imgArr)
#imgStr = open('rgb4.txt', 'r').read()

#print(camera1.testName + '/' + camera1.testName + 'Lepton' +  + '.txt')

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if (rc == 0):
        print('Code "0" indicates successful connection.  Waiting for messages...')
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("asset/andon1/state")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    msgRec = msg.payload
    if msg.payload == "start":
        [lastData, lastImg] = camera1.takeData()
    eval(msg.payload)  # runs message string as if a cmd line entry

# Topics: mb12/asset/CameraCntrl, .../DataPts .../Imgs
client = mqtt.Client(client_id="mb12andon1")
client.username_pw_set("mb12andon1", password="FzXVLvSagaZ58qMf")
client.on_connect = on_connect
client.on_message = on_message

client.connect("mb12.iotfm.org", 1883, 60)
# For listening for take img cmds:
# client.subscribe("FLIRControl")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

# create Camera object and construct with desired parameters
# camera1 = FLIR.Camera(refreshRate, imgReturn=yes/no, MQTTtopic)
# camera1.firstImg()
# camera1.pickAreas()

client.loop_start()  # start listening in a thread and proceed

try:

    client.publish("asset/Imgs", payload=imgStr, qos=0, retain=False)
    time.sleep(5)

except KeyboardInterrupt:  # so that aborting with Ctrl+C works cleanly
    # stop recording
    print('Process interrupted')

#finally:
 #   print('Done')p