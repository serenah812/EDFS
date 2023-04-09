import aiohttp_cors
import asyncio
from aiohttp import web
import tracemalloc
tracemalloc.start()

# 数据传输给服务器
async def tcp_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8001)
    writer.write(message.encode())
    await writer.drain()
    await reader.read(100)

# 前端获取上传的文件的数据
async def handle_upload(request):
    data = await request.json()
    content = data.get('content')
    await tcp_client(content)
    return web.Response(text=content)

# 前端获取Command
async def handle_upload(request):
    data = await request.json()
    command = data.get('command')
    await tcp_client(command)
    return web.Response(text=command)

# async def handle_index(request):
#     with open('UI/UI.html') as f:
#         content = f.read()
#         return web.Response(text=content, content_type='text/html')

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






