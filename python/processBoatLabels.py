from spaceNet import labelTools as lT
from spaceNet import dataTools as dT
import numpy as np
import argparse
import os

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create Object Classification Dataset'
                                                 'Supply Raster Image and GeoJson'
                                                 'Program will cut a box with 30% buffer around the supplied features'
                                                 'envelope.')
    parser.add_argument("rasterSrc", help="raster to chip")
    parser.add_argument("objectSrc", help="geoJSON of object Labels")
    parser.add_argument("outputDirectory", help="Location To place chipped files")
    parser.add_argument("--imgSize",
                        help="set the pixel dimension of the square image.  "
                             "Default is 256pixels"
                             "Set to -1 for the images to not be resized",
                        type=int)

    parser.add_argument("--rotationStep",
                        help="Augment dataset by rotating images about the unit circle at X degree increments"
                             "rotationList = np.arange(0,360, rotationStep)"
                             "Default is No Rotation",
                        type=float)






    args = parser.parse_args()

    rasterFileName = args.rasterSrc

    objectSrc = args.objectSrc
    clipSize = args.clipSize
    outputDirectory = args.outputDirectory
    if args.imgSize:
        finalImageSize = args.imgSize
    else:
        finalImageSize = 256

    if args.rotationStep:
        rotationList = np.arange(0, 360, args.rotationStep)
    else:
        rotationList = np.array([])





    dT.chipImage(rasterFileName,
                 objectSrc,
                 outputDirectory,
                 finalImageSize=finalImageSize,
                 rotationList=np.arange(0,360,5),
                 rotateNorth=True,
                 windowSize='adjust')
