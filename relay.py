import asyncio, struct, os, sys
import websockets

AUTH_TOKEN = "8b417e59a39abfea9c4eea850ad362eb"

async def handle(ws):
    try:
        data = await asyncio.wait_for(ws.recv(), timeout=10)
        # 格式: [1 byte auth_len][auth][1 byte host_len][host][2 bytes port]
        pos = 0
        auth_len = data[pos]; pos += 1
        auth = data[pos:pos+auth_len].decode(); pos += auth_len
        if auth != AUTH_TOKEN:
            await ws.close(4001, "Bad auth")
            return
        host_len = data[pos]; pos += 1
        host = data[pos:pos+host_len].decode(); pos += host_len
        port = struct.unpack('!H', data[pos:pos+2])[0]
        
        print(f"Relay: {host}:{port}", flush=True)
        reader, writer = await asyncio.open_connection(host, port)
        
        async def ws2tcp():
            try:
                async for msg in ws:
                    if isinstance(msg, bytes): writer.write(msg); await writer.drain()
            except: pass
        async def tcp2ws():
            try:
                while True:
                    d = await reader.read(8192)
                    if not d: break
                    await ws.send(d)
            except: pass
        await asyncio.gather(ws2tcp(), tcp2ws())
    except Exception as e:
        print(f"Error: {e}", flush=True)

async def main():
    port = int(os.environ.get("PORT", "8080"))
    async with websockets.serve(handle, "0.0.0.0", port):
        print(f"Relay on :{port}", flush=True)
        await asyncio.Future()

asyncio.run(main())
