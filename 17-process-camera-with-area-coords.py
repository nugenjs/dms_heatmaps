
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

# ################################################################################################

async def process():
    # # Consts
    dbTable = "CameraMetadata"
    images_dir = 'images'

    # connect to database
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")


    camera_metadatas = await db.select(dbTable)
    for camera_metadata in camera_metadatas:
        print('camera_metadata:', camera_metadata)
        camera = camera_metadata['camera']
        areas_of_interest = camera_metadata['areas_of_interest']

        files = os.listdir(f'{images_dir}/{camera}')
        files_sorted = sorted(files)


        camera_metadata['processed'] = {}

        # iterate through each camera and add Line of Interest and slope intercept form to the metadata
        for aoi_key, aoi_metadata in areas_of_interest.items():
            aoi_coords = aoi_metadata['aoi_coords']

            # calculate the line of interest (loi) from the area_coords
            # draw a line from the center of the top line to the center of the bottom line
            lineStartX = int((aoi_coords[0][0]+aoi_coords[1][0]) / 2)
            lineStartY = int((aoi_coords[0][1]+aoi_coords[1][1]) / 2)
            lineEndX = int((aoi_coords[2][0]+aoi_coords[3][0]) / 2)
            lineEndY = int((aoi_coords[2][1]+aoi_coords[3][1]) / 2) 

            # save to an object to store in db
            aoi_metadata['loi_coords'] = {
                'start': (lineStartX, lineStartY),
                'end': (lineEndX, lineEndY)
            }
            
            # find the slope intercept form of the line of interest
            m = (lineEndY - lineStartY) / (lineEndX - lineStartX)
            b = lineStartY - (m * lineStartX)

            # save to an object to store in db
            aoi_metadata['loi_slope_intercept_form'] = {
                'm': m,
                'b': b
            }


        i = 0
        while i < len(files_sorted):
            file = files_sorted[i]

            print(f'{images_dir}/{camera}/{file}')

            image = cv2.imread(f'{images_dir}/{camera}/{file}')
            results = model(image)
            result = results[0]


            # Process for all bounding boxes
            # save to an object to store in db
            bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
            classes = np.array(result.boxes.cls.cpu(), dtype='int')
            fileDatetime = file.split("_", 1)[0]
            # dbRecord = {
            #     "datetime": fileDatetime,
            #     "soiLocation": {}
            # }

            found_person_in_any_aoi = False

            # for each bounding box
            for cls, bbox in zip(classes, bboxes):
                if cls != 0: # only humans
                    continue
                x1, y1, x2, y2 = bbox

                # draw bounding box
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # create a point at bottom center of bounding box
                xMiddleFloat = ((x2+x1)/2)
                bbX = int(xMiddleFloat)
                bbY = int(y2)
                # draw a dot at the center of the bottom of each bounding box
                cv2.circle(image, (bbX, bbY), 5, (0, 0, 255), -1)



                is_person_inside_aoi = False


                # for each area of interest
                for aoi_key, aoi_metadata in areas_of_interest.items():
                    print('aoi_key:', aoi_key)
                    aoi_coords = aoi_metadata['aoi_coords']
                    aoi_coords_np = np.array(aoi_coords, np.int32)
                    contour = aoi_coords_np.reshape((-1, 1, 2))
                    #  aoi_metadata['loi_slope_intercept_form'] = {
                    #     'm': m,
                    #     'b': b
                    # }
                    if aoi_key not in camera_metadata['processed']:
                        camera_metadata['processed'][aoi_key] = {}
                    if fileDatetime not in camera_metadata['processed'][aoi_key]:
                        camera_metadata['processed'][aoi_key][fileDatetime] = []


                                            
                    # determine if the dot is inside the laser area
                    isInside = cv2.pointPolygonTest(contour, (bbX, bbY), False)
                    print('isInside:', isInside)

                    if isInside == 1.0:
                        is_person_inside_aoi = True
                        # find perpendicular
                        m = aoi_metadata['loi_slope_intercept_form']['m']
                        b = aoi_metadata['loi_slope_intercept_form']['b']
                        interceptX, interceptY = calcPerpendicularSlopeLineIntercept(m, b, bbX, bbY)
                        interceptDot = [int(interceptX), int(interceptY)] #expecting this number
                        interceptDotNp = np.array([interceptDot], np.int32)
                        cv2.circle(image, (interceptDot[0], interceptDot[1]), 5, (100, 100, 255), -1)
                        cv2.line(image, interceptDot, [bbX, bbY], (255, 0, 0), 5)


                        # # # calculate the line of interest (loi) from the area_coords
                        # # # draw a line from the center of the top line to the center of the bottom line
                        # # lineStartX = int((aoi_coords[0][0]+aoi_coords[1][0]) / 2)
                        # # lineStartY = int((aoi_coords[0][1]+aoi_coords[1][1]) / 2)
                        # # lineEndX = int((aoi_coords[2][0]+aoi_coords[3][0]) / 2)
                        # # lineEndY = int((aoi_coords[2][1]+aoi_coords[3][1]) / 2) 

                        # # save to an object to store in db
                        # aoi_metadata['loi_coords'] = {
                        #     'start': (lineStartX, lineStartY),
                        #     'end': (lineEndX, lineEndY)
                        # }
                        (lineStartX, lineStartY) = aoi_metadata['loi_coords']['start']
                        (lineEndX, lineEndY) = aoi_metadata['loi_coords']['end']


                        # calculate percentage from beginning to end of Section Of Interest
                        intInterceptX = int(interceptX)
                        intInterceptY = int(interceptY)
                        normalizedStart = lineStartX + lineStartY
                        normalizedEnd = lineEndX + lineEndY
                        normalizedIntercept = intInterceptX + intInterceptY
                        linePercentageFromStart = (normalizedIntercept - normalizedStart) / (normalizedEnd - normalizedStart) * 100
                        print('linePercentageFromStart', linePercentageFromStart)

                        # save to an object to store in db
                        camera_metadata['processed'][aoi_key][fileDatetime].append(linePercentageFromStart)

                        # dbRecord["soiLocation"][aoi_key] = []

                        # dbRecord["soiLocation"][aoi_key].append(linePercentageFromStart)
                    
                    # person can only be in one aoi
                    if is_person_inside_aoi:
                        found_person_in_any_aoi = True
                        break


            if found_person_in_any_aoi:
            # if False:
                # iterate through each camera and add Line of Interest and slope intercept form to the metadata
                for aoi_key, aoi_metadata in areas_of_interest.items():
                    aoi_coords = aoi_metadata['aoi_coords']
                    points = np.array(aoi_coords, np.int32)
                    points = points.reshape((-1, 1, 2))
                    cv2.polylines(image, [points], isClosed=True, color=AC_EDGE_COLOR, thickness=5)

                    # save to an object to store in db
                    line_of_interest_start = aoi_metadata['loi_coords']['start']
                    line_of_interest_end = aoi_metadata['loi_coords']['end']

                    cv2.arrowedLine(image, line_of_interest_start, line_of_interest_end, AC_ARROW_COLOR, AC_CORNER_CIRCLE_RADIUS, cv2.FILLED, 0, 0.03)

                    # write the area_coords key next to the top left corner
                    cv2.putText(image, aoi_key, (aoi_coords[0][0], aoi_coords[0][1] + AC_CORNER_CIRCLE_RADIUS + AC_LABEL_Y_OFFSET), cv2.FONT_HERSHEY_SIMPLEX, 2, AC_LABEL_COLOR, 2, cv2.LINE_AA)

                # show a smaller image
                small = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
                cv2.moveWindow('small image', 40, 30)
                cv2.imshow('small image', small)

                print("file name is " + file)


                while True:
                    key = cv2.waitKey(0)
                    if key == 2:
                        print('Left arrow key pressed')
                        cv2.destroyAllWindows()
                        i = i - 1
                        if i < 0:
                            i = 0
                        break
                    elif key == 3:
                        i = i + 1 
                        if i >= len(files_sorted):
                            i = len(files_sorted) - 1
                        print('Right arrow key pressed')
                        cv2.destroyAllWindows()
                        break
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

            else:
                i = i + 1

        # camera_metadata
        res = await db.update(f'{dbTable}:{camera}', camera_metadata)
        # if res['status'] == 'success':
        #     print('camera_metadata updated')


    await db.close()





if __name__ == '__main__':
    import asyncio
    asyncio.run(process())


# Wrap up notes
# creates an empty object and doesn't fetch if existing from db
# is limited to 20 images, can change
