# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 14:01:08 2020

@author: #http://tsaith.github.io/combine-images-into-a-video-with-python-3-and-opencv-3.html
"""

import cv2
import argparse
import os

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-ext", "--extension", required=False, default='png', help="extension name. default is 'png'.")
ap.add_argument("-o", "--output", required=False, default='000_output.mp4', help="output video file")
args = vars(ap.parse_args())

# Arguments
dir_path = '.'
ext = args['extension']
output = args['output']

def vid_stitch(images, fps=20):
    if images == []:
        for f in os.listdir(dir_path):
            if f.endswith(ext):
                images.append(f)
    
    # Determine the width and height from the first image
    image_path = os.path.join(dir_path, images[0])
    frame = cv2.imread(image_path)
    cv2.imshow('video',frame)
    height, width, channels = frame.shape
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Be sure to use lower case
    out = cv2.VideoWriter(output, fourcc, fps, (width, height))
    
    for image in images:
    
        image_path = os.path.join(dir_path, image)
        frame = cv2.imread(image_path)
    
        out.write(frame) # Write out frame to video
    
        cv2.imshow('video',frame)
        if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
            break
    
    # Release everything if job is finished
    out.release()
    cv2.destroyAllWindows()
    
    print("The output video is {}".format(output))
    
if __name__ == "__main__":
    images=[]
    vid_stitch(images)