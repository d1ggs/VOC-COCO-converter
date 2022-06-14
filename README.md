# Annotations converter
A simple python script to convert XML-based Pascal VOC annotations to simplified COCO

## Task
Implement a python application that performs the following operations:
- read xml files
- parses the contents of these files
- resize images if dimensions exceed 800px (width) x 450px (height)
- save the final images in a dedicated folder to have a complete folder with all the images in their final version, whether they have been
resized or not
- recalculates the coordinates of the bounding boxes of annotated objects to adapt them to the new dimensions of the image, if it has been
resized
- composes an output file in json format and saves it to disk

## Data Format
The xml files contain the labeling data relating to a single image in Pascal VOC format.

It is required to merge these records into a single file in the simplified COCO format whose structure is shown below: