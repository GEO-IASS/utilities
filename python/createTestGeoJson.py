from spaceNet import evalTools as eT
from spaceNet import geoTools as gT
import os
import csv

if __name__ == "__main__":

    # load Truth and Test File Locations

    truth_fp = '../data/AOI_0_TEST/processedData/AOI_0_TEST_Summary.csv'
    envelopeLocation = '../data/AOI_0_TEST/answers/AOI_0_TEST_ResultsEnvSummary.csv'

    sol_polyList = gT.readwktcsv(truth_fp)


    sol_polyNewList = []
    for sol_poly in sol_polyList:
        if sol_poly['BuildingId'] == -1:
            sol_polyNewList.append(sol_poly)
        else:
            sol_polyNewList.append({'ImageId': sol_poly['ImageId'], 'BuildingId': sol_poly['BuildingId'],
                    'polyPix': gT.get_envelope(sol_poly['polyPix']),
                    'polyGeo': gT.get_envelope(sol_poly['polyGeo']),
                          })

    with open(envelopeLocation, 'wb') as csvfile:
        writerTotal = csv.writer(csvfile, delimiter=',', lineterminator='\n')

        writerTotal.writerow(['ImageId', 'BuildingId', 'PolygonWKT_Pix', 'PolygonWKT_Geo'])

        for sol_poly in sol_polyNewList:
            writerTotal.writerow([os.path.basename(sol_poly['ImageId']), sol_poly['BuildingId'],
                              sol_poly['polyPix'], sol_poly['polyGeo']])





