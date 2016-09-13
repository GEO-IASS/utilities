# SpaceNet Utilities

This repository has two python packages, geoTools and evalTools. The geoTools packages is intended to assist in the preprocessing of [SpaceNet](https://aws.amazon.com/public-data-sets/spacenet/) satellite imagery data corpus to a format that is consumable by machine learning algorithms. The evalTools package is used to evaluate the effectiveness of object detection algorithms using ground truth.

## Dependencies
All dependencies can be found in requirements.txt.  Some dependencies must be installed by apt-get.  Main dependencies are GDAL Python Bindings, OpenCV and numpy
Installation instruction:
```python
sudo apt-get install python-gdal # Install Python Gdal Bindings
sudo apt-get install python-opencv # Install OpenCV
pip install -r requirements.txt # Install additional requirements
```

## Example code
Basic Usage from the base directory.
```python
python python/processBoatLabels.py data/rasterFile.tiff data/objectfile.geojson data/results 
```


## License
See [LICENSE](./LICENSE).
