#!/usr/bin/python3
# Aplicaiton for converting RGBA tiff to CMYK jpg, quickly
# Created by Mikeal Simburger (Simburger.com)
# Oct 24th 2020
# requires libjpeg-turbo https://sourceforge.net/projects/libjpeg-turbo/files
# requires libvips https://github.com/libvips/libvips/releases
# tested in windows python 3.8.6

from turbojpeg import TurboJPEG, TJPF_CMYK
from datetime import datetime
import argparse
import os
import time
import sys
import multiprocessing.pool
import numpy as np
import pyvips

# using default library installation
jpeg = TurboJPEG()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inpath", help="path to input file", type=str, required=True)
parser.add_argument("-o", "--outpath", help="path to output file", type=str, required=True)
parser.add_argument("-q", "--quality", help="jpeg quality value [0-100]", default=90, type=int)
parser.add_argument("-f", "--format", help="output format", choices=["j", "jpg", "t", "tif"], required=True)
parser.add_argument("-ov", "--overwrite", help="replace existing files", action='store_true')
parser.add_argument("-r","--recurse", help="include all sub dirrectories", action='store_true', default='false')
parser.add_argument("-cpu", "--cpu", help="Percent of threads to CPUs [150 - 25]", default='100', type=int)
# args are global
args = parser.parse_args()
args.to_jpg = False
if args.format == 'j' or args.format == "jpg":
    args.to_jpg = True

format_to_dtype = {
        'uchar': np.uint8,
        'char': np.int8,
        'ushort': np.uint16,
        'short': np.int16,
        'uint': np.uint32,
        'int': np.int32,
        'float': np.float32,
        'double': np.float64,
        'complex': np.complex64,
        'dpcomplex': np.complex128,
    }

def Convert2Jpg(data) -> bool:
    path = data[0]
    output_path = data[1]
    
    # check if should overwrite existing data
    if args.overwrite is False:
        if os.path.exists(output_path):
            print("\rOutput Exists: " + output_path)
            return False

    # if output sub folder does not exist make it
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # decoding jpg to BGR array
    try:
        image = pyvips.Image.new_from_file(path, access='sequential')
    except:
        print("\rError reading: " + path)
        return False

    mem_img = image.write_to_memory()
    output = np.frombuffer(
        mem_img, dtype=format_to_dtype[image.format]).reshape(
            image.height, image.width, image.bands)
    
    if image.format == "float" or image.format == "double":
        output = output * 255
            
    # only uint8 is supported by turbojpeg
    if image.format != "uchar":
        output = output.astype(np.uint8)
        
    try:
        out_file = open(output_path, 'wb')
        out_file.write(jpeg.encode(
            output, quality=args.quality, pixel_format=TJPF_CMYK))
        out_file.close()
    except:
        print("\rError writting: " + output_path, sys.exc_info())
        return False
    return True


def Convert2tiff(data) -> bool:
    path = data[0]
    output_path = data[1]
    # check if should overwrite existing data
    if args.overwrite is False:
        if os.path.exists(output_path):
            print("\rOutput Exists: " + output_path)
            return False

    # if output sub folder does not exist make it
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        in_file = open(path, 'rb')
        image = jpeg.decode(in_file.read(), pixel_format=TJPF_CMYK)
        in_file.close()
    except:
        print("\rError reading: " + path)
        return False
        
    image_out = pyvips.Image.new_from_memory(
        image, image.shape[1], image.shape[0], image.shape[2], 'uchar')
      
    try:
        image_out.write_to_file(output_path)
    except:
        print("\rError writing: " + output_path, sys.exc_info())
        return False
    return True


# show pool progress
# uses undocumented interal values, no other way for it to work
def TrackJobProgress(job, total_jobs, update_interval=2):
    start = datetime.now()
    total_jobs += 1
    while job._number_left > 0:
        pct_complated = int(((total_jobs - (job._number_left * job._chunksize))/total_jobs) * 100)
        pct_complated = max(0, pct_complated)
		# adjustment for actual typical performance, half the predicted
        pct_complated = int(pct_complated / 2)
        sys.stdout.write("\rProgress %d%%   " % pct_complated)
        # predict time left
        if pct_complated >= 5:
            pct_left = 100 - pct_complated
            durration = datetime.now() - start
            eta = datetime.now() + ((pct_left/100) * durration)
            f_eta = eta.strftime("%I:%M.%S %p") 
            sys.stdout.write("eta %s   " % str(f_eta))
        time.sleep(update_interval)

    # remove progress line
    columns, rows = os.get_terminal_size(1)
    string_val = " " * (columns - 1)
    sys.stdout.write('\r' + string_val + '\r')


# function for running jobs operation in parallel
def RunParallel(data, target):
    try:
        task_count = len(data)
        # set the number of threads from user input, min 1
        threads = max(1, int(multiprocessing.cpu_count() * (args.cpu / 100)))
        # a silly number of threads will not run any faster
        threads = min(multiprocessing.cpu_count() * 2, threads)
        p = multiprocessing.Pool(threads)
        results = []
        # restrict chunks from to 1 to 50 jobs,
        # targeting 5% of run when possible
        # so that most threads will compleate near same time
        # and less overhead for larger jobs
        chunk_size = min(max(1, int(task_count * .05)), 50)
        rs = p.map_async(
            target, data, callback=results.append, chunksize=chunk_size)
        # no more jobs can be submitted
        p.close()
        # show progress
        TrackJobProgress(rs, task_count)
        # close pool objects
        p.join()
    except: # catch *all* exceptions
        print("Error: ", sys.exc_info()[0])
        raise
    return results


# recursive function for finding all images to be processed
def GetFiles(source_folder, dest_folder, source_image_exention, results):
    for filename in os.listdir(source_folder):
        # looking for RGB jpgs
        if filename.lower().endswith(source_image_exention):
            image_path = source_folder + filename

            output_path = dest_folder + os.path.basename(filename)
            results.append([image_path, output_path])

        # recurse if user option
        if(args.recurse is True):
            if os.path.isdir(source_folder + filename):
                GetFiles(source_folder + filename + "\\",
                         dest_folder + filename + "\\",
                         source_image_exention, results)
            continue


def ToJpg(source_folder, dest_folder) -> bool:
    data = []
    GetFiles(source_folder, dest_folder, ".tif", data)
    
    results = RunParallel(data, Convert2Jpg)
    if (len(results) > 0):
        print("compleated: " + str(sum(results[0])) + " of " + str(len(data)))
    else:
        print("compleated: 0 of " + str(len(data)))
        return False
    return True


def ToTiff(source_folder, dest_folder) -> bool:
    data = []
    GetFiles(source_folder, dest_folder, ".jpg", data)

    results = RunParallel(data, Convert2tiff)
    if (len(results) > 0):
        print("compleated: " + str(sum(results[0])) + " of " + str(len(data)))
    else:
        print("compleated: 0 of " + str(len(data)))
        return False
    return True


def main():
    # bound input to good values
    quality_value = max(0, min(100, args.quality))
    if quality_value != args.quality:
        args.quality = quality_value
        print("using quality: " + str(args.quality))
        
    # has quotes
    if args.inpath[0] == '\"' and args.inpath.endswith('\"'):
        args.inpath = args.inpath[1:-1]

    if args.outpath[0] == '\"' and args.outpath.endswith('\"'):
        args.outpath = args.outpath[1:-1]

    # relative path with a leading slash
    if args.outpath[0] == '\\':
        args.outpath = args.outpath[1:]

    if args.inpath[0] == '\\':
        args.inpath = args.inpath[1:]
    
    # handle relative output paths
    if not os.path.isabs(args.outpath):
        args.outpath = os.getcwd() + "\\" + args.outpath
        
    if not os.path.exists(args.inpath):
        print("inpath does not exist")
        print("inpath: " + args.inpath)
        exit(1)
    
    startTime = datetime.now()
    if os.path.isdir(args.inpath):
        # folder in, folder out
        if not args.inpath.endswith("\\"):
            args.inpath = args.inpath + "\\"
        
        if not args.outpath.endswith("\\"):
            args.outpath = args.outpath + "\\"
            
        # if output folder does not exist make it
        if not os.path.exists(args.outpath):
            os.makedirs(args.outpath, exist_ok=True)

        if args.to_jpg is True:
            if not ToJpg(args.inpath, args.outpath):
                exit(1)
        else:
            if not ToTiff(args.inpath, args.outpath):
                exit(1)
                
    elif os.path.isfile(args.inpath):
        if os.path.isdir(args.outpath):
            # in file, out directory; keep input name
            output = args.outpath + os.path.basename(args.inpath)
            if args.to_jpg is True:
                if not Convert2Jpg([args.inpath, output]):
                    exit(1)
            else:
                if not Convert2tiff([args.inpath, output]):
                    exit(1)
        else:
            # in file, out file
            if args.to_jpg is True:
                if not Convert2Jpg([args.inpath, args.outpath]):
                    exit(1)
            else:
                if not Convert2tiff([args.inpath,  args.outpath]):
                    exit(1)
    else:
        print("\ninvalid inputs, does inpath exist?")
        print("inpath: " + args.inpath)
        print("outpath: rrr" + args.outpath)
        exit(1)

    print("\rOutput location: " + str(args.outpath))
    duration = datetime.now() - startTime
    # show h:mm::ss.ms
    print("Run Duration: " + str(duration)[:10])
    exit(0)


if __name__ == '__main__':
    main()
    