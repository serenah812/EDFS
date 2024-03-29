#   https://docs.python.org/3/library/asyncio-stream.html#examples
import asyncio
import subprocess
import json
import math

def size_to_bytes(size_str):
    units = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3, "TB": 1024 ** 4}
    size = size_str.split()
    for unit, factor in units.items():
        if unit == size[1]:
            # size[] = float(size_str.replace(unit, ""))
            return int(int(size[0]) * factor)
    return  1
    raise ValueError("Invalid size format: " + size_str)

def run_command(args):
    try:
        subprocess.run(args, capture_output=True, text=True)
    except Exception as e:
        print(e)

def MetaData(filename,blocks,replication,BlockNum,filepath):
    pyfilename = '../Shell/dfs.py'
    # 输入文件名称
    if filepath.startswith('/MetaData'):
        filepath = filepath[9:]
    if not filepath.endswith('/'):
        filepath = filepath+'/'

    try:
        args = ['python', pyfilename, '-mkdir', filepath+str(filename)]
        run_command(args)
    except Exception as e:
        print(e)
    # 输入文件block数量
    data = {"BlockNumber": BlockNum, "Replication": int(replication)}
    data.update(blocks)
    args = ['python',
            pyfilename,
            '-create',
            '/MetaData' + filepath + str(filename),
            json.dumps(data)
            ]
    try:
        run_command(args)
    except Exception as e:
        print(e)

def DataNode(Datanode,filename,data,Num):
    pyfilename = '../Shell/dfs.py'
    # 输入文件名称
    try:
        args = ['python', pyfilename, '-createDataNode', '/'+ Datanode +'/'+str(filename)]
        run_command(args)
    except Exception as e:
        print(e)
    # 输入文件block数量
    dataname = str(Num)
    data = {dataname: data}
    args = ['python',
            pyfilename,
            '-create',
            '/'+ Datanode +'/' + str(filename),
            json.dumps(data)
            ]
    try:
        run_command(args)
    except Exception as e:
        print(e)

def get_byte_count(my_string, encoding='utf-8'):
    byte_seq = my_string.encode(encoding)
    return len(byte_seq)

def divide_ceil(numerator, denominator):
    quotient, remainder = divmod(numerator, denominator)
    if remainder > 0:
        quotient += 1
    return quotient

def split_content(s,num_bytes):
    byte_index = 0
    result = []
    while byte_index < len(s.encode("utf-8")):
        result.append(s[byte_index:byte_index + num_bytes])
        byte_index += num_bytes
    return result

async def handle_client(reader, writer):
    data = await reader.read(100000)
    message = data.decode()
    print(message)
    message = json.loads(message)
    # 执行commad
    if message.get('type') == 'shell':
        parts = message.get('command').split()
        if (parts[0] == 'edfs'):
            filename = '../Shell/dfs.py'
            args = ['python', filename]
            for i in parts:
                if(i!='edfs'):
                    args.append(i)
            try:
                if args[2] == '-put':
                    result = subprocess.run(args, capture_output=True, text=True)
                    if result.stdout == '':
                        local_path = args[3]
                        edfs_path = args[4]
                        file_name_encoded = local_path[local_path.rfind('/')+1:].replace(".", "-")
                        with open(local_path) as f:
                            file_content = f.read()
                        message = {
                            'type': 'upload',
                            'filepath': edfs_path,
                            'filename': file_name_encoded,
                            'content': file_content,
                            'replication': '1', 
                            'blocksize': '60 B'
                            }
                    else:
                        writer.write(result.stdout.encode())
                else:
                    result = subprocess.run(args, capture_output=True, text=True)
                    writer.write(result.stdout.encode())
            except Exception as e:
                print(e)

    # upload file
    if message.get('type') == 'upload':
        filename = message.get('filename')
        content = message.get('content')
        replication = message.get('replication')
        blocksize = message.get('blocksize')
        filepath = message.get('filepath')

        bytes_num = get_byte_count(content)
        Block_byte = size_to_bytes(blocksize)
        BlockNum = divide_ceil(bytes_num, Block_byte)
        blocks = {}
        Blocks = 3
        result = split_content(content, Block_byte)
        for i in range(BlockNum):
            b = 'Block'+str(i)
            blocks[b] = 'DataNode'+str(i%Blocks)
            DataNode('DataNode'+str(i%Blocks), filename, result[i], Num='Block'+str(i))
        MetaData(filename,blocks,replication,BlockNum,filepath)

    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8001)
    async with server:
        await server.serve_forever()

asyncio.run(main())
