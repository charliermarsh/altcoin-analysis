"""
    Identifies clusters in an edge CSV

    Usage:
        src/clustergen.py edges.csv > ~/Desktop/clusters.txt

    Tests:
        # should produce 2 clusters on Heuristic 2 alone
        src/clustergen.py src/tests/heuristic2test.csv > ~/Desktop/clusters.txt

"""

import sys
import os
import logging

import config
import utils

logging.basicConfig(level=logging.INFO)
INPUT_FILE = os.path.expanduser(sys.argv[1])

def log(msg):
    logging.info(msg)

log("Creating data structures")

# maintaining two dictionaries saves time by using more memory
clusters = {} #  cluster_id : list of pubkeys
cluster_directory = {} # pubkey : cluster_id

for row in utils.get_csvreader(INPUT_FILE):
    if len(row) < 2:
        continue
    clusters[row[1]] = [row[1]]
    cluster_directory[row[1]] = row[1]

    clusters[row[3]] = [row[3]]
    cluster_directory[row[3]] = row[3]

log("Generating clusters with Heuristic 1")
last_transaction_id = None
last_cluster_id = None
counter = 0
for row in utils.get_csvreader(INPUT_FILE):
    if len(row) < 2:
        continue

    if counter % 1000 == 0:
        log("Heuristic 1: %s" % counter)

    tx_id = row[0]
    pubkey_id = row[1]

    if pubkey_id == config.COINGEN_ADDRESS:
        continue

    if last_transaction_id == tx_id:
        # within a transaction, so add this and peers to last_cluster_id
        current_home = cluster_directory[pubkey_id]

        if current_home != last_cluster_id:
            clusters[last_cluster_id].extend(clusters[current_home])

            for pubkey in clusters[current_home]:
                cluster_directory[pubkey] = last_cluster_id
            clusters[current_home] = []
    else:
        # new transaction, so record new last_ values
        last_transaction_id = tx_id
        last_cluster_id = cluster_directory[pubkey_id]

    counter += 1

log("Generating clusters with Heuristic 2")
keys_seen = {}
last_tx = None
tx_inputs = {}
tx_outputs = {}
counter = 0
for row in utils.get_csvreader(INPUT_FILE):
    if len(row) < 2:
        continue

    if counter % 1000 == 0:
        log("Heuristic 2: %s" % counter)

    tx_id = row[0]
    pubkey_input = row[1]
    pubkey_output = row[3]

    if tx_id != last_tx and tx_inputs:
        # end of reading a transaction series, run heuristic

        # 4.3.1, 4.3.4: must be first output
        # appearance and the only output key as such
        exists_unique_first_appearance = None
        for pubkey in tx_outputs:
            if pubkey not in keys_seen and not exists_unique_first_appearance:
                exists_unique_first_appearance = pubkey
            elif pubkey not in keys_seen and exists_unique_first_appearance:
                exists_unique_first_appearance = False
                break

        # 4.3.2: not coin generation
        is_coin_gen = config.COINGEN_ADDRESS in tx_inputs

        # 4.3.3: no key in output is also in input
        is_self_change = False
        for pubkey in tx_outputs:
            if pubkey in tx_inputs:
                self_change = True

        # additional heuristic: must be more than one output
        multiple_outputs = False
        if len(tx_outputs) > 1:
            multiple_outputs = True

        # merge clusters if appropriate
        if (exists_unique_first_appearance and
                not is_coin_gen and not is_self_change and multiple_outputs):
            change_address = exists_unique_first_appearance

            current_home = cluster_directory[change_address]
            first_input_current_home = cluster_directory[tx_inputs.keys()[0]]

            if current_home != first_input_current_home:
                clusters[first_input_current_home].extend(clusters[current_home])

                for pubkey in clusters[current_home]:
                    cluster_directory[pubkey] = first_input_current_home
                clusters[current_home] = []

        for key in tx_outputs:
            keys_seen[key] = True

        tx_inputs = {}
        tx_outputs = {}

    last_tx = tx_id
    tx_inputs[pubkey_input] = True
    tx_outputs[pubkey_output] = True

    counter += 1

log("Exporting non-trivial clusters")
for key in clusters:
    if len(clusters[key]) > 1:
        print ",".join(clusters[key])
