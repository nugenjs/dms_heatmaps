
import pprint
from ultralytics import YOLO
import cv2
import numpy as np
from utils.perpendicular import calcPerpendicularSlopeLineIntercept
import os
from surrealdb import Surreal
import time
from utils.os import listDirectoriesInPath
from datetime import datetime

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

FILTER = -1 # could be -2 or 0 or others, -1 is 1 decimal place


async def process():
    # Consts
    dbTable = "CameraMetadata"

    # connect to database
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")

    imagesDir = 'images'
    imageOriginal = cv2.imread(f'{imagesDir}/layout_overview.png')


    camera_metadatas = await db.select(dbTable)

    timestamps = camera_metadatas[2]['processed']['1'].keys()
    timestamps = list(timestamps)
    timestamps.sort()
    timestampStart = timestamps[0]
    timestampsLength = len(timestamps)
    i = timestampsLength-1

    while True:
        print('i', i)
        image = imageOriginal.copy()

        for k in range(0, 26):
            # draw a line across the image
            cv2.line(image, (0, k* 100), (2600, k* 100), (100, 100, 100), 1)
            cv2.putText(image, str(k), (10, k* 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2, cv2.LINE_AA)

        for k in range(0, 26):
            # draw a line across the image
            cv2.line(image, (k * 100, 0), (k * 100, 2000), (100, 100, 100), 1)
            cv2.putText(image, str(k), (k * 100, 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2, cv2.LINE_AA)

        # "2024-03-16-16-10-04"

        timestamp_format = "%Y-%m-%d-%H-%M-%S"
        timestampStart_obj = datetime.strptime(timestampStart, timestamp_format)
        timestampStart_format = timestampStart_obj.strftime("%H:%M:%S")

        timestampEnd = datetime.strptime(timestamps[i], timestamp_format)
        timestampEnd_format = timestampEnd.strftime("%H:%M:%S")


        cv2.putText(image, timestampStart_format + ' =>' + timestampEnd_format, (1400, 1800), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 100, 100), 2, cv2.LINE_AA)
        

        for camera_metadata in camera_metadatas:
            # print('camera_metadata:', camera_metadata)
            camera = camera_metadata['camera']
            areas_of_interest = camera_metadata['areas_of_interest']

            for aoi_key, aoi_metadata in areas_of_interest.items():
                if 'processed' not in camera_metadata:
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('processed not in camera_metadata')
                    continue
                # aoi_coords = aoi_metadata['aoi_coords']
                # points = np.array(aoi_coords, np.int32)
                # points = points.reshape((-1, 1, 2))
                # cv2.polylines(image, [points], isClosed=True, color=AC_EDGE_COLOR, thickness=5)

                npOverviewCoords = None

                print('camera', camera)
                print('aoi_key', aoi_key)
                if camera not in ['3D1', 'Auto1', 'CeramicsJewelry2']:
                    continue

                if camera == '3D1':
                    if aoi_key == '1':
                        npOverviewCoords = np.array([[800, 1660], [800, 1780]], np.int32)
                elif camera == 'Auto1':
                    if aoi_key == '1':
                        npOverviewCoords = np.array([[1910, 600], [1910, 400]], np.int32)
                    elif aoi_key == '2':
                        npOverviewCoords = np.array([[1800, 600], [1800, 400]], np.int32)
                elif camera == 'CeramicsJewelry2':
                    if aoi_key == '1':
                        npOverviewCoords = np.array([[150, 530], [150, 740]], np.int32)
                    elif aoi_key == '2':
                        npOverviewCoords = np.array([[250, 530], [250, 740]], np.int32)


                if npOverviewCoords is None:
                    continue

                loiStart = (npOverviewCoords[0][0], npOverviewCoords[0][1])
                loiEnd = (npOverviewCoords[1][0], npOverviewCoords[1][1])
                cv2.arrowedLine(image, loiStart, loiEnd, (255, 0, 0),  5, cv2.FILLED, 0, 0.03)



                loiLocations_filtered = {}
                for loiTime, loiLocations in camera_metadata['processed'][aoi_key].items():
                    if loiTime > timestamps[i]:
                    # if loiTime <= '2024-03-16-18-45-06':
                        continue
                    for loiLocation in loiLocations:
                        loiLocation_filtered = round(loiLocation, FILTER)

                        if loiLocation_filtered not in loiLocations_filtered:
                            loiLocations_filtered[loiLocation_filtered] = 1
                        else:
                            loiLocations_filtered[loiLocation_filtered] += 1

                print('loiLocations_filtered')
                print(loiLocations_filtered)


                for loiLocation, count in loiLocations_filtered.items():
                    print(loiLocation)

                    # filter the location here
                    # print(round(0, -1))

                    # calculate the cartesian coordinates of the loiLocation
                    loiLocationX = npOverviewCoords[0][0] + (float(loiLocation) / 100) * (npOverviewCoords[1][0] - npOverviewCoords[0][0])
                    loiLocationY = npOverviewCoords[0][1] + (float(loiLocation) / 100) * (npOverviewCoords[1][1] - npOverviewCoords[0][1])


                    red = 50 + (5 * count)
                    if red > 200:
                        red = 200
                    red = 255-red
                    # cv2.circle(image, (int(loiLocationX), int(loiLocationY)), 10 * count, (50, 150, 255), -1)
                    cv2.circle(image, (int(loiLocationX), int(loiLocationY)), 5 + (2 * count), (0, 0, red), -1)


        cv2.imshow('Image', image)

        # out = imageOriginal.copy()
        # alpha = 0.5
        # mask = image.astype(bool)
        # out[mask] = cv2.addWeighted(imageOriginal, alpha, image, 1 - alpha, 0)[mask]
        # cv2.imshow('Image', imageOriginal)
        # cv2.imshow('Shapes', image)
        # cv2.imshow('Output', out)




        print('i', i)
        key = cv2.waitKey(0)
        if key == 2:
            print('Left arrow key pressed')
            cv2.destroyAllWindows()
            i = i - 1
            if i < 0:
                i = 0
            # break
        elif key == 3:
            i = i + 1 
            if i >= len(timestamps):
                i = len(timestamps) - 1
            print('Right arrow key pressed')
            cv2.destroyAllWindows()
            # break
        elif key == 27:
            cv2.destroyAllWindows()
            await db.close()
            print('Esc key pressed')
            exit()
        else:
            cv2.destroyAllWindows()
            await db.close()
            print('Key pressed:', key)
            exit()


if __name__ == '__main__':
    import asyncio
    asyncio.run(process())
