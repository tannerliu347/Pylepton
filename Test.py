import sys
import numpy as np
import cv2
from pylepton.Lepton3 import Lepton3

with Lepton3("/dev/spidev0.0") as l:
    rawArray,_ = l.capture()
a = rawArray / 100 -273.15
for i in range(0, 120):
    print(a[i])
