import csv
import pickle
import operator

import config
import address_handler


class GraphAnalyzer(object):

    def __init__(self, ticker):
        self.ticker = ticker.lower()
        self._load_balances()
        self._load_clusters()

        # A value just larger than the largest tx_id
        # If you ever ignore the tx_id keyword argument, it will default to this
        self.now_tx_id = 0
        for pubkey in self.balances:
            for (tx_id, _) in self.balances[pubkey]:
                self.now_tx_id = max(self.now_tx_id, tx_id)
        self.now_tx_id += 1

    def _load_clusters(self):
        self.clusters = {}  # cluster_id : list of member pubkeys
        self.clusters_by_pubkey = {}  # pubkey_id : cluster_id

        # load clusters
        cluster_file_path = config.data_dir + 'clusters/clusters-%s.txt' % self.ticker
        csvfile = open(cluster_file_path, 'rb')
        csvreader = csv.reader(csvfile, delimiter=',')

        cluster_id = 0
        pubkeys_seen = []
        for row in csvreader:
            self.clusters[cluster_id] = [int(x) for x in row]
            pubkeys_seen.extend(self.clusters[cluster_id])

            for pubkey in self.clusters[cluster_id]:
                self.clusters_by_pubkey[pubkey] = cluster_id

            cluster_id += 1

        unseen_keys = set(self.balances.keys()).difference(set(pubkeys_seen))
        for pubkey in unseen_keys:
            self.clusters[cluster_id] = [pubkey]
            cluster_id += 1

    def _load_balances(self):
        self.balances = {}  # key is pubkey and value is list of (tx_id, balance after tx_id)
        balance_file_path = config.data_dir + 'balances/balances-%s.pickle' % self.ticker
        with open(balance_file_path, 'rb') as handle:
            self.balances = pickle.load(handle)

    def cluster_for_pubkey(self, pubkey_id):
        return self.clusters_by_pubkey[pubkey_id]

    def pubkey_for_address(self, address):
        return address_handler.encode_address(address, self.ticker)

    def pubkey_exists(self, pubkey_id, tx_id=None):
        """Returns True if pubkey_id was used before transaction tx_id"""
        if tx_id is None:
            tx_id = self.now_tx_id

        (first_activity_tx_id, _) = self.balances[pubkey_id][1]
        return first_activity_tx_id < tx_id

    def cluster_exists(self, cluster_id, tx_id=None):
        """Returns True if any pubkey in cluster_id was used before transaction tx_id"""
        if tx_id is None:
            tx_id = self.now_tx_id

        return any(
            [self.pubkey_exists(pubkey_id, tx_id=tx_id) for pubkey_id in self.clusters[cluster_id]]
        )

    def balance_for_blockchain(self, tx_id=None):
        """Return the total amount of coin in the blockchain at time tx_id"""
        if tx_id is None:
            tx_id = self.now_tx_id

        return sum([self.balance_for_pubkey(pubkey_id, tx_id=tx_id) for pubkey_id in self.balances])

    def balance_for_pubkey(self, pubkey_id, tx_id=None):
        """Returns the current balance for a pubkey at the time represented by tx_id"""
        if tx_id is None:
            tx_id = self.now_tx_id

        if pubkey_id not in self.balances:
            return 0

        for i, balance_data in enumerate(self.balances[pubkey_id]):
            if balance_data[0] > tx_id:
                if i > 0:
                    return self.balances[pubkey_id][i - 1][1]

        if len(self.balances[pubkey_id]) > 0:
            return self.balances[pubkey_id][-1][1]

        return 0

    def balance_for_cluster(self, cluster_id, tx_id=None):
        """Returns the total balance for a cluster at the time represented by tx_id"""
        if tx_id is None:
            tx_id = self.now_tx_id

        return sum(
            [self.balance_for_pubkey(pubkey_id, tx_id=tx_id)
             for pubkey_id in self.clusters[cluster_id]]
        )

    def mean_balance_for_cluster(self, tx_id=None):
        """Returns the mean cluster balance at the time represented by tx_id"""
        if tx_id is None:
            tx_id = self.now_tx_id

        existing_clusters = [
            cluster_id for cluster_id in self.clusters if self.cluster_exists(cluster_id, tx_id=tx_id)
        ]

        num = sum(
            [self.balance_for_cluster(cluster_id, tx_id=tx_id) for cluster_id in existing_clusters]
        )
        denom = float(len(existing_clusters))

        if denom == 0:
            return None
        return num / denom

    def richest_n_clusters(self, n, tx_id=None):
        """Returns a list of the n richest clusters, represented as (cluster_id, balance) pairs."""
        if tx_id is None:
            tx_id = self.now_tx_id

        cluster_balances = {
            cluster_id: self.balance_for_cluster(cluster_id, tx_id=tx_id) for cluster_id in self.clusters
        }
        return sorted(cluster_balances.items(), key=operator.itemgetter(1), reverse=True)[:n]

    def largest_n_clusters(self, n):
        """Returns a list of the n largest clusters, represented as (cluster_id, size) pairs."""
        cluster_sizes = {
            cluster_id: len(self.clusters[cluster_id]) for cluster_id in self.clusters
        }
        return sorted(cluster_sizes.items(), key=operator.itemgetter(1), reverse=True)[:n]
