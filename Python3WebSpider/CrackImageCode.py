import tesserocr
from PIL import Image
import sys
from collections import defaultdict

image = Image.open(sys.path[0]+'/some/checkcode.gif')
# image = Image.open(sys.path[0]+'/some/code.jpg')
image = image.convert('L')
threshold = 50
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

image = image.point(table, '1')     
image.show()

result = tesserocr.image_to_text(image)
print(result)
