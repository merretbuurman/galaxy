#!/usr/bin/env python3

import requests
import argparse
import sys
import geojson
import logging

LOGGER = logging.getLogger(__name__)


'''
10 Oktober 2023

Calling this script:
python /home/mbuurman/galaxy/galaxy/tools/ogc_services/wrap_snap_to_network.py --method "distance" --distance 500 --accumulation 0.5 --coordinate_geojson "{\"inputs\":{\"method\": \"distance\", \"accumulation\": 0.5, \"distance\": 500, \"coordinate_multipoint\":{\"coordinates\": [[-17.25355, -44.885825], [-13.763611, -43.595833]], \"type\": \"MultiPoint\"}}}" 

How Galaxy calls this script:
python /home/mbuurman/galaxy/galaxy/tools/ogc_services/wrap_snap_to_network.py --coordinate_geojson "$coordinate_geojson" --coordinate_csv "$coordinate_csv" --distance $distance --method $method --accumulation $accumulation --output $galaxy_output

This script is a wrapper to be called by Galaxy.
It then makes a HTTP request to a OGC service.

NOTE:
THe OGC service wants the GeoJSON in the parameter named coordinate_multipoint, while this wrapper takes coordinate_geojson or coordinate_csv, to distinguish between both types!

These are the valid inputs for the OGC service:
body = {
    "inputs":{
        "method": "distance",
        "distance": 500,
        "accumulation": 0.5,
        "coordinate_multipoint": {
           "type": "MultiPoint",
           "coordinates": [
                [-17.25355, -44.885825],
                [-13.763611, -43.595833]
            ]
        }
    }
}

These are the inputs without newlines and with escaped double-quotes (ready for curl):
{\"inputs\":{\"method\":\"distance\",\"distance\":500,\"accumulation\":0.5,\"coordinate_multipoint\":{\"type\":\"MultiPoint\",\"coordinates\":[[-17.25355, -44.885825], [-13.763611, -43.595833]]}}}

How to pass the inputs?
curl -X POST "http://localhost:5000/processes/snap-to-network/execution" -H "Content-Type: application/json" -d "{\"inputs\":{\"method\":\"distance\",\"distance\":500,\"accumulation\":0.5,\"coordinate_multipoint\":{\"type\":\"MultiPoint\",\"coordinates\":[[-17.25355, -44.885825], [-13.763611, -43.595833]]}}}"
'''



def csv_to_geojson(input_string, sep=','):
    result_multipoint = {"type": "MultiPoint", "coordinates":[]}

    # Split at newline:
    # If there is a newline in the GUI, it will end up here as "__cn__":
    LOGGER.debug('CSV input before splitting: %s' % input_string)
    input_string = input_string.split('__cn__')
    LOGGER.debug('CSV input after splitting: %s' % input_string)

    # Get coords from each line:
    for line in input_string:
        LOGGER.debug('Found coordinate line: %s' % line)
        splitted = line.strip().split(sep)
        coord1, coord2 = float(splitted[0].strip()), float(splitted[1].strip())
        LOGGER.debug('Extracted these coordinates %s, %s' % (coord1, coord2))
        result_multipoint['coordinates'].append([coord2, coord1])
    
    LOGGER.info('Finished creating GeoJSON multipoint from CSV coordinates: %s' % geojson.dumps(result_multipoint))
    return result_multipoint



if __name__ == '__main__':

    print('Python script: %s' % sys.argv[0])

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    ### Replace those weird escaped characters from the string that was passed by Galaxy GUI:
    LOGGER.debug('Python script inputs sys.argv: %s' % sys.argv)
    LOGGER.debug('Run the replacement dirty fix:')
    i = 0
    for i in range(0,len(sys.argv)):
        LOGGER.debug('Python command line arg: "%s"' % sys.argv[i])
        sys.argv[i] = sys.argv[i].replace('__oc__', '{').replace('__cc__', '}')
        sys.argv[i] = sys.argv[i].replace('__ob__', '[').replace('__cb__', ']')
        sys.argv[i] = sys.argv[i].replace('__dq__', '"')
        LOGGER.debug('Same item after replace: "%s"' % sys.argv[i])
        # https://git.bwcloud.uni-freiburg.de/galaxyproject/galaxy/-/blob/5701fe7e108126fda05c33dfe083bd2c7f370db9/tools/filters/grep.py#L71


    ### Input params
    LOGGER.debug('Getting the input parameters...')
    parser = argparse.ArgumentParser(
                        prog='Calling snap-to-network service from OGC API at localhost:5000 via python',
                        description='This program wants to substitute snap_to_network.R, see https://glowabio.github.io/hydrographr/reference/snap_to_network.html')
    parser.add_argument('--ogc_service_url', default="http://localhost:500", help='Which service to call, incl. http/https and port, e.g. http://localhost:5000')
    parser.add_argument('--method', default="distance", help='"distance", "accumulation", or "both". Defines if the points are snapped using the distance or flow accumulation.')
    parser.add_argument('--distance', default=500, help='Maximum radius in map pixels. The points will be snapped to the next stream within this radius.')
    parser.add_argument('--accumulation', default=0.5, help='Minimum flow accumulation. Points will be snapped to the next stream with a flow accumulation equal or higher than the given value.')
    parser.add_argument('--output', default="DUMMY", help='Galaxy needs this, but you can just put some dummy string there.')
    parser.add_argument('--coordinate_geojson', default="null", help='GeoJSON Coordinates in which CRS?')
    parser.add_argument('--coordinate_csv', default="null", help='Columns with coordinates in which CRS?')
    args = parser.parse_args()
    LOGGER.debug('Getting the input parameters... done.')


    ### Select whether we have CSV or GeoJSON coordinates, parse accordingly:
    if len(args.coordinate_geojson) == 0:
        if len(args.coordinate_csv) == 0:
            err_msg = 'Cannot have both coordinate fields empty! Please pass either a CSV list or a GeoJSON multipoint.'
            LOGGER.error(err_msg)
            raise ValueError(err_msg)
        else:
            LOGGER.info('Using CSV coordinates: "%s"' % args.coordinate_csv)
            multipoint_to_pass_on = csv_to_geojson(args.coordinate_csv)
            LOGGER.debug('Converted the CSV coordinates to multipoint in geojson')
    else:
        if len(args.coordinate_csv) == 0:
            LOGGER.info('Using GeoJSON coordinates! %s' % type(args.coordinate_geojson))
            multipoint_to_pass_on = geojson.loads(args.coordinate_geojson)
            LOGGER.debug('Parsed the string geojson to proper geojson object')
        else:
            LOGGER.warning('If both coordinate input fields are filled, we use the CSV ones!')
            LOGGER.info('Using CSV coordinates: "%s"' % args.coordinate_csv)
            multipoint_to_pass_on = csv_to_geojson(args.coordinate_csv)
            LOGGER.debug('Converted the CSV coordinates to multipoint in geojson')


    ### Assemble the HTTP request
    LOGGER.debug('Assembling the request...')
    url = args.ogc_service_url.rstrip('/')+'/processes/snap-to-network/execution'
    LOGGER.info('This URL will be queried: %s' % url)
    h = {'accept': 'application/json', 'Content-Type': 'application/json'}
    body = {
        "inputs":{
            "method" : args.method,
            "distance" : args.distance,
            "accumulation" : args.accumulation,
            "coordinate_multipoint" : multipoint_to_pass_on
        }
    }
    LOGGER.info('This is the request body: %s' % body)
    LOGGER.debug('Data type of body: %s' % type(body))


    ### Make POST request
    LOGGER.debug('Making POST request to server:')
    print('Making POST request to server:')
    resp = requests.post(url, headers=h, json=body)
    resp_json = resp.json()
    LOGGER.info('Finished making POST request to server! Received HTTP status code: %s' % resp.status_code)
    LOGGER.info('And this is the server\'s response: \n%s' % resp_json)
    # Example: {'id': 'snapped_points', 'value': {'type': 'MultiPoint', 'coordinates': [['-43.595833', '-13.763611'], ['-44.885825', '-17.25355']]}}


    ### Hand through server errors:
    if not resp.status_code == 200:
        err_msg = 'Tool failure! Server responded with HTTP status code %s (expected 200)' % resp.status_code
        LOGGER.error(err_msg)
        raise ValueError(err_msg)
    elif (('code' in resp_json and resp_json['code'] == 'InvalidParameterValue') 
       or ('description' in resp_json and resp_json['description'] == 'Error updating job')):
        err_msg = 'Tool failure! Server responded with: %s' % resp_json
        LOGGER.error(err_msg)
        raise ValueError(err_msg)


    ### Write to file
    OUTPUTFILE = args.output
    with open(OUTPUTFILE, 'w') as out:
        geojson.dump(resp_json, out)
        LOGGER.info('Written to file: %s' % OUTPUTFILE)