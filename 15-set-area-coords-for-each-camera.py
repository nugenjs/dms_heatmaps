
import pprint
from ultralytics import YOLO
import cv2
import numpy as np
from utils.perpendicular import calcPerpendicularSlopeLineIntercept
import os
from surrealdb import Surreal
import time
from utils.os import listDirectoriesInPath


model = YOLO("yolov8m.pt")

# consts
circle_radius = 20


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
    cv2.arrowedLine(image, lineStartingPoint2, lineEndingPoint2, (255, 0, 0), circle_radius, cv2.FILLED, 0, 0.03)
    is_image_modified = True

    return image

def draw_area_coords_circle(image, area_coords):
    global is_image_modified
    # print('draw_area_coords_circle')
    for areaCoord in area_coords:
        cv2.circle(image, (areaCoord[0], areaCoord[1]), 5, (0, 0, 255), -1)
        is_image_modified = True

    return image

def handle_mouse_event(event,x,y,flags,param):
    global mouseX,mouseY,area_coords_index_selected
    area_coords = param["area_coords"]

    if event == cv2.EVENT_LBUTTONDOWN:
        area_coords_index_selected = find_closest_area_coords(x, y, area_coords)
    elif flags == cv2.EVENT_FLAG_LBUTTON:
        mouseX,mouseY = x,y
        area_coords[area_coords_index_selected] = [x, y]
    elif event == cv2.EVENT_LBUTTONUP:
        mouseX,mouseY = x,y
        area_coords[area_coords_index_selected] = [x, y]
        area_coords_index_selected = -1



async def process():
    # # Consts
    # # dbTable = "ImageGroups"
    dbTable = "CameraMetadata"

    # connect to database
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")


    imagesDir = f'images/'
    dirs = listDirectoriesInPath(imagesDir)
    filesSorted = sorted(dirs)

    i = 0
    while i < len(filesSorted):
        camera = filesSorted[i]
        print('camera', camera)

        files = os.listdir(imagesDir + camera)
        file = files[0]

        global is_image_modified
        original_image = cv2.imread(imagesDir + camera + '/' + file)
        image = original_image.copy()
        is_image_modified = False



        # get area_coords from db
        # if not found, create a new one
        area_coords = []
        result = await db.select(f'{dbTable}:{camera}')
        if result:
            area_coords = result['area_coords']['1']
        else:
            # area_coords = [[0, 0], [0, 0], [0, 0], [0, 0]]
            # area coords will be a square in the center of the image
            area_coords = [
                [int(image.shape[1] * 0.25), int(image.shape[0] * 0.25)], 
                [int(image.shape[1] * 0.75), int(image.shape[0] * 0.25)], 
                [int(image.shape[1] * 0.75), int(image.shape[0] * 0.75)],
                [int(image.shape[1] * 0.25), int(image.shape[0] * 0.75)], 
            ]
            await db.create(f'{dbTable}:{camera}', {
                'camera': camera,
                'area_coords': {
                    '1': area_coords
                }
            })


        cv2.namedWindow('image')
        cv2.setMouseCallback('image',handle_mouse_event, param={'image': image, 'area_coords': area_coords})


        while(1):
            draw_area_coords(image, area_coords)
            draw_area_coords_circle(image, area_coords)
            cv2.imshow('image',image)

            if is_image_modified:
                image = original_image.copy()
            is_image_modified = False

            key = cv2.waitKey(20) & 0xFF

            if key == 2:
                print('Left arrow key pressed')
                cv2.destroyAllWindows()
                i = i - 1
                if i < 0:
                    i = 0
                break
            elif key == 3:
                i = i + 1 
                if i >= len(filesSorted):
                    i = len(filesSorted) - 1
                print('Right arrow key pressed')
                cv2.destroyAllWindows()
                break
            elif key == ord('s'):
                print('s key pressed')
                print('area_coords', area_coords)
                await db.update(f'{dbTable}:{camera}', {
                    'area_coords': {
                        '1': area_coords
                    }
                })
                print('area_coords saved')
            elif key == ord('n'):
                print('adding a new area_coords hasn"t been implemented yet')
            elif key == 27 or key == ord('q'):
                cv2.destroyAllWindows()
                await db.close()
                print('Esc key pressed')
                exit()
            elif key == ord(' '):
                print(mouseX)
                print(mouseY)



if __name__ == '__main__':
    import asyncio
    asyncio.run(process())


# Wrap up notes
# creates an empty object and doesn't fetch if existing from db
# is limited to 20 images, can change
