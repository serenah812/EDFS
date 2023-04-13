#   https://docs.python.org/3/library/asyncio-stream.html#examples
import asyncio
import subprocess


async def handle_client(reader, writer):
    data = await reader.read(100)
    message = data.decode()

    # 执行commad
    parts = message.split()
    if (parts[0] == 'edfs'):
        filename = '../Shell/dfs.py'
        args = ['python', filename]
        for i in parts:
            if(i!='edfs'):
                args.append(i)
        # print(args)
        try:
            result = subprocess.run(args, capture_output=True, text=True)
            writer.write(result.stdout.encode())
            print(result.stdout)
        except Exception as e:
            print(e)

    await writer.drain()
    writer.close()


    	# writer.write(b'edfs -ls')
    # else:
    # 	writer.write(b'File not found!')
    # await writer.drain()
    # writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8001)
    async with server:
        await server.serve_forever()


asyncio.run(main())
