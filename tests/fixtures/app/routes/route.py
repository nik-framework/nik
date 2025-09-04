import asyncio

from nik.views.elements import Div


async def action():
    await asyncio.sleep(0.1)


async def view():
    await asyncio.sleep(0.1)
    return Div("Home Page")
