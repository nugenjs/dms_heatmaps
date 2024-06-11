
# from ultralytics import YOLO
from pprint import pprint
import cv2
import numpy as np
from utils.perpendicular import calcPerpendicularSlopeLineIntercept
import os
from surrealdb import Surreal

from image_contants import laser1_areas

async def process():
    # Consts
    # dbTable = "ImageGroups"
    dbTable = "Laser1Processed"

    # connect to database
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")

    imagesDir = 'images'
    image = cv2.imread(f'{imagesDir}/layout_overview.png')



    # Laser1 Specific

    # laserArea = laser1_areas['laser1']['areaCoords']
    # nppoints = np.array(laserArea, np.int32)
    # points = nppoints.reshape((-1, 1, 2))
    # cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)


    npLaser1OverviewCoords = np.array(laser1_areas['laser1']['overviewCoords'], np.int32)
    soiStart = (npLaser1OverviewCoords[0][0], npLaser1OverviewCoords[0][1])
    soiEnd = (npLaser1OverviewCoords[1][0], npLaser1OverviewCoords[1][1])
    cv2.arrowedLine(image, soiStart, soiEnd, (255, 0, 0),  5, cv2.FILLED, 0, 0.03)


    # laser1ProcessedRes = await db.select(f'Laser1Processed:p9ulwr3vh9p5jgh9q5jy')
    laser1ProcessedRes = await db.query(f'SELECT * FROM Laser1Processed WHERE imageGroup = "Laser1"')
    laser1ProcessedRes = laser1ProcessedRes[0]['result'][0]

    pprint(laser1ProcessedRes)

    laser1Processed = laser1ProcessedRes['areas'][0]['processed']

    pprint(laser1Processed)





    # ################################################ test

    soiLocations = laser1Processed['2024-03-16-16-55-56']['soiLocations']
    filter = -1 # could be -2 or 0 or others

    soiLocations_filtered = {}
    for soiLocation in soiLocations:
        soiLocation_filtered = round(soiLocation, filter)

        if soiLocation_filtered not in soiLocations_filtered:
            soiLocations_filtered[soiLocation_filtered] = 1
        else:
            soiLocations_filtered[soiLocation_filtered] += 1
        # print('soiLocations_filtered[soiLocation_filtered]')
        # print(soiLocations_filtered[soiLocation_filtered])
        # if(soiLocations_filtered[soiLocation_filtered]):
        #     soiLocations_filtered[soiLocation_filtered] += 1
        # else:
        #     soiLocations_filtered[soiLocation_filtered] = 1
    
    print('soiLocations_filtered')
    for soiLocation, count in soiLocations_filtered.items():
        print(soiLocation)

        # filter the location here
        # print(round(0, -1))

        # calculate the cartesian coordinates of the soiLocation
        soiLocationX = npLaser1OverviewCoords[0][0] + (float(soiLocation) / 100) * (npLaser1OverviewCoords[1][0] - npLaser1OverviewCoords[0][0])
        soiLocationY = npLaser1OverviewCoords[0][1] + (float(soiLocation) / 100) * (npLaser1OverviewCoords[1][1] - npLaser1OverviewCoords[0][1])

        print('soiLocationX', soiLocationX)
        print('soiLocationY', soiLocationY)

        cv2.circle(image, (int(soiLocationX), int(soiLocationY)), 10 * count, (50, 150, 255), -1)



    # show a smaller image
    small = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
    cv2.moveWindow('small image', 40, 30)
    cv2.imshow('small image', small)


    key = cv2.waitKey(0)
    if key == 27:
        cv2.destroyAllWindows()
        print('Esc key pressed')
        # exit()
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

    print('closing db')
    await db.close()
    print('db closed')


if __name__ == '__main__':
    import asyncio
    asyncio.run(process())



# files = os.listdir(imagesDir)
# filesSorted = sorted(files)


# i = 0
# while i < len(filesSorted):
#     file = filesSorted[i]

#     image = cv2.imread(imagesDir + '/' + file)
#     results = model(image)
#     result = results[0]



#     # Draw areas of interest on the image
#     #                   tl              tr          bl             br
#     # laserArea = [[600, 380], [190, 430], [420, 1400], [1800, 1350]]
#     laserArea = laser1_areas['laser1']['areaCoords']
#     points = np.array(laserArea, np.int32)
#     points = points.reshape((-1, 1, 2))
#     cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)

#     # draw a line from the center of the top line to the center of the bottom line
#     lineStartX = int((laserArea[0][0]+laserArea[1][0]) / 2)
#     lineStartY = int((laserArea[0][1]+laserArea[1][1]) / 2)
#     lineEndX = int((laserArea[2][0]+laserArea[3][0]) / 2)
#     lineEndY = int((laserArea[2][1]+laserArea[3][1]) / 2) 

#     lineStartingPoint2 = (lineStartX, lineStartY)   
#     lineEndingPoint2 = (lineEndX, lineEndY)
#     cv2.arrowedLine(image, lineStartingPoint2, lineEndingPoint2, (255, 0, 0), 5, cv2.FILLED, 0, 0.03)


#     # find the slope intercept form of the line
#     m = (lineEndY - lineStartY) / (lineEndX - lineStartX)
#     b = lineStartY - (m * lineStartX)


#     # Process for all bounding boxes
#     bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
#     classes = np.array(result.boxes.cls.cpu(), dtype='int')

#     for cls, bbox in zip(classes, bboxes):
#         # only humans
#         if cls != 0:
#             continue
#         x1, y1, x2, y2 = bbox
#         cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

#         # create a point at bottom center of bounding box
#         xMiddleFloat = ((x2+x1)/2)
#         bbX = int(xMiddleFloat)
#         bbY = int(y2)

#         # draw a dot at the center of the bottom of each bounding box
#         cv2.circle(image, (bbX, bbY), 5, (0, 0, 255), -1)

#         # determine if the dot is inside the laser area
#         isInside = cv2.pointPolygonTest(points, (bbX, bbY), False)
#         print('isInside:', isInside)

#         if isInside == 1.0:
#             # find perpendicular
#             interceptX, interceptY = calcPerpendicularSlopeLineIntercept(m, b, bbX, bbY)
#             interceptDot = [int(interceptX), int(interceptY)] #expecting this number
#             interceptDotNp = np.array([interceptDot], np.int32)
#             cv2.circle(image, (interceptDot[0], interceptDot[1]), 5, (100, 100, 255), -1)
#             cv2.line(image, interceptDot, [bbX, bbY], (255, 0, 0), 5)


#             # calculate percentage from beginning to end of line of interest
#             intInterceptX = int(interceptX)
#             intInterceptY = int(interceptY)
#             normalizedStart = lineStartX + lineStartY
#             normalizedEnd = lineEndX + lineEndY
#             normalizedIntercept = intInterceptX + intInterceptY
#             linePercentageFromStart = (normalizedIntercept - normalizedStart) / (normalizedEnd - normalizedStart) * 100
#             print('linePercentageFromStart', linePercentageFromStart)

#     # show a smaller image
#     small = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
#     cv2.moveWindow('small image', 40, 30)
#     cv2.imshow('small image', small)


#     i = i + 1

#     key = cv2.waitKey(0)
#     if key == 27:
#         cv2.destroyAllWindows()
#         print('Esc key pressed')
#         exit()
#     elif key == 2:
#         print('Left arrow key pressed')
#         cv2.destroyAllWindows()
        
#         i = i - 2
#         if i < 0:
#             i = 0
#     elif key == 3:
#         print('Right arrow key pressed')
#         cv2.destroyAllWindows()
#     else:
#         print('Key pressed:', key)
#         cv2.destroyAllWindows()


