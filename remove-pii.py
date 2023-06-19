import json
import re
import sys

def remove_pii(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    pii_data = {}
    placeholder_id = 1

    def replace_pii(obj):
        nonlocal placeholder_id
        if isinstance(obj, dict):
            keys_to_remove = []
            for key, value in obj.items():
                if key == 'regex':
                    pii_data[f'regex-{placeholder_id}'] = value
                    keys_to_remove.append(key)
                    obj[key] = 'PII removed'
                    placeholder_id += 1
                elif key in ['createdDate', 'templateLink', 'uuid', 'id', 'accountId', 'contractId', 'groupId', 'ruleFormat', 'propertyId', 'propertyName', 
'propertyVersion']:
                    keys_to_remove.append(key)
                    obj[key] = 'PII removed'
                elif key == 'customCertificateAuthorities':
                    obj[key] = []
                elif isinstance(value, str):
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value) or \
                       re.match(r'^[\w.-]+\.[a-zA-Z]{2,}$', value) or \
                       re.match(r'^\*\.[\w.-]+\.[a-zA-Z]{2,}$', value):
                        pii_data[f'domain-{placeholder_id}'] = value
                        obj[key] = f'placeholder-{placeholder_id}.com'
                        placeholder_id += 1
                    elif re.match(r'^/[\w./-]*$', value) or re.match(r'^/[\w./-]*\*$', value):
                        pii_data[f'path-{placeholder_id}'] = value
                        obj[key] = f'/placeholder-{placeholder_id}/'
                        placeholder_id += 1
                elif key == 'customCertificates':
                    pii_data[f'customCertificates-{placeholder_id}'] = value
                    obj[key] = []
                    placeholder_id += 1
                else:
                    replace_pii(value)
            for key in keys_to_remove:
                obj.pop(key, None)

        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                if isinstance(item, str):
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', item) or \
                       re.match(r'^[\w.-]+\.[a-zA-Z]{2,}$', item) or \
                       re.match(r'^\*\.[\w.-]+\.[a-zA-Z]{2,}$', item):
                        pii_data[f'domain-{placeholder_id}'] = item
                        obj[index] = f'placeholder-{placeholder_id}.com'
                        placeholder_id += 1
                    elif re.match(r'^/[\w./-]*$', item) or re.match(r'^/[\w./-]*\*$', item):
                        pii_data[f'path-{placeholder_id}'] = item
                        obj[index] = f'/placeholder-{placeholder_id}/'
                        placeholder_id += 1
                else:
                    replace_pii(item)

    replace_pii(data)

    with open('pii_removed.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

    with open('pii_data.json', 'w') as outfile:
        json.dump(pii_data, outfile, indent=4)

if __name__ == "__main__":
    input_file = input("Enter the input JSON file name: ")
    remove_pii(input_file)
