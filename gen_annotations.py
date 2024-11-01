#!/usr/bin/env python
# -----------------------------------------------------------------------------
# File:         gen_annotations.py
# Author:       steven
# Email:        coder.wine@gmail.com
# Description:  provide extreamly easy-to-use, effective and efficient tools (X3ET)
# Created:      20241030
# Updated:      20241030
# Version:      1.0.0
# -----------------------------------------------------------------------------

import os
import json
from PIL import Image

datasets_dir="datasets"

def create_coco_annotations(image_dir, label_dir):
    # Initialize COCO annotation structure
    coco_format = {
        "info": {
            "year": 2024,
            "version": "1.0",
            "description": "COCO128 Dataset",
            "contributor": "Generated",
            "date_created": "2024"
        },
        "licenses": [
            {
                "id": 1,
                "name": "Attribution-NonCommercial",
                "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
            }
        ],
        "categories": [
            {"id": i, "name": str(i), "supercategory": "none"} for i in range(80)
        ],
        "images": [],
        "annotations": []
    }

    annotation_id = 0

    # Process each image and its corresponding label file
    for img_file in sorted(os.listdir(image_dir)):
        if not img_file.endswith('.jpg'):
            continue

        # Get image info
        img_path = os.path.join(image_dir, img_file)
        img = Image.open(img_path)
        width, height = img.size

        image_id = int(img_file.split('.')[0])

        # Add image info
        image_info = {
            "id": image_id,
            "file_name": img_file,
            "height": height,
            "width": width,
            "date_captured": "2024"
        }
        coco_format["images"].append(image_info)

        # Process corresponding label file
        txt_file = img_file.replace('.jpg', '.txt')
        txt_path = os.path.join(label_dir, txt_file)

        if os.path.exists(txt_path):
            with open(txt_path, 'r') as f:
                for line in f:
                    category_id, x_center, y_center, w, h = map(float, line.strip().split())

                    # Convert YOLO format to COCO format
                    x = (x_center - w/2) * width
                    y = (y_center - h/2) * height
                    w = w * width
                    h = h * height

                    annotation = {
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": int(category_id),
                        "bbox": [x, y, w, h],
                        "area": w * h,
                        "segmentation": [],
                        "iscrowd": 0
                    }

                    coco_format["annotations"].append(annotation)
                    annotation_id += 1

    return coco_format

# Create annotations
image_dir = datasets_dir + "/coco128/images/train2017"
label_dir = datasets_dir + "/coco128/labels/train2017"
annotations_dir = datasets_dir + "/coco128/annotations"

annotations = create_coco_annotations(image_dir, label_dir)

# Save to JSON file
os.makedirs(annotations_dir, exist_ok=True)
with open(f"{annotations_dir}/instances_train2017.json", 'w') as f:
    json.dump(annotations, f)