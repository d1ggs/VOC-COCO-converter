import argparse
import json
import os
import shutil
from math import floor, ceil
from xml.etree import ElementTree as ET

import xmltodict
from PIL import Image
from PIL.Image import Resampling

TARGET_WIDTH = 800
TARGET_HEIGHT = 450

# Add the parser arguments, default use folders in the project directory
parser = argparse.ArgumentParser(description='Convert image annotation format')
parser.add_argument('--imagedir', type=str, default='images',
                    help='path to the folder with images')
parser.add_argument('--xmldir', type=str, default='xmldata',
                    help='path to the folder with the xml files '
                         'with the original labeling data')
parser.add_argument('--outputdir', type=str, default='output',
                    help='path to the output folder where the images '
                         'and the produced json file will be saved')

args = parser.parse_args()

result_dict = {}

# For each XML file compute whether the resize is needed
for file in os.scandir(args.xmldir):

    # Build a DOM tree of the XML file for easy access
    tree = ET.parse(file.path)
    root = tree.getroot()
    size_node = root.find('size')

    width = int(size_node.find('width').text)
    height = int(size_node.find('height').text)

    # The path in the annotations might not correspond if
    # the script is executed on a different machine
    image_path = root.find('path').text
    image_name = image_path.split('/')[-1]
    actual_image_path = os.path.join(args.imagedir, image_name)
    image_output_path = os.path.join(args.outputdir, image_name)

    # Replace the old path with the new path
    root.find('path').text = image_output_path

    # Copy the images, we will edit them directly in the destination folder
    shutil.copyfile(actual_image_path, image_output_path)

    # If the dimensions are not correct, resize the image
    if width > 800 or height > 450:

        img = Image.open(image_output_path)

        # Preserve the aspect ratio to preserve
        # spatial information about features

        # Try computing the resize over x axis first
        w_size = TARGET_WIDTH
        w_percent = (TARGET_WIDTH / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))

        # If the height still doesn't fit the desired dimension,
        # use the y axis as main resize axis
        if h_size > 450:
            h_size = TARGET_HEIGHT
            h_percent = (h_size / float(img.size[1]))
            w_size = int((float(img.size[0]) * float(h_percent)))

        # Apply the scaling with pillow, then compute the scale
        # factors for the single axes independently
        img = img.resize((w_size, h_size), Resampling.LANCZOS)
        w_scale = img.size[0] / float(width)
        h_scale = img.size[1] / float(height)

        # Update the XML with the new image size
        size_node.find('width').text = str(img.size[0])
        size_node.find('height').text = str(img.size[1])

        # Move the corners of the bounding boxes in the XML
        for obj_node in root.findall('object'):
            bndbox_node = obj_node.find('bndbox')
            xmin_node = bndbox_node.find('xmin')
            xmax_node = bndbox_node.find('xmax')
            ymin_node = bndbox_node.find('ymin')
            ymax_node = bndbox_node.find('ymax')

            xmin_node.text = str(floor(int(xmin_node.text) * w_scale))
            xmax_node.text = str(ceil(int(xmax_node.text) * w_scale))
            ymin_node.text = str(floor(int(ymin_node.text) * h_scale))
            ymax_node.text = str(ceil(int(ymax_node.text) * h_scale))

        # Save the resized image
        img.save(image_output_path)

    # The xml tree can easily converted into a string,
    # then parsed into a dict for simpler JSON conversion
    tree_dict = xmltodict.parse(ET.tostring(root))
    result_dict[file.name] = tree_dict

# JSON-dump each annotation in a single file, using the old file name as key
with open(os.path.join(args.outputdir, 'annotations.json'), 'w') as json_out:
    json.dump(result_dict, json_out, sort_keys=True, indent=4)

# TODO this was not the required output format, it is needed to pull COCO categories
#  and map the Pascal VOC categories onto these
