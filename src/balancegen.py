"""
    Calculates every pubkey's balance after transactions that impact them

    Usage:
        src/balancegen.py edges.csv ~/Desktop/balances.pickle
        src/balancegen.py edges.csv --print

    Output:
        Pickled data structure is a dictionary with pubkey_id as key
        and list of (tx_id, balance after tx_id)

    Tests:
        # should produce the following holdings:
        #   2: (0,5000000000), (127,0)
        #   3: (0,5000000000), (132,0)
        #   4: (0,5000000000), (133,0)
        #   5: (0,0), (127,4999000000)
        #   6: (0,0), (127,1000000)
        #   7: (0,0), (132, 4999000000)
        #   8: (0,0), (132, 1000000)
        #   9: (0,0), (133, 4999000000)
        #   10: (0,0), (133, 1000000)
        src/balancegen.py src/tests/balancetest.csv --print
"""

import sys
import os
import logging
import pickle
from collections import defaultdict

import config
import utils

logging.basicConfig(level=logging.INFO)
EMPTY_OUTPUT = -1
INPUT_FILE = os.path.expanduser(sys.argv[1])
INPUT_COUNTS_FILE = os.path.expanduser(sys.argv[2])
OUTPUT_COUNTS_FILE = os.path.expanduser(sys.argv[3])

OUTPUT_FILENAME = None
SHOULD_PRINT = False
if sys.argv[2] == "--print":
    SHOULD_PRINT = True
else:
    OUTPUT_FILENAME = os.path.expanduser(sys.argv[4])


def log(msg):
    logging.info(msg)

input_counts = defaultdict(int)
output_counts = defaultdict(int)
for row in utils.get_csvreader(INPUT_COUNTS_FILE):
    if len(row) > 1:
        input_counts[int(row[0])] = int(row[1])
for row in utils.get_csvreader(OUTPUT_COUNTS_FILE):
    if len(row) > 1:
        output_counts[int(row[0])] = int(row[1])


def update_balances(tx_inputs, tx_outputs, balances):
    # Correct for multiple counts
    input_set = set(tx_inputs.keys())
    output_set = set(tx_outputs.keys())

    for pubkey in tx_inputs.keys():
        tx_inputs[pubkey] /= output_counts[last_tx]
    for pubkey in tx_outputs.keys():
        tx_outputs[pubkey] /= input_counts[last_tx]

    both = input_set.intersection(output_set)
    for pubkey in both:
        if pubkey not in balances:
            balances[pubkey] = [(0, tx_inputs[pubkey])]

        if balances[pubkey][-1][1] - tx_inputs[pubkey] + tx_outputs[pubkey] < 0:
            print pubkey, last_tx, balances[pubkey][-1], tx_inputs[pubkey] / 2, tx_outputs[pubkey] / 32
        balances[pubkey].append(
            (last_tx, balances[pubkey][-1][1] - tx_inputs[pubkey] + tx_outputs[pubkey])
        )

    only_output = output_set.difference(input_set)
    for pubkey in only_output:
        if pubkey not in balances:
            balances[pubkey] = [(0, 0)]
        balances[pubkey].append(
            (last_tx, balances[pubkey][-1][1] + tx_outputs[pubkey])
        )

    only_input = input_set.difference(output_set)
    for pubkey in only_input:
        # Check for coingen
        if pubkey == config.COINGEN_ADDRESS:
            continue

        if pubkey not in balances:
            balances[pubkey] = [(0, tx_inputs[pubkey])]
        balances[pubkey].append(
            (last_tx, balances[pubkey][-1][1] - tx_inputs[pubkey])
        )

log("Creating data structures")
balances = {}  # key is pubkey and value is list of (tx_id, balance after tx_id)

last_tx = None
tx_inputs = defaultdict(int)
tx_outputs = defaultdict(int)
counter = 0
for row in utils.get_csvreader(INPUT_FILE):
    if len(row) < 2:
        continue

    if counter % 1000 == 0:
        log("Calculating balance: %s" % counter)

    tx_id = int(row[0])

    # Detect coingen
    try:
        pubkey_input = int(row[1])
        value_input = int(row[2])
    except:
        pubkey_input = config.COINGEN_ADDRESS
        value_input = 0

    try:
        pubkey_output = int(row[3])
    except:
        pubkey_output = EMPTY_OUTPUT
    value_output = int(row[4])

    if tx_id != last_tx and tx_inputs:
        # end of reading a transaction series. Update balances

        update_balances(tx_inputs, tx_outputs, balances)

        tx_inputs = defaultdict(int)
        tx_outputs = defaultdict(int)

    last_tx = tx_id
    tx_inputs[pubkey_input] += value_input
    if pubkey_output != EMPTY_OUTPUT:
        tx_outputs[pubkey_output] += value_output

    counter += 1

update_balances(tx_inputs, tx_outputs, balances)

if SHOULD_PRINT:
    log("Printing balances")
    for pubkey in balances:
        print "%s:%s" % (pubkey, balances[pubkey])

if OUTPUT_FILENAME:
    log("Pickling (takes a few minutes)")
    with open(OUTPUT_FILENAME, 'wb') as handle:
        pickle.dump(balances, handle)
