from ultralytics import YOLO
import cv2
import numpy as np
import os

import torch #for faster processing
# This code attempts to check whether the MPS (Memory Pooling System) is 
# available in the PyTorch backend. MPS is a feature provided by PyTorch
#  to efficiently manage GPU memory, especially in multi-GPU setups.
print(torch.backends.mps.is_available())

model = YOLO("yolov8m.pt")

imagesDir = './woodshop3'

files = os.listdir(imagesDir)
filesSorted = sorted(files)

i = 0
# for i in range(len(filesSorted)):
while i < len(filesSorted):

    print(i, filesSorted[i])
    file = filesSorted[i]

    image = cv2.imread(imagesDir + '/' + file)

    results = model(image)
    # results = model(image, device="mps") # since mpx is available, we can use it to speed up the processing

    result = results[0]
    boxes = result.boxes.xyxy
    print(boxes)

    bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
    classes = np.array(result.boxes.cls.cpu(), dtype='int')

    for cls, bbox in zip(classes, bboxes):
        if cls != 0: # look for only people
            continue
        x1, y1, x2, y2 = bbox
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, str(cls), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # frame = cv2.imshow('image', image)

    # show a smaller image
    small = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
    cv2.moveWindow('small image', 40, 30)
    cv2.imshow('small image', small)


    i = i + 1

    key = cv2.waitKey(0)
    if key == 27:
        cv2.destroyAllWindows()
        print('Esc key pressed')
        exit()
    elif key == 2:
        print('Left arrow key pressed')
        cv2.destroyAllWindows()
        
        i = i - 2
        if i < 0:
            i = 0
    elif key == 3:
        print('Right arrow key pressed')
        cv2.destroyAllWindows()
    else:
        print('Key pressed:', key)
        cv2.destroyAllWindows()

exit()





print('End of program')


