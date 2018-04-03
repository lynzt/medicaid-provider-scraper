import re
import os
import sys
import pprint as pp

from people_names import people_names
# from provider_files_config import provider_files

import database.types as types_model
import database.subtypes as subtypes_model
import database.providers as providers_model
import database.doctors as doctors_model
import database.type_providers as type_providers_model
import database.type_doctors as type_doctors_model
import database.subtype_types as subtype_types_model

from pathlib import Path


def get_provider_files(provider_files):
    p = Path(provider_files)
    files = list(p.glob('**/*.txt'))
    return files

def read_and_parse_file(path, provider_type, provider_subtype, stopwords):
    file_contents = read_file(path)
    return parse_file(file_contents, provider_type, provider_subtype, stopwords)


def read_file(path):
    with open(path) as f:
        file_contents = f.read().split("\t\t\t\t\t\t\t\t\t\t\t")
    return list(map(lambda x : x.split('\n'), file_contents))

def read_stopfile():
    with open('./stopwords.txt', 'r') as f:
        return  f.read().splitlines()

def parse_file(file_contents, provider_type, provider_subtype, stopwords):

    has_doc_name = includes_doctor_name(file_contents, stopwords)
    providers = []
    # def parse_provider_data(line, data, counter, has_doc_name):
    for s in file_contents[:6]:
        fields = list(filter(lambda x: x != '', s))
        if len(fields) == 0:
            continue

        data = {}
        data['type'] = provider_type
        data['subtype'] = provider_subtype

        providers.append(parse_provider_data(fields, data, has_doc_name, stopwords))

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
    return count_doc_name > (nbr_providers_subset/2 + 1)

def is_provider_name(stopwords, string):
    return  re.findall(r"(?=("+'|'.join(stopwords)+r"))", string)

def parse_provider_data(provider_info, data, has_doc_name, stopwords):
    if is_provider_name(stopwords, provider_info[0]):
        data['provider_name'] = provider_info[0].strip()
        start_index = 1
    elif is_provider_name(stopwords, provider_info[1]):
        doc_name = parse_doctor_name(provider_info[0].strip())
        data['doc_name'] = people_names.split_name(doc_name, 'fml')
        data['provider_name'] = provider_info[1].strip()
        start_index = 2
    elif check_regex(provider_info[1], data) == 'address':
        if has_doc_name:
            doc_name = parse_doctor_name(provider_info[0].strip())
            data['doc_name'] = people_names.split_name(doc_name, 'fml')

        else:
            data['provider_name'] = provider_info[1].strip()
        start_index = 1
    else:
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
    if re.compile('(?i)PO BOX|(?i)p.o. box').match(line):
        return 'po_box'
        # return data
    if re.compile(r'^(\d{2,}|\d+TH|\d+RD)(.+ ){2,}').match(line):
        return 'address'
    elif re.compile('^STE').match(line):
        return 'address'
    elif re.compile(r'\s\d{5}$').search(line):
        return 'address'
    elif re.compile(r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}').search(line):
        return 'phone'
    elif re.compile('(?i)Critical access provider').match(line):
        return 'critical_access_provider'
    elif re.compile('(?i)Specialty').match(line):
        return 'specialty'
    else:
        return 'other_info'
    return data


def insert_into_db(providers):
    counter = 0
    for provider in providers:
        counter += 1
        if counter % 100 == 0:
            print ('loading db: {}'.format(counter))

        # this should be in a transaction... meh
        type_id = types_model.upsert_type(provider)
        subtype_id = subtypes_model.upsert_subtype(provider)
        provider_id = providers_model.upsert_provider(provider)
        providers_model.update_provider(provider, provider_id[0])
        type_providers_model.upsert_type_provider(type_id[0], provider_id[0])
        subtype_types_model.upsert_subtype_type(subtype_id[0], type_id[0])
        if 'doc_name' in provider:
            doctor_id = doctors_model.upsert_doctor(provider['doc_name'])
            type_doctors_model.upsert_type_doctor(type_id[0], doctor_id[0])



def main():
    files = get_provider_files('./provider_files')
    stopwords = read_stopfile()
    all_providers = []

    for file in files[10:15]:
        dir, subdir, filename = file.parts
        print('\n**************subdir: {} | filename: {}'.format(subdir, filename))
        subtype, _ = filename.split(".")
        providers = read_and_parse_file(file, subdir, subtype, stopwords)# print (providers)
        # pp.pprint(providers)
        insert_into_db(providers)

        # all_providers += providers
    # return all_providers

    # providers = parse_all_providers(provider_files)
    # insert_into_db(providers)

if __name__ == '__main__':
    main()
