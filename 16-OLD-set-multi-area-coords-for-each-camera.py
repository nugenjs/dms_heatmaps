
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
# - iterate through each camera
# - display the image
# - allow the user to set the area coords
# - save the area coords to the database
# - allow the user to add a new area coords
# - allow the user to export the image with the area coords
# - allow the user to navigate to the next or previous camera


# model = YOLO("yolov8m.pt")
imagesDir = f'images_curated/'
# imagesDir = f'images/'

# consts
AC_CORNER_COLOR = (0, 0, 255)
AC_CORNER_CIRCLE_RADIUS = 20
AC_LABEL_COLOR = (0, 0, 255)
AC_LABEL_Y_OFFSET = 30
AC_ARROW_COLOR = (235, 0, 0)


def find_closest_area_coords(x, y, all_area_coords):
    # find the closest area coords
    closest_distance = None
    closest_area_coords_key = None
    closest_index = -1
    for area_coords_key, area_coords in all_area_coords.items():
        for index, areaCoord in enumerate(area_coords):
            distance = np.sqrt((x - areaCoord[0])**2 + (y - areaCoord[1])**2)
            if distance < AC_CORNER_CIRCLE_RADIUS and (closest_distance is None or distance < closest_distance):
                closest_distance = distance
                closest_area_coords_key = area_coords_key
                closest_index = index
        # if multiple area_coords overlap, the first one found will be selected
        if closest_index != -1:
            break
    return (closest_area_coords_key, closest_index)

def draw_area_coords(image, all_area_coords):
    global update_show_image

    for area_coords_key, area_coords in all_area_coords.items():
        points = np.array(area_coords, np.int32)
        points = points.reshape((-1, 1, 2))
        cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)

        # draw a line from the center of the top line to the center of the bottom line
        lineStartX = int((area_coords[0][0]+area_coords[1][0]) / 2)
        lineStartY = int((area_coords[0][1]+area_coords[1][1]) / 2)
        lineEndX = int((area_coords[2][0]+area_coords[3][0]) / 2)
        lineEndY = int((area_coords[2][1]+area_coords[3][1]) / 2) 

        lineStartingPoint2 = (lineStartX, lineStartY)   
        lineEndingPoint2 = (lineEndX, lineEndY)
        cv2.arrowedLine(image, lineStartingPoint2, lineEndingPoint2, AC_ARROW_COLOR, AC_CORNER_CIRCLE_RADIUS, cv2.FILLED, 0, 0.03)

        # write the area_coords key next to the top left corner
        cv2.putText(image, area_coords_key, (area_coords[0][0], area_coords[0][1] + AC_CORNER_CIRCLE_RADIUS + AC_LABEL_Y_OFFSET), cv2.FONT_HERSHEY_SIMPLEX, 2, AC_LABEL_COLOR, 2, cv2.LINE_AA)


    return image

def draw_area_coords_circle(image, all_area_coords):
    global update_show_image
    # print('draw_area_coords_circle')
    for area_coords in all_area_coords.values():
        for areaCoord in area_coords:
            cv2.circle(image, (areaCoord[0], areaCoord[1]), 5, AC_CORNER_COLOR, -1)
            update_show_image = True

    return image

def handle_mouse_event(event,x,y,flags,param):
    global mouseX,mouseY,prevMouseX,prevMouseY,area_coords_key_selected,area_coords_index_selected,update_show_image
    all_area_coords = param["all_area_coords"]

    if event == cv2.EVENT_LBUTTONDOWN:
        area_coords_key_selected, area_coords_index_selected = find_closest_area_coords(x, y, all_area_coords)
    elif area_coords_key_selected is not None or area_coords_index_selected != -1:
        if flags == cv2.EVENT_FLAG_LBUTTON:
            mouseX,mouseY = x,y
            all_area_coords[area_coords_key_selected][area_coords_index_selected] = [x, y]
            if mouseX != prevMouseX or mouseY != prevMouseY:
                update_show_image = True
            prevMouseX, prevMouseY = mouseX, mouseY
        elif event == cv2.EVENT_LBUTTONUP:
            mouseX,mouseY = x,y
            all_area_coords[area_coords_key_selected][area_coords_index_selected] = [x, y]
            update_show_image = True

def add_new_area_coords(image, all_area_coords):
    global update_show_image
    highest_key = 0
    for key in all_area_coords:
        if int(key) > highest_key:
            highest_key = int(key)

    all_area_coords[str(highest_key + 1)] = [
        [int(image.shape[1] * 0.25), int(image.shape[0] * 0.25)], 
        [int(image.shape[1] * 0.75), int(image.shape[0] * 0.25)], 
        [int(image.shape[1] * 0.75), int(image.shape[0] * 0.75)],
        [int(image.shape[1] * 0.25), int(image.shape[0] * 0.75)], 
    ]
    update_show_image = True

def export_image(image, dir, filename):
    if not os.path.exists(dir):
        os.makedirs(dir)
    cv2.imwrite(f'{dir}{filename}', image)
    print('image exported')


# ################################################################################################

async def process():
    # # Consts
    dbTable = "CameraMetadata"

    # connect to database
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")


    dirs = listDirectoriesInPath(imagesDir)
    filesSorted = sorted(dirs)

    i = 0
    while i < len(filesSorted):
        camera = filesSorted[i]
        print('camera', camera)

        files = os.listdir(imagesDir + camera)
        file = files[0]

        global update_show_image,area_coords_key_selected,area_coords_index_selected,prevMouseX,prevMouseY
        print(imagesDir + camera + '/' + file)
        original_image = cv2.imread(imagesDir + camera + '/' + file)
        image = original_image.copy()
        update_show_image = False

        prevMouseX, prevMouseY = 0, 0

        area_coords_key_selected = None
        area_coords_index_selected = -1

        # get area_coords from db, if not found, create a new one
        all_area_coords = {}
        result = await db.select(f'{dbTable}:{camera}')
        if result:
            all_area_coords = result['all_area_coords']
        else:
            # area coords will be a square in the center of the image
            all_area_coords = {
                '1': [
                    [int(image.shape[1] * 0.25), int(image.shape[0] * 0.25)], 
                    [int(image.shape[1] * 0.75), int(image.shape[0] * 0.25)], 
                    [int(image.shape[1] * 0.75), int(image.shape[0] * 0.75)],
                    [int(image.shape[1] * 0.25), int(image.shape[0] * 0.75)], 
                ]
            }
            await db.create(f'{dbTable}:{camera}', {
                'camera': camera,
                'all_area_coords': {}
            })


        cv2.namedWindow('image')
        cv2.setMouseCallback('image',handle_mouse_event, param={'image': image, 'all_area_coords': all_area_coords})

        # initial draw
        draw_area_coords(image, all_area_coords)
        draw_area_coords_circle(image, all_area_coords)

        time_start_after_waitKey = time.time()
        while(1):
            if update_show_image:
                image = original_image.copy()
                draw_area_coords(image, all_area_coords)
                draw_area_coords_circle(image, all_area_coords)

            # show a smaller image
            cv2.imshow('image',image)

            # if update_show_image:
            update_show_image = False

            time_end_after_waitKey = time.time()
            time_elapsed_after_waitKey = time_end_after_waitKey - time_start_after_waitKey
            lag = 0.007
            if time_elapsed_after_waitKey > lag:
                print(f'time elapsed over {lag}, {time_elapsed_after_waitKey}')

            key = cv2.waitKey(20) & 0xFF
            time_start_after_waitKey = time.time()

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
                print('all_area_coords', all_area_coords)
                await db.update(f'{dbTable}:{camera}', {
                    'all_area_coords': all_area_coords
                })
                print('all_area_coords saved')
            elif key == ord('n'):
                print('n key pressed')
                add_new_area_coords(image, all_area_coords)
                print('added a new area_coords')
            elif key == ord('e'):
                print('e key pressed')
                export_image(image, f'export/camera-areas/', f'{camera}.png')
            elif key == 27 or key == ord('q'):
                cv2.destroyAllWindows()
                await db.close()
                print('Esc key pressed')
                exit()
            elif key == ord(' '):
                print(prevMouseX)
                print(prevMouseY)



if __name__ == '__main__':
    import asyncio
    asyncio.run(process())


# Wrap up notes
# creates an empty object and doesn't fetch if existing from db
# is limited to 20 images, can change
