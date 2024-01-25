#!/usr/bin/env python3

import requests
import argparse
import sys
import json
import logging

LOGGER = logging.getLogger(__name__)


'''
Merret, 11 December 2023

Calling this script:
python /home/mbuurman/galaxy/galaxy/tools/ogc_services/wrap_get_species_data.py --species_name "Conorhynchos conirostris" --basin_id "481051" --output "output.json"

This script is a wrapper to be called by Galaxy.
It then makes a HTTP request to a OGC service.

These are the valid inputs for the OGC service:
body = {
    "inputs":{
        "assessmentPeriod" : "2011-2016",
        "combined_Chlorophylla_IsWeighted": True
    }
}

How to call the pygeoapi service that this script calls?
curl -X POST "http://130.225.37.27:5000/processes/gridunits/execution" -H "Content-Type: application/json" -d "{\"inputs\":{\"assessmentPeriod\": \"2011-2016\", \"combined_Chlorophylla_IsWeighted\": true}}
'''


if __name__ == '__main__':

    print('Python script: %s' % sys.argv[0])

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    ### Replace those weird escaped characters from the string that was passed by Galaxy GUI:
    LOGGER.debug('Python script inputs sys.argv: %s' % sys.argv)

    ### Input params
    ### These are provided by Galaxy (call defined in the tool's xml file.)
    LOGGER.debug('Getting the input parameters...')
    parser = argparse.ArgumentParser(
                        prog='Call the process "HELCOM HEAT1" from an OGC API.',
                        description='This program returns species occurences from GBIF, filtered by the basin XYZ.')
    parser.add_argument('--assessment_period', default="2011-2016", help='The HELCOM Assessment Period, one of: "1877-9999", "2011-2016" or "2016-2021"')
    parser.add_argument('--combined_chlorophylla_is_weighted', default="true", help='Not too sure, ask HELCOM.')
    parser.add_argument('--ogc_service_url', default="http://130.225.37.27:5000", help='Which service to call, incl. http/https and port, e.g. http://localhost:5000')
    parser.add_argument('--username', help='The username used to login')
    parser.add_argument('--password', help='The password used to login')
    parser.add_argument('--output', default="DUMMY", help='Galaxy needs this, but you can just put some dummy string there.')
    args = parser.parse_args()
    LOGGER.debug('Getting the input parameters... done.')

    # TODO FEATURE: Do we have to check the species name against some taxonomy database?

    ### Assemble the HTTP request
    LOGGER.debug('Assembling the request...')
    url = args.ogc_service_url.rstrip('/')+'/processes/annual-indicator/execution'
    LOGGER.info('This URL will be queried: %s' % url)
    h = {'accept': 'application/json', 'Content-Type': 'application/json'}
    body = {
        "inputs":{
            "assessmentPeriod" : args.assessment_period,
            "combined_Chlorophylla_IsWeighted": args.combined_chlorophylla_is_weighted
        }
    }
    LOGGER.info('This is the request body: %s' % body)
    LOGGER.debug('Data type of body: %s' % type(body))


    ### Make POST request
    LOGGER.debug('Making POST request to server:')
    print('Making POST request to server:')
    verify = False # TODO: In production, don't!!
    resp = requests.post(url, headers=h, json=body, verify=verify, auth=(args.username, args.password))
    #resp_json = resp.json()
    LOGGER.info('Finished making POST request to server! Received HTTP status code: %s' % resp.status_code)
    LOGGER.info('And this is the server\'s response: \n%s...' % resp.text[0:100])


    ### Hand through server errors:
    if not resp.status_code == 200:
        err_msg = 'Tool failure! Server responded with HTTP status code %s (expected 200)' % resp.status_code
        LOGGER.error(err_msg)
        raise ValueError(err_msg)
    #elif (('code' in resp_json and resp_json['code'] == 'InvalidParameterValue') 
    else:
        try:
            resp_json = resp.json()
            if (('code' in resp_json and resp_json['code'] == 'InvalidParameterValue') 
                or ('description' in resp_json and resp_json['description'] == 'Error updating job')):
                err_msg = 'Tool failure! Server responded with: %s' % resp_json
                LOGGER.error(err_msg)
                raise ValueError(err_msg)
        except json.decoder.JSONDecodeError as e:
            LOGGER.info('The server\'s response is not a JSON response.')


    ### Write to file
    OUTPUTFILE = args.output
    with open(OUTPUTFILE, 'w') as out:
        #geojson.dump(output_tobereturned, out)
        out.write(resp.text)
        LOGGER.info('Output written to file: %s' % OUTPUTFILE)
