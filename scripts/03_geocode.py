import os
import sys
import requests
import json
import database.addresses as addresses_model

def getComponent(type, address_components):
    component = list(filter(lambda x: type in x['types'], address_components))
    return component[0]['long_name'] if component else None

def main():
    results = addresses_model.get_null_zip_codes(100)

    for result in results:
        print ('{} ||| {}'.format(result['provider'], result['address']))
        url = '\thttps://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(result['address'], os.environ["G_API_KEY"])
        print (url)
        r = requests.get(url)
        geocoded_address = json.loads(r.text)
        geodata = {}
        r = geocoded_address['results'][0]
        geodata['lat'] = r['geometry']['location']['lat']
        geodata['lng'] = r['geometry']['location']['lng']
        geodata['full_address'] = r['formatted_address']

        geodata['street_nbr'] = getComponent('street_number', r['address_components'])
        geodata['street'] = getComponent('route', r['address_components'])
        geodata['city'] = getComponent('locality', r['address_components'])
        geodata['postal_code'] = getComponent('postal_code', r['address_components'])
        geodata['county'] = getComponent('administrative_area_level_2', r['address_components'])
        geodata['state'] = getComponent('administrative_area_level_1', r['address_components'])

        if not geodata['postal_code']:
            print ('no zip comming back...')
            sys.exit(0)
        
        addresses_model.update_address_geodata(geodata, result['id'])

if __name__ == '__main__':
    main()
