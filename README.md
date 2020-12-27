# RGBA_tiff_to_jpg
4 Band tiff to CMYK jpg to preserve 4 channels as a jpg and reverse, using fast libraries
  Created to compress 4 band tiffs for ftp while still being an easly viewable format, CMYK jpgs can be more effeciant than 2 jpgs if done well. 

This should be about 3.5 times faster than compairable imagemagick scripts

To use:
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        path to input file or folder
  -o OUTPATH, --outpath OUTPATH
                        path to output file or folder
  -q QUALITY, --quality QUALITY
                        jpeg quality value [0-100]
  -f {j,jpg,t,tif}, --format {j,jpg,t,tif}
                        output format
  -ov, --overwrite      replace existing files
  -r, --recurse         include all sub dirrectories
  -cpu CPU, --cpu CPU   Percent of threads to CPUs [150 - 25]

Install:
  requires python 64bit, tested with 3.8.6

  install libjpeg-turbo
  https://sourceforge.net/projects/libjpeg-turbo/files/

  install vips lib
  https://github.com/libvips/libvips/releases
  add vips\bin to system path (restart recomended)

  pip install -r requirements.txt

requirements:
  argparse
  numpy==1.19.3
  PyTurboJPEG>=1.4.1
  pyvips>=2.1.13
