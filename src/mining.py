import csv
import bisect

import config


class MiningAnalyzer(object):

    def __init__(self, graph_analyzer):
        self.graph_analyzer = graph_analyzer
        self.ticker = self.graph_analyzer.ticker
        self.now_tx_id = self.graph_analyzer.now_tx_id
        self._load_miners()

    def _load_miners(self):
        # Store the mining information as: (tx_id, output_pubkey_id)
        file_path = config.data_dir + 'csv_exports/edges-%s.csv' % self.ticker.lower()
        seen_tx_ids = set([])
        with open(file_path, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')

            # Aggregate miners
            miners = []
            tx_ids = []
            for row in csvreader:
                # Skip header
                if row[0] == 'tx_id':
                    continue

                try:
                    this_tx_id = int(row[0])
                    input_pubkey_id = row[1]
                    output_pubkey_id = int(row[3])
                except:
                    continue

                if this_tx_id in seen_tx_ids:
                    continue

                if input_pubkey_id == config.COINGEN_ADDRESS:
                    tx_ids.append(this_tx_id)
                    miners.append(output_pubkey_id)
                    seen_tx_ids.add(this_tx_id)

            self.tx_ids = tx_ids
            self.miners = miners

    def num_blocks(self, tx_id=None):
        """Return the number of blocks mined before tx_id."""
        if tx_id is None:
            tx_id = self.now_tx_id

        miner_pubkeys = self.miner_pubkeys(tx_id=tx_id)
        return len(miner_pubkeys)

    def miner_pubkeys(self, tx_id=None):
        """Return the public keys for blocks mined before tx_id."""
        if tx_id is None:
            tx_id = self.now_tx_id

        idx = bisect.bisect_left(self.tx_ids, tx_id)
        return self.miners[:idx]

    def num_blocks_by_cluster(self, cluster_id, tx_id=None):
        """Return the number of blocks mined by cluster_id before tx_id."""
        if tx_id is None:
            tx_id = self.now_tx_id

        cluster_pubkeys = set(self.graph_analyzer.clusters[cluster_id])
        miner_pubkeys = self.miner_pubkeys(tx_id=tx_id)
        num_mined_blocks = len(
            [pubkey_id for pubkey_id in miner_pubkeys if pubkey_id in cluster_pubkeys]
        )
        return num_mined_blocks
