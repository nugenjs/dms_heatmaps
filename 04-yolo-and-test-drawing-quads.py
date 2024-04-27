from ultralytics import YOLO
import cv2
import numpy as np

# https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html

import torch #for faster processing
# This code attempts to check whether the MPS (Memory Pooling System) is 
# available in the PyTorch backend. MPS is a feature provided by PyTorch
#  to efficiently manage GPU memory, especially in multi-GPU setups.
print(torch.backends.mps.is_available())

# Load the model and the image
model = YOLO("yolov8m.pt")
image = cv2.imread('images/Laser1/2024-03-16-16-55-56_frame_Laser1.jpg')
# results = model(image, device="mps") # since mpx is available, we can use it to speed up the processing # Not working for me

# Draw areas of interest
#                   tl              tr          bl             br
points = np.array([[600, 380], [190, 430], [420, 1400], [1800, 1350]], np.int32)
points = points.reshape((-1, 1, 2))

# Process the image
results = model(image)
result = results[0]
boxes = result.boxes.xyxy
print(boxes)

bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
classes = np.array(result.boxes.cls.cpu(), dtype='int')

for cls, bbox in zip(classes, bboxes):
    if cls != 0:
        continue
    x1, y1, x2, y2 = bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, str(cls), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)
frame = cv2.imshow('image', image)

key = cv2.waitKey(0)
if key == 27:
    cv2.destroyAllWindows()
    print('Esc key pressed')
else:
    print('Key pressed:', key)
    cv2.destroyAllWindows()

print('End of program')


