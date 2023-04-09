class MetadataServer:
    def __init__(self):
        self.file_to_blocks = {}  # map filename to list of blocks
        self.block_to_servers = {}  # map block ID to list of data server addresses

    def register_block(self, block_id, server_addr):
        if block_id not in self.block_to_servers:
            self.block_to_servers[block_id] = []
        self.block_to_servers[block_id].append(server_addr)

    def allocate_blocks(self, filename):
        num_blocks = 1  # for simplicity, we assume all files are one block
        block_ids = [i for i in range(num_blocks)]
        self.file_to_blocks[filename] = block_ids
        return block_ids

    def get_block_locations(self, block_id):
        if block_id in self.block_to_servers:
            return self.block_to_servers[block_id]
        else:
            return []

    def list_directory(self, dir_path):
        files = []
        for filename in self.file_to_blocks:
            if filename.startswith(dir_path):
                files.append(filename)
        return files