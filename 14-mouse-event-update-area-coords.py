
from ultralytics import YOLO
import cv2
import numpy as np
from utils.perpendicular import calcPerpendicularSlopeLineIntercept

# consts
circle_radius = 20

model = YOLO("yolov8m.pt")
imageGroup = 'Laser1'
imagesDir = f'images/{imageGroup}/'

imageGroup_laser1 = {
    'imageGroup': imageGroup,
    'areas': [
        {
            'areaName': 'laser1',
        #                   tl          tr          bl           br
            'areaCoords': [[600, 380], [190, 430], [420, 1400], [1800, 1350]],
            'processed': {}
        } 
    ]
}




def find_closest_area_coords(x, y, area_coords):
    # find the closest area coords
    closest_distance = None
    index = -1
    closest_index = -1
    for areaCoord in area_coords:
        index = index + 1
        distance = np.sqrt((x - areaCoord[0])**2 + (y - areaCoord[1])**2)
        if distance < circle_radius and (closest_distance is None or distance < closest_distance):
            closest_distance = distance
            closest_index = index
    return closest_index

def draw_area_coords(image, area_coords):
    global is_image_modified
    # print('draw_area_coords')
    points = np.array(area_coords, np.int32)
    points = points.reshape((-1, 1, 2))
    cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)
    is_image_modified = True

    # draw a line from the center of the top line to the center of the bottom line
    lineStartX = int((area_coords[0][0]+area_coords[1][0]) / 2)
    lineStartY = int((area_coords[0][1]+area_coords[1][1]) / 2)
    lineEndX = int((area_coords[2][0]+area_coords[3][0]) / 2)
    lineEndY = int((area_coords[2][1]+area_coords[3][1]) / 2) 

    lineStartingPoint2 = (lineStartX, lineStartY)   
    lineEndingPoint2 = (lineEndX, lineEndY)
    cv2.arrowedLine(image, lineStartingPoint2, lineEndingPoint2, (255, 0, 0), 5, cv2.FILLED, 0, 0.03)
    is_image_modified = True

    return image

def draw_area_coords_circle(image, area_coords):
    global is_image_modified
    # print('draw_area_coords_circle')
    for areaCoord in area_coords:
        cv2.circle(image, (areaCoord[0], areaCoord[1]), circle_radius, (0, 0, 255), -1)
        is_image_modified = True

    return image

def handle_mouse_event(event,x,y,flags,param):
    global mouseX,mouseY,area_coords_index_selected
    area_coords = param["area_coords"]

    if event == cv2.EVENT_LBUTTONDOWN:
        area_coords_index_selected = find_closest_area_coords(x, y, area_coords)
    elif flags == cv2.EVENT_FLAG_LBUTTON:
        mouseX,mouseY = x,y
        if area_coords_index_selected == -1:
            return
        area_coords[area_coords_index_selected] = [x, y]
        # area_coords_index_selected = find_closest_area_coords(x, y, area_coords)
    elif event == cv2.EVENT_LBUTTONUP:
        mouseX,mouseY = x,y
        area_coords[area_coords_index_selected] = [x, y]
        area_coords_index_selected = -1

async def process():
    area_coords = imageGroup_laser1["areas"][0]["areaCoords"]

    global is_image_modified

    original_image = np.zeros((2000,2000,3), np.uint8)
    image = original_image.copy()
    is_image_modified = False

    cv2.namedWindow('image')
    cv2.setMouseCallback('image',handle_mouse_event, param={'image': image, 'area_coords': area_coords})


    while(1):
        draw_area_coords(image, area_coords)
        draw_area_coords_circle(image, area_coords)

        cv2.imshow('image',image)

        if is_image_modified:
            image = original_image.copy()
        is_image_modified = False

        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break
        elif k == ord('q'):
            break
        elif k == ord('a'):
            print(mouseX)
            print(mouseY)




if __name__ == '__main__':
    import asyncio
    asyncio.run(process())
