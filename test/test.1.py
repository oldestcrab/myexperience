import cv2
import sys
from tesserocr import *
from PIL import Image
import os
# img = sys.path[0] + '/checkcode.gif'
# print(img)
img_name = sys.path[0]+'/checkcode.gif'
cv2.imread(img_name)
print(im,type(im))
print(im.size) 