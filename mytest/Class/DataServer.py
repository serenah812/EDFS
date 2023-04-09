class DataServer:
    def __init__(self, addr):
        self.addr = addr
        self.blocks = {}  # map block ID to data contents

    def get_block(self, block_id):
        if block_id in self.blocks:
            return self.blocks[block_id]
        else:
            return None

    def put_block(self, block_id, data):
        self.blocks[block_id] = data