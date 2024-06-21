
import pprint
from ultralytics import YOLO
import cv2
import numpy as np
from utils.perpendicular import calcPerpendicularSlopeLineIntercept
import os
from surrealdb import Surreal
import time
from utils.os import listDirectoriesInPath

# WHAT DO
# - iterate through saved cameras in db that have area coords
# - display the image
# - use saved area coords from db to draw on the image
# - find people on camera that are within the area coords
# - find where the person is on the area coords line of interest
# - save the area coords to the database



model = YOLO("yolov8m.pt")
images_dir = f'images/'

# consts
AC_EDGE_COLOR = (0, 255, 0)
AC_CORNER_COLOR = (0, 0, 255)
AC_CORNER_CIRCLE_RADIUS = 20
AC_LABEL_COLOR = (0, 0, 255)
AC_LABEL_Y_OFFSET = 30
AC_ARROW_COLOR = (235, 0, 0)


def find_closest_area_coords(x, y, areas_of_interest):
    # find the closest area coords
    closest_distance = None
    closest_aoi_key = None
    closest_index = -1
    for aoi_key, aoi_metadata in areas_of_interest.items():
        for index, aoi_coords in enumerate(aoi_metadata['aoi_coords']):
            distance = np.sqrt((x - aoi_coords[0])**2 + (y - aoi_coords[1])**2)
            if distance < AC_CORNER_CIRCLE_RADIUS and (closest_distance is None or distance < closest_distance):
                closest_distance = distance
                closest_aoi_key = aoi_key
                closest_index = index
        # if multiple area_coords overlap, the first one found will be selected
        if closest_index != -1:
            break
    return (closest_aoi_key, closest_index)


def handle_mouse_event(event,x,y,flags,param):
    global mouseX,mouseY,prevMouseX,prevMouseY,areas_of_interest_key_selected,areas_of_interest_index_selected,update_show_image
    areas_of_interest = param["areas_of_interest"]

    if event == cv2.EVENT_LBUTTONDOWN:
        areas_of_interest_key_selected, areas_of_interest_index_selected = find_closest_area_coords(x, y, areas_of_interest)
    elif areas_of_interest_key_selected is not None or areas_of_interest_index_selected != -1:
        if flags == cv2.EVENT_FLAG_LBUTTON:
            mouseX,mouseY = x,y
            areas_of_interest[areas_of_interest_key_selected]['aoi_coords'][areas_of_interest_index_selected] = [x, y]
            if mouseX != prevMouseX or mouseY != prevMouseY:
                update_show_image = True
            prevMouseX, prevMouseY = mouseX, mouseY
        elif event == cv2.EVENT_LBUTTONUP:
            mouseX,mouseY = x,y
            areas_of_interest[areas_of_interest_key_selected]['aoi_coords'][areas_of_interest_index_selected] = [x, y]
            update_show_image = True



# ################################################################################################

async def process():
    # # Consts
    dbTable = "CameraMetadata"
    images_dir = 'images'
    overview_image = 'layout_overview.png'

    # connect to database
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")


    original_image = cv2.imread(f'{images_dir}/{overview_image}')
    image = original_image.copy()

    cv2.imshow('image', image)

    # camera_metadatas = await db.select(dbTable)
    # for camera_metadata in camera_metadatas:
    #     print('camera_metadata:', camera_metadata)
    #     camera = camera_metadata['camera']
    #     areas_of_interest = camera_metadata['areas_of_interest']


    # camera_metadata
    # res = await db.update(f'{dbTable}:{camera}', camera_metadata)

    key = cv2.waitKey(0)
    await db.close()





if __name__ == '__main__':
    import asyncio
    asyncio.run(process())


# Wrap up notes
# creates an empty object and doesn't fetch if existing from db
# is limited to 20 images, can change
