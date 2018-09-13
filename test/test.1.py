import cv2
import sys
from tesserocr import *
from PIL import Image
import os
# img = sys.path[0] + '/checkcode.gif'
# print(img)
im = cv2.imread( 'checkcode.jpg')

print(im,type(im))