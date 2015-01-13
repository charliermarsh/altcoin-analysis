import csv


def get_csvreader(file_name):
    csvfile = open(file_name, 'rb')
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    csvreader.next()
    return csvreader


def work_to_difficulty(work):
    return work * ((1 << 224) - 1) * 1000 / (1 << 256) / 1000.0
