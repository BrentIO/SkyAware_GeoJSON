#!/usr/bin/env python

#######################################################
##
## Installation Pre-Reqs:
##      sudo pip install shapely
##
##  Usage: sudo python3 fileProcessor.py {geojsonfile.geojson}
##
## Download GeoJSON files from:
##   https://adds-faa.opendata.arcgis.com/search?collection=Dataset
##
#######################################################

import argparse
import json
import os
from shapely.geometry import mapping, shape, Point, Polygon, LineString
from pathlib import Path

def main():

    try:

        #Define the center of a circle based on the lat/long provided in settings
        pointOfInterest = Point(settings['center']['longitude'], settings['center']['latitude'])

        #Draw a circle around that point
        areaOfInterestPolygon = pointOfInterest.buffer(settings['center']['buffer'])

        with open(settings['geoJsonFile']) as geoJsonFile:
            geoJsonData = json.load(geoJsonFile)

        knownFileType = False

        #Check the file format
        if "name" not in geoJsonData:
            raise Exception("File does not contain a 'name' element.")

        #Ensure the data contains a features array
        if "features" not in geoJsonData:
            raise Exception("File does not contain a 'features' element.")

        #Parse the file based on the name
        if geoJsonData['name'].lower() == "runways":
            knownFileType = True
            process_runways(areaOfInterestPolygon, geoJsonData)

        if geoJsonData['name'].lower() == "class_airspace":
            knownFileType = True            
            process_class_airspace(areaOfInterestPolygon, geoJsonData)

        if geoJsonData['name'].lower() == "designated_points":
            knownFileType = True            
            process_designated_points(areaOfInterestPolygon, geoJsonData)

        if geoJsonData['name'].lower() == "ats_route":
            knownFileType = True            
            process_ats_route(areaOfInterestPolygon, geoJsonData)

        if knownFileType == False:
            raise Exception("File processor cannot be identified.")

        print("G'Day!")

    except Exception as e:
        print(e)
        exit()

def writeFile(name, features, fileName):

    geoJson = {}

    geoJson['type'] = "FeatureCollection"
    geoJson['name'] = name
    geoJson['crs'] = {}
    geoJson['crs']['type'] = "name"
    geoJson['crs']['properties'] = {}
    geoJson['crs']['properties']['name'] = "urn:ogc:def:crs:OGC:1.3:CRS84"
    geoJson['features'] = features

    #Make sure the directory exists
    if os.path.exists(os.path.os.path.dirname(fileName)) == False:
        os.mkdir(os.path.os.path.dirname(fileName))

    #Write the file to disk
    with open(fileName, 'w') as outfile:
        json.dump(geoJson, outfile)

    print("Wrote " + fileName)

def process_runways(poi, geoJson):
    featuresOfInterest = []
    runwayCenterlines = []
    print("GeoJSON file contains " + str(len(geoJson['features'])) + " runways.")

    try:

        for feature in geoJson['features']:

            featureShape = shape(feature['geometry'])

            #Get the center of the feature
            featureCenter = featureShape.centroid

            #Check if the center of the runway is inside the POI area
            if featureCenter.within(poi):

                #Ensure the runway is greater than the minimum length
                if feature['properties']['LENGTH'] < settings['runways']['minimumLength']:
                    continue

                #Ignore helipads if configured in settings
                if settings['runways']['helipads'] == False:

                    if feature['properties']['DESIGNATOR'] == "H1":
                        continue

                #Clean up the properties
                feature['properties'] = cleanProperties(feature, "runways")

                #Runway meets requirements; Add it to the features of interest
                featuresOfInterest.append(feature)

        print("Found " + str(len(featuresOfInterest)) + " runways of interest.")

        #Write the features of interest to disk
        writeFile("Runways", featuresOfInterest, os.path.join(settings['outputPath'], os.path.basename(settings['geoJsonFile'])))

    except Exception as e:
        print(e)
        exit()

def process_class_airspace(poi, geoJson):
    featuresOfInterest = []
    airspaceList = []
    
    print("GeoJSON file contains " + str(len(geoJson['features'])) + " airspace features.")

    try:

        for feature in geoJson['features']:

            polygon = shape(feature['geometry'])

            #Get the center of the feature
            featureCenter = polygon.centroid

            #Check if the center of the airspace is inside the POI area
            if featureCenter.within(poi):

                #Ensure we care about this airspace type
                if feature['properties']['LOCAL_TYPE'] not in settings['class_airspace']['classes']:
                    continue

                #Add the airpsace type to the list if it doesn't already exist
                if feature['properties']['LOCAL_TYPE'] not in airspaceList:
                    airspaceList.append(feature['properties']['LOCAL_TYPE'])

                #Clean up the properties
                feature['properties'] = cleanProperties(feature, "class_airspace")

                #Airspace meets requirements; Add it to the features of interest
                featuresOfInterest.append(feature)

        print("Found " + str(len(featuresOfInterest)) + " airspace classes of interest.")

        #Cycle through each airspace type and write them all to the same file
        for airspace in airspaceList:
            tmpFeaturesOfInterest = []

            #Cycle through each feature of interest and see if it has the same type of airspace as being inspected
            for feature in featuresOfInterest:

                if feature['properties']['LOCAL_TYPE'] == airspace:

                    #Add this to the temporary list
                    tmpFeaturesOfInterest.append(feature)

            print("Found " + str(len(tmpFeaturesOfInterest)) + " in " + airspace)

            #Write all of these airspace entries to  disk
            writeFile("Class_Airspace_" + airspace, tmpFeaturesOfInterest, os.path.join(settings['outputPath'], "Airspace_" + airspace + Path(settings['geoJsonFile']).suffix))

    except Exception as e:
        print(e)
        exit()

def process_designated_points(poi, geoJson):
    featuresOfInterest = []
    print("GeoJSON file contains " + str(len(geoJson['features'])) + " designated points.")

    try:

        for feature in geoJson['features']:

            #Ensure the data exists for every point being evaluated
            if 'geometry' in feature:

                if feature['geometry'] != None:

                    if "coordinates" in feature['geometry']:

                        if feature['geometry']['coordinates'] != None:

                            p = Point(feature['geometry']['coordinates'])

                            #Check if the point is inside the POI area
                            if p.within(poi):

                                #Clean up the properties
                                feature['properties'] = cleanProperties(feature, "designated_points")

                                #Add it to the features of interest
                                featuresOfInterest.append(feature)

        print("Found " + str(len(featuresOfInterest)) + " designated points of interest.")

        #Write the features of interest to disk
        writeFile("Designated_Points", featuresOfInterest, os.path.join(settings['outputPath'], os.path.basename(settings['geoJsonFile'])))

    except Exception as e:
        print(e)
        exit()

def process_ats_route(poi, geoJson):
    featuresOfInterest = []
    print("GeoJSON file contains " + str(len(geoJson['features'])) + " ATS Routes.")

    try:

        for feature in geoJson['features']:

            polygon = shape(feature['geometry'])

            #Get the center of the feature
            featureCenter = polygon.centroid

            #Check if the center of the runway is inside the POI area
            if featureCenter.within(poi):

                #Clean up the properties
                feature['properties'] = cleanProperties(feature, "ats_route")

                #Runway meets requirements; Add it to the features of interest
                featuresOfInterest.append(feature)
        
        print("Found " + str(len(featuresOfInterest)) + " ATS Routes of interest.")

        #Write the features of interest to disk
        writeFile("ATS_Routes", featuresOfInterest, os.path.join(settings['outputPath'], os.path.basename(settings['geoJsonFile'])))

    except Exception as e:
        print(e)
        exit()

def setup(geoJsonFile, outputPath):

    global settings

    try:
        
        #Get the settings
        if os.path.exists(os.getcwd() + "/settings.json"):
            with open(os.getcwd() + "/settings.json") as settingsFile:
                settings = json.load(settingsFile)
        else:
            raise Exception("Settings file does not exist")

        #Ensure the geoJson file exists
        if os.path.exists(geoJsonFile):
            settings['geoJsonFile'] = geoJsonFile
        else:
            raise Exception("GeoJSON file does not exist")

        if outputPath != None:
            settings['outputPath'] = outputPath       

        # Run the main program
        main()

    except Exception as e:
        print(e)
        exit()

def cleanProperties(feature, fileType):

    cleanProperties = {}

    for propertyEntry in feature['properties']:

        if propertyEntry in settings[fileType]['properties']:

            if propertyEntry in ["IDENT", "NAME", "DESIGNATOR"]:
                cleanProperties['name'] = feature['properties'][propertyEntry]
            else:
                cleanProperties[propertyEntry] = feature['properties'][propertyEntry]

    return cleanProperties

if __name__ == "__main__":

    global settings
    settings = {}

    parser = argparse.ArgumentParser(description='Exports features from a GeoJSON file within a rough radius around a point of interest.')
    parser.add_argument('GeoJSON_File', type=str, help="The GeoJSON file containing all of the shapes to consider.")
    parser.add_argument("--outputPath", help="Changes default output location from /usr/share/skyaware/html/geojson to the specified file directory")

    args = parser.parse_args()

    setup(args.GeoJSON_File, args.outputPath)