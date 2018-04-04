import re
import os
import sys
import requests
import json
import database.providers as providers_model

def main():
    results = providers_model.get_null_zip_codes(2)

    for result in results:
        print ('{} ||| {}'.format(result['provider'], result['address']))
        url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(result['address'], os.environ["G_API_KEY"])
        r = requests.get(url)
        geocoded_address = json.loads(r.text)

        geodata = {}
        r = geocoded_address['results'][0]
        geodata['lat'] = r['geometry']['location']['lat']
        geodata['lng'] = r['geometry']['location']['lng']
        geodata['full_address'] = r['formatted_address']
        geodata['street_nbr'] = list(filter(lambda x: 'street_number' in x['types'], r['address_components']))[0]
        geodata['street'] = list(filter(lambda x: 'route' in x['types'], r['address_components']))[0]
        geodata['city'] = list(filter(lambda x: 'locality' in x['types'], r['address_components']))[0]
        geodata['postal_code'] = list(filter(lambda x: 'locality' in x['types'], r['address_components']))[0]
        geodata['county'] = list(filter(lambda x: 'administrative_area_level_2' in x['types'], r['address_components']))[0]
        geodata['state'] = list(filter(lambda x: 'administrative_area_level_1' in x['types'], r['address_components']))[0]
        providers_model.update_address_geodata(geodata, result['id'])

if __name__ == '__main__':
    main()
