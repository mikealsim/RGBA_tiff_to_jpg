# RGBA_tiff_to_jpg
4 Band tiff to CMYK jpg to preserve 4 channels @ 8 bit as a jpg and the reverse process, using fast libraries TurboJpeg and vips. Created to compress 4 band tiffs for ftp while still being an easly viewable format, CMYK jpgs can are more effeciant than 2 jpgs. 

While the jpg is stored as CMYK the chanels are not changed. <br>
  R=C<br>
  G=M<br>
  B=Y<br>
  A=K<br>

This should be about 3.5 times faster than compairable imagemagick scripts<br/>

# To use:
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

# Install:
  requires python 64bit, tested with 3.8.6

  install libjpeg-turbo<br/>
  https://sourceforge.net/projects/libjpeg-turbo/files/<br/>

  install vips lib<br/>
  https://github.com/libvips/libvips/releases<br/>
  add vips\bin to system path (restart recomended)<br/>

  pip install -r requirements.txt<br/>
