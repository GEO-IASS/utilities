# SpaceNet Utilities

This repository has two python packages, geoTools and evalTools. The geoTools packages is intended to assist in the preprocessing of [SpaceNet](https://aws.amazon.com/public-data-sets/spacenet/) satellite imagery data corpus to a format that is consumable by machine learning algorithms. The evalTools package is used to evaluate the effectiveness of object detection algorithms using ground truth.

## Dependencies
All dependencies can be found in requirements.txt.  Main dependencies are GDAL Python Bindings, OpenCV and numpy

## Example code
Basic Usage from the base directory.

python python/processBoatLabels.py rasterFile.tiff objectfile.geojson /tmp/storage/  

## License
See [LICENSE](./LICENSE).
