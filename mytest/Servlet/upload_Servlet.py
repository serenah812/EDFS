import aiohttp_cors
import asyncio
from aiohttp import web
import tracemalloc
import json

tracemalloc.start()

# 数据传输给服务器
async def tcp_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8001)
    message = json.dumps(message)
    writer.write(message.encode())
    await writer.drain()
    data = await reader.read(1000)
    return data.decode()

# 前端获取上传的文件的数据
async def handle_upload(request):
    data = await request.json()
    print(data)
    content = data.get('content')
    filename = data.get('filename')
    replication = data.get('replication')
    blocksize = data.get('blocksize')
    # 创建一个空字典,添加键值对
    dict = {}
    dict['type'] = 'upload'
    dict['content'] = content
    filename = filename.replace(".", "-")
    dict['filename'] = filename
    dict['replication'] = replication
    dict['blocksize'] = blocksize
    await tcp_client(dict)
    return web.Response(text="success")

#配置webapp接受前端数据
app = web.Application()
app.add_routes([
    web.post('/upload', handle_upload)
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

web.run_app(app, port=8000)






