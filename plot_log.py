import json
import string
from collections import defaultdict
import matplotlib.pyplot as plt
from os import makedirs
from os.path import exists
import yaml

LABELS = ['siegessaeule',
          'fernsehturm',
          'funkturm',
          'berlinerdom',
          'other',
          'brandenburgertor',
          'reichstag',
          'rotesrathaus']
OTHER_RESULTS = ['main/loss',
                 'main/loss/conf',
                 'main/loss/loc']

with open('plot_config.yml', 'r') as cfg:
    CONFIG = yaml.load(cfg)


def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')
    return filename


def plot_for_key(data, label, desc):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot([x[0] for x in data[label]],
            [x[1] for x in data[label]])
    plt.ylabel(desc)
    plt.xlabel('iterations')
    plt.semilogy()
    plt.tight_layout()
    if CONFIG['save_plots']:
        if not exists(CONFIG['output']):
            makedirs(CONFIG['output'])
        fig.savefig(CONFIG['output'] + format_filename(label) + '.png')
    else:
        plt.show()
    plt.close(fig)


def main():
    data_rows = defaultdict(list)
    with open(CONFIG['input_file'], 'r') as log:
        log_data = json.load(log)
        for log_item in log_data:
            if 'validation/main/ap/none' in log_item.keys():
                for label in LABELS:
                    data_rows[label].append((log_item['iteration'],
                                             log_item['validation/main/ap/{}'
                                             .format(label)]))
                data_rows['validation/main/map'] \
                    .append((log_item['iteration'],
                             log_item['validation/main/map']))
            for key in OTHER_RESULTS:
                data_rows[key].append((log_item['iteration'],
                                       log_item[key]))
    print(data_rows)
    for label in LABELS:
        plot_for_key(data_rows, label, 'average precision {}'.format(label))
    for key in OTHER_RESULTS:
        plot_for_key(data_rows, key, key)
    plot_for_key(data_rows, 'validation/main/map', 'mean avg precision')

if __name__ == '__main__':
    main()
