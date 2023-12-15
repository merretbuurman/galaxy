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
curl -X POST "http://130.225.37.27:5000/processes/assessment-units/execution" -H "Content-Type: application/json" -d "{\"inputs\":{\"assessmentPeriod\": \"2011-2016\", \"combined_Chlorophylla_IsWeighted\": true}}
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
                        prog='Call the process "HELCOM HEAT2" from an OGC API.',
                        description='This program returns Assessment Indicator...')
    parser.add_argument('--assessment_period', default="2011-2016", help='The HELCOM Assessment Period, one of: "1877-9999", "2011-2016" or "2016-2021"')
    parser.add_argument('--input_csv', help='The HELCOM Annual Indicator as CSV')
    parser.add_argument('--ogc_service_url', default="http://130.225.37.27:5000", help='Which service to call, incl. http/https and port, e.g. http://localhost:5000')
    parser.add_argument('--output', default="DUMMY", help='Galaxy needs this, but you can just put some dummy string there.')
    args = parser.parse_args()
    LOGGER.debug('Getting the input parameters... done.')

    LOGGER.info('______________________args.assessment_period: %s' % args.assessment_period)
    LOGGER.info('______________________args.input_csv: %s' % args.input_csv) # This is a path: /home/.../galaxy/database/objects/1/a/6/dataset_1a654d97-4a0b-49fc-bbbf-3612c595da94.dat

    with open(args.input_csv, 'r') as myinputfile:
        input_csv = myinputfile.read()

    #LOGGER.info('______________________input_csv: %s' % input_csv)


    ### Assemble the HTTP request
    LOGGER.debug('Assembling the request...')
    url = args.ogc_service_url.rstrip('/')+'/processes/assessment-b/execution'
    LOGGER.info('This URL will be queried: %s' % url)
    h = {'accept': 'application/json', 'Content-Type': 'application/json'}
    body = {
        "inputs":{
            "assessmentPeriod" : args.assessment_period,
            "assessment_indicators_csv": input_csv
        }
    }
    #LOGGER.debug('This is the request body: %s' % body)
    #LOGGER.debug('Data type of body: %s' % type(body))

    
    ### Make POST request
    LOGGER.debug('Making POST request to server:')
    print('Making POST request to server:')
    resp = requests.post(url, headers=h, json=body)
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
        #out.write(resp.text)
        out.write(input_csv)
        LOGGER.info('Output written to file: %s' % OUTPUTFILE)
