
import pprint
from ultralytics import YOLO
import cv2
import numpy as np
from utils.perpendicular import calcPerpendicularSlopeLineIntercept
import os
from surrealdb import Surreal


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


async def process():
    # Consts
    # dbTable = "ImageGroups"
    dbTable = "Laser1Processed"

    # connect to database
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")

    # add the laser1 metadata and structure to the database
    # await db.create(dbTable, imageGroup_laser1)

    # await db.close()
    # exit()


    # iterate through each image in laser1
    files = os.listdir(imagesDir)
    filesSorted = sorted(files)

    i = 0
    while i < len(filesSorted):
        file = filesSorted[i]

        image = cv2.imread(imagesDir + '/' + file)
        results = model(image)
        result = results[0]

        # Draw areas of interest on the image
        laserArea = imageGroup_laser1["areas"][0]["areaCoords"]
        points = np.array(laserArea, np.int32)
        points = points.reshape((-1, 1, 2))
        cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)

        # draw a line from the center of the top line to the center of the bottom line
        lineStartX = int((laserArea[0][0]+laserArea[1][0]) / 2)
        lineStartY = int((laserArea[0][1]+laserArea[1][1]) / 2)
        lineEndX = int((laserArea[2][0]+laserArea[3][0]) / 2)
        lineEndY = int((laserArea[2][1]+laserArea[3][1]) / 2) 

        lineStartingPoint2 = (lineStartX, lineStartY)   
        lineEndingPoint2 = (lineEndX, lineEndY)
        cv2.arrowedLine(image, lineStartingPoint2, lineEndingPoint2, (255, 0, 0), 5, cv2.FILLED, 0, 0.03)


        # find the slope intercept form of the line
        m = (lineEndY - lineStartY) / (lineEndX - lineStartX)
        b = lineStartY - (m * lineStartX)


        # Process for all bounding boxes
        # save to an object to store in db
        bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
        classes = np.array(result.boxes.cls.cpu(), dtype='int')
        fileDatetime = file.split("_", 1)[0]
        soiLocations = []

        for cls, bbox in zip(classes, bboxes):
            # only humans
            if cls != 0:
                continue
            x1, y1, x2, y2 = bbox
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # create a point at bottom center of bounding box
            xMiddleFloat = ((x2+x1)/2)
            bbX = int(xMiddleFloat)
            bbY = int(y2)

            # draw a dot at the center of the bottom of each bounding box
            cv2.circle(image, (bbX, bbY), 5, (0, 0, 255), -1)

            # determine if the dot is inside the laser area
            isInside = cv2.pointPolygonTest(points, (bbX, bbY), False)
            print('isInside:', isInside)

            if isInside == 1.0:
                # find perpendicular
                interceptX, interceptY = calcPerpendicularSlopeLineIntercept(m, b, bbX, bbY)
                interceptDot = [int(interceptX), int(interceptY)] #expecting this number
                interceptDotNp = np.array([interceptDot], np.int32)
                cv2.circle(image, (interceptDot[0], interceptDot[1]), 5, (100, 100, 255), -1)
                cv2.line(image, interceptDot, [bbX, bbY], (255, 0, 0), 5)


                # calculate percentage from beginning to end of Section Of Interest
                intInterceptX = int(interceptX)
                intInterceptY = int(interceptY)
                normalizedStart = lineStartX + lineStartY
                normalizedEnd = lineEndX + lineEndY
                normalizedIntercept = intInterceptX + intInterceptY
                linePercentageFromStart = (normalizedIntercept - normalizedStart) / (normalizedEnd - normalizedStart) * 100
                print('linePercentageFromStart', linePercentageFromStart)

                soiLocations.append(linePercentageFromStart)

        # don't create if already exists if in db already.
        # imageGroup_laser1 = {
        #     'imageGroup': imageGroup,
        #     'areas': [
        #         {
        #             'areaName': 'laser1',
        #         #                   tl          tr          bl           br
        #             'areaCoords': [[600, 380], [190, 430], [420, 1400], [1800, 1350]],
        #             'processed': []
        #         } 
        #     ]
        # }
        isExist = fileDatetime not in imageGroup_laser1['areas'][0]['processed']
        if (isExist):
            imageGroup_laser1['areas'][0]['processed'][fileDatetime] = {
                'soiLocations': soiLocations
            }
            print(fileDatetime + 'has been added')


        # show a smaller image
        # small = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
        # cv2.moveWindow('small image', 40, 30)
        # cv2.imshow('small image', small)

        print("file name is " + file)

        i = i + 1


        print(i-1, ' imageGroup_laser1')
        pprint.pprint(imageGroup_laser1)


        if (i >= 20):
            # await db.close()
            # exit()
            break

        # key = cv2.waitKey(0)
        # if key == 2:
        #     print('Left arrow key pressed')
        #     cv2.destroyAllWindows()
        #     i = i - 2
        #     if i < 0:
        #         i = 0
        # elif key == 3:
        #     print('Right arrow key pressed')
        #     cv2.destroyAllWindows()
        # elif key == 27:
        #     cv2.destroyAllWindows()
        #     await db.close()
        #     print('Esc key pressed')
        #     exit()
        # else:
        #     cv2.destroyAllWindows()
        #     await db.close()
        #     print('Key pressed:', key)
        #     exit()

    print('final imageGroup_laser1')
    pprint.pprint(imageGroup_laser1)

    await db.create(dbTable, imageGroup_laser1)

    await db.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(process())


# Wrap up notes
# creates an empty object and doesn't fetch if existing from db
# is limited to 20 images, can change
