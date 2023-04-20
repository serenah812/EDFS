import json
import aiohttp_cors
import asyncio
from aiohttp import web
import tracemalloc
import ast
tracemalloc.start()

def to_json(key, value):
    # 构建一个字典，包含指定的key-value
    data = {key: value}

    # 使用json.dumps函数将字典转换为JSON格式
    json_data = json.dumps(data)

    return json_data


# 数据传输给服务器
async def tcp_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8001)
    message = json.dumps(message)
    writer.write(message.encode())
    await writer.drain()
    data = await reader.read(100000)
    return data.decode()

# 前端获取Command
async def handle_upload(request):
    data = await request.json()
    command = data.get('command')
    # get output of the command from socket server
    dict = {}
    dict['type'] = 'shell'
    dict['command'] = command
    print(dict)
    output = await tcp_client(dict)
    if(data.get('content') == 'fileinfo'):
        res= []
        file_list_str = output
        file_list_str = file_list_str.strip()
        file_list = ast.literal_eval(file_list_str)

        for filename in file_list:
            comm = command + "/" + filename
            print(comm)
            res.append(to_json("filename", filename))
        print(res)
        res = '{"filename": "test-txt"}', '{"filename": "test2-txt"}', '{"filename": "user"}'
        res = json.dumps(res)
        return web.Response(text=res)
    else:
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






