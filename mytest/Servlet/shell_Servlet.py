import json
import aiohttp_cors
import asyncio
from aiohttp import web
import tracemalloc
tracemalloc.start()

# 数据传输给服务器
async def tcp_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8001)
    message = json.dumps(message)
    writer.write(message.encode())
    await writer.drain()
    data = await reader.read(100)
    return data.decode()

# 前端获取Command
async def handle_upload(request):
    data = await request.json()
    command = data.get('command')
    # get output of the command from socket server
    dict = {}
    dict['type'] = 'shell'
    dict['command'] = command
    output = await tcp_client(dict)
    # if(command == 'edfs -ls /MetaData'):
    #     output =json.dumps({'fileName':'text.txt'})
    return web.Response(text=output)

#配置webapp接受前端数据
app = web.Application()
app.add_routes([
    web.post('/shell', handle_upload)
    # web.get('/', handle_index),
    # web.static('/', './')
])
# 设置 CORS 头
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})
# 将 CORS 应用于所有路由
for route in list(app.router.routes()):
    cors.add(route)

web.run_app(app, port=7999)






