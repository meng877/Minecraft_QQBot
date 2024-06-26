from Config import config
from Minecraft import server_manager

from json import dumps

from nonebot import get_driver, get_bot
from nonebot.log import logger
from nonebot.drivers import HTTPServerSetup, ASGIMixin, Request, Response, URL


async def send_message(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'Success': False}))
    bot = get_bot()
    if message := request.json.get('message'):
        logger.info(F'发送消息到同步消息群！消息为 {message} 。')
        for group_id in config.sync_groups:
            await bot.send_group_msg(group_id=group_id, message=message)
    return Response(200, content=dumps({'Success': True}))


async def server_startup(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'Success': False}))
    logger.info(F'收到服务器开启数据！尝试连接到服务器……')
    server_manager.connect_server(request.json)
    return Response(200, content=dumps({'Success': True, 'bot_prefix': config.bot_prefix.upper()}))


async def server_shutdown(request: Request):
    if request.json.get('token') != config.token:
        return Response(403, content=dumps({'Success': False}))
    logger.info(F'收到服务器关闭信息！正在断开连接……')
    server_manager.disconnect_server(request.json.get('name'))
    return Response(200, content=dumps({'Success': True}))


def setup_http_server():
    if isinstance(driver := get_driver(), ASGIMixin):
        http_server = HTTPServerSetup(
            URL('/send_message'), 'POST', 'send_message', send_message)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(
            URL('/server/startup'), 'POST', 'server_startup', server_startup)
        driver.setup_http_server(http_server)
        http_server = HTTPServerSetup(
            URL('/server/startup'), 'POST', 'server_shutdown', server_shutdown)
        driver.setup_http_server(http_server)
