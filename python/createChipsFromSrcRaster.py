from spaceNet import geoTools as gT
import argparse
import os

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Clip Source Raster Files to make individual chips from large Mosaic')
    parser.add_argument("rasterSrc", help="raster to chip")
    parser.add_argument("objectSrc", help="geoJSON of object Labels")
    parser.add_argument("clipSize", help="Chip Size in meters", type=int)
    parser.add_argument("outputDirectory", help="Location of chipped files")
    parser.add_argument("--rasterSrcFileList", help="File List of Input Raster Files (1 Raster File Per a line")
    parser.add_argument("--outputPrefix", help="Optional Prefix to append to output")
    parser.add_argument("--outlineSrc", help="geoJSON of AOI outline")
    parser.add_argument("--clipOverLap",
                        help="Decimal of Overlap , 1.0 Equals 100% overlap (infiniteLoop), 0.0 = No Overlap"
                             "Default is 0.0 (No OverLap)", type=float)
    parser.add_argument("--minDecimalToInclude",
                        help="Decimal of Object in image require to include , 1.0 Requires entire object to be in clip "
                             "to be inlcluded, 0.0 = Include all of object in image no matter how small it is in "
                             "size to the entire of the object"
                             "Default is 0.0, Include everything", type=float)
    parser.add_argument("-cpix", "--createPixelGeoJson",
                        help="Create geoJson with polygon Coordinates in pixels",
                        action="store_true")

    parser.add_argument("-m", "--maskFile", help="mask input raster with outline src",
                        action="store_true")
    args = parser.parse_args()

    rastList = []
    if args.rasterSrcFileList:
        with open(args.rasterSrcFileList, 'r') as f:
            for line in f:
                rastList.append(line)
    else:
        rastList.append(args.rasterSrc)


    objectSrc = args.objectSrc
    clipSize = args.clipSize
    output_directory = args.outputDirectory
    if args.outputPrefix:
        output_prefix = args.outputPrefix
    else:
        output_prefix = ''
    if args.outlineSrc:
        outlineSrc = args.outlineSrc
    else:
        outlineSrc = ''

    if args.clipOverLap:
        clipOverlap= args.clipOverLap
    else:
        clipOverlap=0.0

    if args.minDecimalToInclude:
        minpartialPerc= args.minDecimalToInclude
    else:
        minpartialPerc=0.0

    if args.createPixelGeoJson:
        createPix=True
        print("createPix")
    else:
        createPix=False
        print("createPixFalse")



    for rasterFile in rastList:
        rasterFinal = rasterFile
        if args.maskFile:
            rasterFinal = os.path.join(output_directory, os.path.basename(rasterFile).replace(".tif", "_mask.tif"))
            gT.createMaskedMosaic(rasterFile, rasterFinal, outlineSrc)
        gT.cutChipFromMosaic(rasterFinal, objectSrc, outlineSrc,
                             outputDirectory=output_directory,
                             outputPrefix=output_prefix,
                             clipSizeMX=clipSize, clipSizeMY=clipSize,
                             clipOverlap=clipOverlap,
                             minpartialPerc=minpartialPerc,
                             createPix=createPix)


