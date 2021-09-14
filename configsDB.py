#!/usr/bin/env python

# WS server example that synchronizes state across clients
import os
import asyncio
import json
import websockets
import subprocess
import time
import sqlite3
import requests

STATE = {"value": 0}

USERS = set()
Active = []



async def register(websocket):
    USERS.add(websocket)
    Active.append({'user':websocket})
    print(USERS)
    


async def unregister(websocket):
    for x in range(len(Active)):
        if Active[x]['user'] == websocket:
            USERS.remove(websocket)
            Active.pop(x)

async def sql(cmd):
    connection = sqlite3.connect("vos.db")
    conn       = connection.cursor()
    row = conn.execute(cmd).fetchall()
    data = {"type":"sql","value":row}
    print(row)
    connection.commit()
    await Active[0]['user'].send(json.dumps(data))
    await Active[0]['user'].send("Break")
    return row


async def run(bash_process,cmd):
    bash_process.stdin.write(cmd)
    bash_process.stdin.close()
    while True:
        output = bash_process.stdout.readline()
        if output.decode("utf-8") == "" and bash_process.poll() is not None:
            await Active[0]['user'].send("Break")
            print("______Breaking Active User______")
            break
        if output.decode("utf-8") != "":
            msg = json.dumps({"type": "sh", "value":output.decode("utf-8")})
            await Active[0]['user'].send(msg)
            print(msg)
            
async def ide(bash_process,cmd):
    bash_process.stdin.write(cmd)
    bash_process.stdin.close()
    time.sleep(10)
    req = requests.get(url="http://localhost:4040/api/tunnels")
    data = json.dumps(req.text)
    msg = json.dumps({"type": "ide", "value":data})
    await Active[0]['user'].send(msg)
    print(msg)
    await Active[0]['user'].send("Break")
    
async def init(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        bash_process = subprocess.Popen(args=['sh'], stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == "sql":
                await sql(data['cmd'])
            if data['type'] == "sh":
                await run(bash_process, data['cmd'].encode('UTF-8'))
            if data['type'] == "ide":
                await ide(bash_process,data['cmd'].encode('UTF-8'))
    finally:
        bash_process.close()
        await unregister(websocket)


start_server = websockets.serve(init, "0.0.0.0", 7777)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()