from os import listdir, makedirs
from os.path import isfile, join, exists
from collections import defaultdict
import xml.etree.ElementTree as ET
import yaml
import shutil


def main():
    with open('balance_config.yml', 'r') as cfg:
        config = yaml.load(cfg)
    print(config)
    cat_dict = defaultdict(list)
    output_dir = config['output']
    sample_size = config['size_per_category']
    include_none = config['include_none']
    for folder in config['folders']:
        folder_dict = get_samples_from_folder(folder,
                                              sample_size,
                                              include_none)
        for label in folder_dict.keys():
            cat_dict[label].extend(folder_dict[label])
    print('Total:', [(k, len(v)) for k, v in cat_dict.items()])
    for label in cat_dict.keys():
        cat_dict[label] = cat_dict[label][:sample_size]
    print('Trimmed:', [(k, len(v)) for k, v in cat_dict.items()])
    print('Copying to ', output_dir)
    copy_files(cat_dict, output_dir)


def get_samples_from_folder(folder, sample_size, include_none):
    sample_dict = defaultdict(list)
    print('Processing ', folder)
    img_paths = [join(folder, ''.join(f.split('.')[:-1])) for f in
                 listdir(folder) if isfile(join(folder, f)) and
                 f.split('.')[-1] == 'jpg']
    for img in img_paths:
        try:
            anno = ET.parse(img + '.xml')
            labels_in_file = set()
            for obj in anno.findall('object'):
                name = obj.find('name').text.lower().strip()
                labels_in_file.add(name)
            for label in labels_in_file:
                if len(sample_dict[label]) < sample_size:
                    sample_dict[label].append(img)
        except FileNotFoundError:
            if include_none:
                if len(sample_dict['none']) < sample_size:
                    sample_dict['none'].append(img)
    return sample_dict


def copy_files(cat_dict, output_dir):
    if not exists(output_dir):
        makedirs(output_dir)
    for files_per_label in cat_dict.values():
        for img_id in files_per_label:
            img_path = img_id + '.jpg'
            xml_path = img_id + '.xml'
            blank_img_id = img_path.split('/')[-1]
            blank_xml_id = xml_path.split('/')[-1]
            if isfile(img_path) and isfile(xml_path):
                shutil.copy(img_path, join(output_dir, blank_img_id))
                shutil.copy(xml_path, join(output_dir, blank_xml_id))
            else:
                print('Error copying {}, either xml or jpg is invalid!'
                      .format(img_path))
    print('Copy finished')

if __name__ == '__main__':
    main()
