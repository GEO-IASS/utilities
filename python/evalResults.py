from spaceNet import labelTools as lT
from spaceNet import evalTools as eT
from spaceNet import geoTools as gT
import numpy as np
import sys
import glob
import os
import time




if __name__ == "__main__":

    # load Truth and Test File Locations

    createNewTruthSummary = True
    createNewTestSummary  = True
    evalResults           = True
    threshold             = 0.5
    localDirectoryTruth = '/raid/data/spacenetFromAWS_08122016/processedData/vectorData/geoJson'
    truthSummaryCSVName = "../data/results/truthSummary_AOI_1_08122016.csv"
    localDirectoryTest = '/raid/local/src/CosmiQNet/geojson/'
    testSummaryCSVName = "../data/results/testGeoJsonSummary.csv"
    testResultsDirectory = "../data/results/"
    resultsPrefix = 'results_'
    if not os.path.exists(testResultsDirectory):
        os.makedirs(testResultsDirectory    )


    geojsonList = glob.glob(os.path.join(localDirectoryTruth, '*.geojson'))

    chipnameList = []
    for geojson in geojsonList:
        chipnameList.append(os.path.basename(os.path.splitext(geojson)[0]).rsplit('_',1)[0])

    if createNewTruthSummary:
        lT.createCSVSummaryFileFromJsonList(geojsonList, truthSummaryCSVName, chipnameList=chipnameList,
                                         input='Geo')



    geojsonList = glob.glob(os.path.join(localDirectoryTest, '*.geojson'))

    chipnameList = []
    for geojson in geojsonList:
        chipnameList.append(os.path.basename(os.path.basename(os.path.splitext(geojson)[0])).rsplit('BuildingID')[0].rsplit('chip.')[1])
    if createNewTestSummary:
        lT.createCSVSummaryFileFromJsonList(geojsonList, testSummaryCSVName, chipnameList=chipnameList,
                                            input='Geo')


    if evalResults:

        # check for cores available
        # initialize scene counts
        true_pos_counts = []
        false_pos_counts = []
        false_neg_counts = []

        t0 = time.time()
        # Start Ingest Of Truth and Test Case
        sol_polys = gT.readwktcsv(truthSummaryCSVName )

        prop_polys = gT.readwktcsv(testSummaryCSVName)

        t1 = time.time()
        total = t1 - t0
        print('time of ingest: ', total)

        # Speed up search by preprocessing ImageId and polygonIds

        test_image_ids = set([item['ImageId'] for item in prop_polys if item['ImageId'] > 0])
        prop_polysIdList = np.asarray([item['ImageId'] for item in prop_polys if item["ImageId"] > 0 and \
                                       item['BuildingId']!=-1])
        prop_polysPoly = np.asarray([item['polyGeo'] for item in prop_polys if item["ImageId"] > 0 and \
                                       item['BuildingId']!=-1])

        sol_polysIdsList = np.asarray([item['ImageId'] for item in sol_polys if item["ImageId"] > 0 and \
                                       item['BuildingId']!=-1])
        sol_polysPoly = np.asarray([item['polyGeo'] for item in sol_polys if item["ImageId"] > 0 and \
                                       item['BuildingId']!=-1])
        bad_count = 0
        F1ScoreList = []

        ResultList = []

        eval_function_input_list = eT.create_eval_function_input((test_image_ids,
                                                             (prop_polysIdList, prop_polysPoly),
                                                             (sol_polysIdsList, sol_polysPoly)))
        # evalFunctionInput =  creatEevalFunctionInput((test_image_ids,
        #                                               (prop_polysIdList, prop_polysPoly),
        #                                               (sol_polysIdsList, sol_polysPoly)))
        # Calculate Values
        t3 = time.time()
        print('time For DataCreation {}s'.format(t3-t1))
        #result_list = p.map(eT.evalfunction, eval_function_input_list)
        result_listTotal = []
        for eval_input in eval_function_input_list:
            resultGeoJsonName = os.path.join(testResultsDirectory, resultsPrefix+eval_input[0]+'.geojson')
            result_listTotal.append(eT.evalfunction(eval_input,
                                                    resultGeoJsonName=resultGeoJsonName,
                                                    threshold=threshold))

        result_list, imageIdList = zip(*result_listTotal)
        result_sum = np.sum(result_list, axis=0)
        true_pos_total = result_sum[1]
        false_pos_total = result_sum[2]
        false_neg_total = result_sum[3]
        print('True_Pos_Total', true_pos_total)
        print('False_Pos_Total', false_pos_total)
        print('False_Neg_Total', false_neg_total)
        precision = float(true_pos_total) / (float(true_pos_total) + float(false_pos_total))
        recall = float(true_pos_total) / (float(true_pos_total) + float(false_neg_total))
        F1ScoreTotal = 2.0 * precision*recall / (precision + recall)
        print('F1Total', F1ScoreTotal)

        t2 = time.time()
        total = t2-t0
        print('time of evaluation: {}'.format(t2-t1))
        print('time of evaluation {}s/imageId'.format((t2-t1)/len(result_list)))
        print('Total Time {}s'.format(total))
        print(result_listTotal)
        print(np.mean(result_list))












