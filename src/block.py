from datetime import datetime


class Block(object):

    def __init__(self, block_id, block_ntime, block_chain_work, block_num_tx, btc=False):
        self.block_id = block_id
        self.block_ntime = int(block_ntime)
        self.time = datetime.fromtimestamp(int(self.block_ntime))
        self.time_str = self.time.strftime('%Y-%m-%d %H:%M:%S')
        # NOTE: block_chain_work is actually difficulty!
        if btc:
            self.block_chain_work = int(block_chain_work)
        else:
            self.block_chain_work = int(block_chain_work, 16)  # convert from hex to int
        self.block_num_tx = int(block_num_tx)
