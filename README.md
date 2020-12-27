# RGBA_tiff_to_jpg
4 Band tiff to CMYK jpg to preserve 4 channels as a jpg and reverse, using fast libraries<br/>
  Created to compress 4 band tiffs for ftp while still being an easly viewable format, CMYK jpgs can be more effeciant than 2 jpgs if done well. 

This should be about 3.5 times faster than compairable imagemagick scripts<br/>

# To use:<pre>
  -h, --help            show this help message and exit<br/>
  -i INPATH, --inpath INPATH<br/>
    path to input file or folder<br/>
  -o OUTPATH, --outpath OUTPATH<br/>
                        path to output file or folder<br/>
  -q QUALITY, --quality QUALITY<br/>
                        jpeg quality value [0-100]<br/>
  -f {j,jpg,t,tif}, --format {j,jpg,t,tif}<br/>
                        output format<br/>
  -ov, --overwrite      replace existing files<br/>
  -r, --recurse         include all sub dirrectories<br/>
  -cpu CPU, --cpu CPU   Percent of threads to CPUs [150 - 25]<br/>
</pre>

# Install:
  requires python 64bit, tested with 3.8.6

  install libjpeg-turbo<br/>
  https://sourceforge.net/projects/libjpeg-turbo/files/<br/>

  install vips lib<br/>
  https://github.com/libvips/libvips/releases<br/>
  add vips\bin to system path (restart recomended)<br/>

  pip install -r requirements.txt<br/>
