# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 09:53:17 2020

@author: Patrick.Barry
"""
import os
from PIL import Image
import image_slicer_main
import Vid_maker

def politely_request(i):
    """ask for the file to be used a frame, one at a time, in order"""
    print('Image ', i, ': name is ')
    target_filename = input()
    return target_filename

def check_images_same_size(filenames):
    """check the size of each image,
    could be context sensitive to ignore white space
    #currently just steps through and returns max size"""
    max_H = 0
    max_V = 0
    for f in filenames:
        im = Image.open(f)
        ims = im.size #(width, height) tuple
        if ims[0] > max_H:
            max_H = ims[0]
        if ims[1] >> max_V:
            max_V = ims[1]
    max_dim = (max_H, max_V)
    return max_dim

def make_images_same_size(filenames, max_dim):
    """takes images, place on common center point
    NOT top left corner
    and pad with white space to suit"""
    filenames_new = []
    for name in filenames:
        padded = Image.new('RGBA', max_dim, (255, 255, 255, 0))
        im = Image.open(name)
        ims = im.size #(width, height) tuple
        X_offset = int(0 + (max_dim[0]-ims[0])/2)
        Y_offset = int(0+ (max_dim[1] -ims[1])/2)
        padded.paste(im, (X_offset, Y_offset))
        new_name = "padded_" + name[:-4] + ".png"  
        # add _ to newname to have these files autodeleted. See tidy_up()
        padded.save(os.path.join(os.getcwd(), new_name))
        filenames_new.append(new_name)
    return filenames_new

def make_barrier(big_size, number_of_frames, number_bars, vertical):
    """make the barrier image using black and transparent sections"""
    number_tiles = number_bars *number_of_frames
    if vertical is True:
        stripsize = (int(big_size[0]/number_tiles), int(big_size[1])) #tuple
        dx = 1
        dy = 0
    else:
        stripsize = (int(big_size[0]), int(big_size[1]/number_tiles))
        dx = 0
        dy = 1
    #print(stripsize, big_size, number_bars, vertical)
    dark_bit = Image.new('RGBA', stripsize, (0, 0, 0, 255))
    clear_bit = Image.new('RGBA', stripsize, (0, 0, 0, 0))
    seed = Image.new('RGBA', big_size, (100, 0, 0, 0))  #red box that's fully transparent
    for i in range(0, number_tiles, number_of_frames):
        for j in range(0, number_of_frames-1):
            coord_tuple1 = ((i+j)*stripsize[0]*dx, (i+j)*stripsize[1]*dy)
            seed.paste(dark_bit, coord_tuple1)
        coord_tuple2 = ((i+number_of_frames)*stripsize[0]*dx, (i+number_of_frames)*stripsize[1]*dy)
        seed.paste(clear_bit, coord_tuple2)
        #print(coord_tuple1, coord_tuple2)
    seed.save(os.path.join(os.getcwd(), "000_barrier.png"))
    return stripsize

def make_output(zipped, max_dim, Vertical):
    """make background image from the list of strips to glue together"""
    X_offset = 0
    Y_offset = 0
    output = Image.new('RGBA', max_dim, (255, 255, 255, 0))
    for name in zipped:
       # im=Image.open(name.generate_filename)
        output.paste(name.image, (X_offset, Y_offset))
        ims = name.image.size
        #print(ims)
        if Vertical is True:
            X_offset = int(X_offset +ims[0])
        else:
            Y_offset = int(Y_offset +ims[1])
    new_name = "000_output.png"
    output.save(os.path.join(os.getcwd(), new_name))
    return

def make_video(seconds, fps=10, barfilename="000_barrier.png", backfilename="000_output.png", Vertical=True):
    """make series of frames by pasting barrier over background at different offsets
    default fps of 10 is for draftin video. more fps needed for smooth results"""
    print('Making video')
    total_frame_count = seconds*fps
    framenames = []
    barim = Image.open(barfilename)
    backim = Image.open(backfilename)
    back_size = backim.size
    offset = [0, 0]
    for i in range(total_frame_count):
        if Vertical is True:
            offset_step = (int(back_size[0]*2/total_frame_count), 0)
            realign_step = (back_size[0], 0)
            static_backim = Image.new('RGBA', (back_size[0]*3, back_size[1]), (0, 0, 0, 0))
            moving_bars = Image.new('RGBA', (back_size[0]*3, back_size[1]), (0, 0, 0, 0))
        else:
            offset_step = (0, int(back_size[1]*2/total_frame_count))
            realign_step = (0, back_size[1])
            static_backim = Image.new('RGBA', (back_size[0], back_size[1]*3), (0, 0, 0, 0))
            moving_bars = Image.new('RGBA', (back_size[0], back_size[1]*3), (0, 0, 0, 0))
        static_backim.paste(backim, realign_step)
        moving_bars.paste(barim, offset)
        offset = [offset[0] + offset_step[0], offset[1] + offset_step[1]]
        frame = Image.composite(moving_bars, static_backim, moving_bars)
        new_name = "frame_"+str(i)+".png"
        framenames.append(new_name)
        frame.save(os.path.join(os.getcwd(), new_name))
    print('Frames are created, starting the video stich')
    Vid_maker.vid_stitch(framenames, fps)
    tidy_up()
    return



def tidy_up(): # modified from image_slicer open_images fuctnion
    """Delete all temp files created by the _ marker in name
    could be a bit more discriminating"""
    directory = os.getcwd()
    files = [filename for filename in os.listdir(directory)
             if '_' in filename and not filename.startswith('000') and not '.py' in filename]
    if files:
        for file in files:
            try:
                os.remove(file)
            except:
                pass
    return


def kinegram(number_of_frames, number_bars, vertical=True):
    """main function, when called will gather inputs and produce solved images"""
    filenames = []
    sliced_images = []

    #get setup, get images, size em all to match
    for image_name in range(1, number_of_frames + 1):
        namestr = politely_request(image_name)
        filenames.append(namestr)

    true_size = check_images_same_size(filenames)
    filenames = make_images_same_size(filenames, true_size)
    number_tiles = number_bars *number_of_frames

    if vertical is True:
        if true_size[0]/number_tiles < 3:
            print("WARNING. SLICED TOO THIN")
    else:
        if true_size[1]/number_tiles < 3:
            print("WARNING. SLICED TOO THIN")

    # make the barrier image
    strip_size = make_barrier(true_size, number_of_frames, number_bars, vertical)
    #hold stripsize in memory for validation function

    #slice image and save
    for img in filenames:
        if vertical is True:
            tiles = image_slicer_main.slice(img, number_tiles, 1)
        else:
            tiles = image_slicer_main.slice(img, 1, number_tiles)
    #creates the files, and creates a tuple of image_slicer tile class instances
        sliced_images.append(tiles)

    #glue back together
    zipped_images = []
    branch = 0
    for j in range(0, number_tiles):  #-2*(number_of_frames-1)
        #print("t=", sliced_images[branch], j)
        try:
            t = sliced_images[branch][j]
            zipped_images.append(t)
        except IndexError:
            print("dropped ", 'branch:', branch, 'j', j, len(sliced_images[branch]), number_tiles)
        branch = branch + 1
        if branch > len(filenames)-1: # 1 item list indexes to zero
            branch = 0

        #print(t, branch-1, j)
    #print(zipped_images)

    make_output(zipped_images, true_size, vertical)

    #delete_all_remaining_files
    tidy_up()
    print("kinegram complete")
    return(strip_size, number_of_frames)
    # (format [d(dim1,dim2) number_of_frames] return keeps them in memory for validation


def archi_validate(strip_size, backfilename="000_output.png"):
    """uses inputs to return real world dims
    COULD read in strip size from barrier by counting pixels.
    this would validate the produced design, not the expected one
    but this input based approach allows future changes
    to barrier style without hidden dependencies"""
    backim = Image.open(backfilename)
    back_size = backim.size
    dims = [back_size[0], back_size[1], strip_size[0][0], strip_size[0][1]]
    bar_size = min(dims[2], dims[3])*strip_size[1] #open strip width* number of frames
    dims.append(bar_size)

    print("Back Image size in pixels: ", back_size)
    print("Open Strip in barrier is: ", strip_size[0])
    print("block strip in barrier is: ", dims[4])
    print("calibration to mm")
    print("For dim 1-5, type in 'the number of the dim, enter")
    dim_id = int(input())-1  #index to zero
    print("that is ", dims[dim_id], ", now the desired length in mm")

    leng = float(input())
    scaling_factor = float(leng/dims[dim_id])
    real_dims = []
    for d in dims:
        newd = int(d)*scaling_factor
        real_dims.append(newd)
    print("Back Image size in millimeters: ", real_dims[0], real_dims[1])
    print("Open Strip in barrier is: ", real_dims[2], real_dims[3])
    print("Block strip in barrier is", real_dims[4])
    print("and basic front on, no depth perspective bar offset is",
          real_dims[4] + min(real_dims[2], real_dims[3]))
        
