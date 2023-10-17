#!/usr/bin/env python3

import requests
import argparse
import sys
import geojson
import logging

LOGGER = logging.getLogger(__name__)


'''
Merret, 16 Oktober 2023

Calling this script:
python /home/mbuurman/galaxy/galaxy/tools/ogc_services/wrap_get_species_data.py --species_name "Conorhynchos conirostris" --basin_id "481051" --output "output.json"

This script is a wrapper to be called by Galaxy.
It then makes a HTTP request to a OGC service.

These are the valid inputs for the OGC service:
{
    "inputs":{
        "species_name":"Conorhynchos conirostris",
        "basin_id":"481051"
    }
}

How to call the pygeoapi service that this script calls?
curl -X POST "http://localhost:5000/processes/get-species-data/execution" -H "Content-Type: application/json" -d "{\"inputs\":{\"species_name\":\"Conorhynchos conirostris\",\"basin_id\":\"481051\"}}"
'''


if __name__ == '__main__':

    print('Python script: %s' % sys.argv[0])

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    ### Replace those weird escaped characters from the string that was passed by Galaxy GUI:
    LOGGER.debug('Python script inputs sys.argv: %s' % sys.argv)
    '''
    LOGGER.debug('Run the replacement dirty fix:')
    i = 0
    for i in range(0,len(sys.argv)):
        LOGGER.debug('Python command line arg: "%s"' % sys.argv[i])
        sys.argv[i] = sys.argv[i].replace('__oc__', '{').replace('__cc__', '}')
        sys.argv[i] = sys.argv[i].replace('__ob__', '[').replace('__cb__', ']')
        sys.argv[i] = sys.argv[i].replace('__dq__', '"')
        sys.argv[i] = sys.argv[i].replace('__cn__', '')
        LOGGER.debug('Same item after replace: "%s"' % sys.argv[i])
        # https://git.bwcloud.uni-freiburg.de/galaxyproject/galaxy/-/blob/5701fe7e108126fda05c33dfe083bd2c7f370db9/tools/filters/grep.py#L71
    '''

    ### Input params
    ### These are provided by Galaxy (call defined in the tool's xml file.)
    LOGGER.debug('Getting the input parameters...')
    parser = argparse.ArgumentParser(
                        prog='Call the process "get-species-data" from an OGC API.',
                        description='This program returns species occurences from GBIF, filtered by the basin XYZ.')
    parser.add_argument('--species_name', default="Conorhynchos conirostris", help='The scienfic name whose species occurence to retrieve from GBIF.')
    parser.add_argument('--basin_id', default="481051", help='The number of the basin in which to look for species occurences.')
    parser.add_argument('--ogc_service_url', default="http://localhost:5000", help='Which service to call, incl. http/https and port, e.g. http://localhost:5000')
    parser.add_argument('--output', default="DUMMY", help='Galaxy needs this, but you can just put some dummy string there.')
    args = parser.parse_args()
    LOGGER.debug('Getting the input parameters... done.')

    # TODO FEATURE: Do we have to check the species name against some taxonomy database?

    ### Assemble the HTTP request
    LOGGER.debug('Assembling the request...')
    url = args.ogc_service_url.rstrip('/')+'/processes/get-species-data/execution'
    LOGGER.info('This URL will be queried: %s' % url)
    h = {'accept': 'application/json', 'Content-Type': 'application/json'}
    body = {
        "inputs":{
            "species_name" : args.species_name,
            "basin_id": args.basin_id
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
        LOGGER.info('Output written to file: %s' % OUTPUTFILE)
