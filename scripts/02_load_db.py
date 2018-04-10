import re
import os
import sys
import pprint as pp
from pathlib import Path
from random import randint
from people_names import people_names

import database.types as types_model
import database.subtypes as subtypes_model
import database.providers as providers_model
import database.addresses as addresses_model
import database.doctors as doctors_model
import database.type_providers as type_providers_model
import database.doctor_providers as doctor_providers_model
import database.provider_addresses as provider_addresses_model

def get_provider_files(provider_files):
    p = Path(provider_files)
    files = list(p.glob('**/*.txt'))
    return files

def read_and_parse_file(path, provider_type, provider_subtype, stopwords):
    file_contents = read_file(path)
    return parse_file(file_contents, provider_type, provider_subtype, stopwords)


def read_file(path):
    with open(path) as f:
        file_contents = f.read()
    split_provider_info = re.split(r'[\n]{2}|\t+', file_contents)
    return list(map(lambda x : x.split('\n'), split_provider_info))

def read_stopfile():
    with open('./scripts/stopwords.txt', 'r') as f:
        return  f.read().splitlines()

def parse_file(file_contents, provider_type, provider_subtype, stopwords):
    has_doc_name = includes_doctor_name(file_contents, stopwords)
    providers = []
    print ('has_doc_name: {}'.format(has_doc_name))

    nbr_providers = len(file_contents) - 5
    print ('len(file_contents): {}'.format(len(file_contents)))
    if len(file_contents) > 30:
        start = randint(0, nbr_providers)
        end = start + 6
    else:
        start = 0
        end = start + 6

    print ('start: {} || end: {}'.format(start, end))

    for s in file_contents[start:end]:
    # for s in file_contents:
        fields = list(filter(lambda x: x != '', s))
        if len(fields) == 0:
            continue

        data = {}
        data['type'] = provider_type
        data['subtype'] = provider_subtype
        provider = parse_provider_data(fields, data, has_doc_name, stopwords)
        providers.append(provider)

    return providers

def includes_doctor_name(file_contents, stopwords):
    nbr_providers_subset = min(len(file_contents), 20)
    sublist = file_contents[:nbr_providers_subset]
    count_doc_name = 0
    for s in sublist:
        fields = list(filter(lambda x: x != '', s))
        if (len(fields) == 0):
            break
        provider_match = is_provider_name(stopwords, fields[0])
        if not provider_match:
            count_doc_name+=1
    return count_doc_name > (nbr_providers_subset/2 - 2)

def is_provider_name(stopwords, string):
    return  re.findall(r"(?=("+'|'.join(stopwords)+r"))", string)

def parse_provider_data(provider_info, data, has_doc_name, stopwords):
    # print (provider_info)
    if is_provider_name(stopwords, provider_info[0]) or check_regex(provider_info[0], data) == 'provider':
        # print ('123 aa')
        data['provider_name'] = provider_info[0].strip()
        start_index = 1
    elif is_provider_name(stopwords, provider_info[1]):
        # print ('123 bb')
        doc_name = parse_doctor_name(provider_info[0].strip())
        data['doc_name'] = people_names.split_name(doc_name, 'fml')
        data['provider_name'] = provider_info[1].strip()
        start_index = 2
    elif check_regex(provider_info[1], data) == 'address':
        # print ('123 cc')
        if has_doc_name:
            doc_name = parse_doctor_name(provider_info[0].strip())
            data['doc_name'] = people_names.split_name(doc_name, 'fml')
        else:
            data['provider_name'] = provider_info[1].strip()
        start_index = 1
    else:
        # print ('123 dd')
        doc_name = parse_doctor_name(provider_info[0].strip())
        data['doc_name'] = people_names.split_name(doc_name, 'fml')

        data['provider_name'] = provider_info[1].strip()
        start_index = 2

    for pi in provider_info[start_index:]:
        type = check_regex(pi, data)
        if type in data:
            data[type] += ', ' + pi
        else:
            data[type] = pi

    return (data)

def parse_doctor_name(line):
    names = line.strip().split(' ')
    return ' '.join(names[1:] + [names[0]])

def check_regex(line, data):
    if re.compile('^(\w+)$').match(line):
        return 'provider'
    if re.compile('(?i)PO BOX|(?i)p.o. box').match(line):
        return 'po_box'
    # elif re.compile(r'^(\d{2,}|\d+TH|\d+RD)(.+ ){2,}').match(line):
    elif re.compile(r'^(\d+|\d+TH|\d+RD)(.+ ){2,}').match(line):
        return 'address'
    elif re.compile('^STE').match(line):
        return 'address'
    elif re.compile(r'\s\d{5}$').search(line):
        return 'address'
    elif re.compile(r'HWY|HIGHWAY').search(line):
        return 'address'
    elif re.compile(r'\b(ST|AVE|BLVD|LN|DR|AV)\b$').search(line):
        return 'address'
    elif re.compile(r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}').search(line):
        return 'phone'
    elif re.compile('(?i)Critical access provider').match(line):
        return 'critical_access_provider'
    elif re.compile('(?i)Specialty').match(line):
        return 'specialty'
    else:
        return 'notes'
    return data


def insert_into_db(providers):
    counter = 0
    for provider in providers:
        counter += 1
        if counter % 100 == 0:
            print ('loading db: {}'.format(counter))
        print (provider)

        # this should be in a transaction... meh
        type_id = types_model.upsert_type(provider)
        subtype_id = subtypes_model.upsert_subtype(provider, type_id[0])
        if 'doc_name' in provider and 'provider_name' not in provider:
            provider['provider_name'] = '{} {} {}'.format(provider['doc_name']['first_name'], provider['doc_name']['middle_name'], provider['doc_name']['last_name'])
            provider['provider_name'] = ' '.join(provider['provider_name'].split())
            # print (provider['provider_name'])

        if 'provider_name' in provider:
            provider_id = providers_model.upsert_provider(provider)
            providers_model.update_provider(provider, provider_id[0])
            type_providers_model.upsert_type_provider('provider', type_id[0], provider_id[0])
            address_id = addresses_model.upsert_address(provider)
            provider_addresses_model.upsert_provider_addresses(provider_id[0], address_id[0])


        if 'doc_name' in provider:
            doctor_id = doctors_model.upsert_doctor(provider['doc_name'])
            type_providers_model.upsert_type_provider('doctor', type_id[0], doctor_id[0])

        if 'doc_name' in provider and 'provider_name' in provider:
            doctor_providers_model.upsert_doctor_providers(doctor_id[0], provider_id[0])

def main():
    # file = open("testfile.txt","w")
    #
    # file.write("Hello World")
    # file.write("This is our new text file")
    # file.write("and this is another line.")
    # file.write("Why? Because we can.")
    #
    # file.close()
    #
    #
    files = get_provider_files('./provider_files')
    stopwords = read_stopfile()

    files = filter(lambda x: x.parts[2] == 'testing.txt', files)
    for file in files:
        dir, subdir, filename = file.parts
        print('\n**************subdir: {} | filename: {}'.format(subdir, filename))
        subtype, _ = filename.split(".")
        providers = read_and_parse_file(file, subdir, subtype, stopwords)
        for p in providers:
            print (p)

        insert_into_db(providers)


if __name__ == '__main__':
    main()
