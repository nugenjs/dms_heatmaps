# Tech Used
- Python (Conda, CV2, YOLO)
- SurrealDB

# Definitions
**Box Of Interest**: a quadrilateral that annotates a section in a camera view.  
**Section Of Interest**: section/line in quadrilateral, as a 1D representation of BOI that can be mapped to overview map easily.

# File Explainations
### 05-added-image-array
- use yolo
- bounding box
- added images to an array
- added left right button controls

### 06-is-in-quad
- check if a point is in a quadrilateral

### 07-on-line-location
- draw a middle line on a quadrilateral
- draw a point
- draws a perpendicular line to the middle line that connects to a point
- gets the x y corrdinates on line

### 08-perpen-bounding-box
- yolo image detection on multiple bounding boxes
- calculates perpendicular to SOI
- normalizes the intercept to the SOI to a 1D array

### 09-15-set-area-coords-for-each-camera.py
- calculates perpendicular to SOI on all images in Camera group
- testing db select, update, create, query
- saving perpendicular SOI results to db with hardcoded SOI
- allow mouse events to allow modifications of SOI

### 16-OLD-set-multi-area-coords-for-each-camera.py
- adf

### 16-set-multi-area-coords-for-each-camera.py
- adf

### 17-process-camera-with-area-coords.py
- adf

### 18-set-loi-coords-for-overview.py
- adf



# Others
Install SurrealDB  
`brew install surrealdb/tap/surreal`  
`surreal start memory -A --auth --user root --pass root`



# TODO
- if multiple points are on the same on line locations
  - add a counter or ignore and only count 1
- save on line locations to a db
- correct image distortion for DMS overview map
- draw dots onto map
- add a way to view certain time frames
  - find tool usage at time of day
  - area of most traffic of entire day
  - heatmap of entire day