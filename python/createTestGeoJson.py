from spaceNet import evalTools as eT
from spaceNet import geoTools as gT
import numpy as np
import sys
import multiprocessing
import time


if __name__ == "__main__":

    # load Truth and Test File Locations
    if len(sys.argv) > 1:
        truth_fp = sys.argv[1]
    else:
        truth_fp = '../testData/public_polygons_solution_3Band.geojson'

    sol_polys = gT.importgeojson(truth_fp, removeNoBuildings=True)

    sol_polysIdsList = np.asarray([item['ImageId'] for item in sol_polys if item["ImageId"] > 0 and \
                                   item['BuildingId'] != -1])
    sol_polysPoly = np.asarray([item['poly'] for item in sol_polys if item["ImageId"] > 0 and \
                                item['BuildingId'] != -1])

    sol_polysNew = [item['poly'] for item in sol_polys if item["ImageId"] > 0 and \
                                item['BuildingId'] != -1]

    sol_polyNew =[]
    for sol_poly in sol_polys:
        sol_polyNew.append({'ImageId': sol_poly['ImageId'], 'BuildingId': sol_poly['BuildingId'],
         'poly': gT.get_envelope(sol_poly['poly'])})

    gT.exporttogeojson(truth_fp.replace(".geojson", "_envelope.geojson"), sol_polyNew)



