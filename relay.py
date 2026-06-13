import asyncio, os, sys, urllib.parse
import websockets

AUTH_TOKEN = "8b417e59a39abfea9c4eea850ad362eb"

async def handle(ws):
    try:
        # 从路径参数获取目标
        path = ws.request.path if hasattr(ws, 'request') else ws.path
        qs = path.split('?',1)[1] if '?' in path else ''
        params = urllib.parse.parse_qs(qs)
        host = params.get('host', [None])[0]
        port = int(params.get('port', ['443'])[0])
        
        if not host:
            await ws.close(4000, "Missing host")
            return
        
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
