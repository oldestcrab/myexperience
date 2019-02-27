# -*- coding:utf-8 -*-
import tesserocr
import pytesseract
from PIL import Image
import sys

image = Image.open(sys.path[0] + '/11.jpg')
image.show()
image =image.convert('L')
image.show()
table = []
threshold = 150
for i in range(256):
    if i < threshold:
        table.append(1)
    else:
        table.append(0)
# print(table)
image = image.point(table, '1')
image.show()

# result = tesserocr.image_to_text(image)
result = pytesseract.image_to_string(image)
print(result)