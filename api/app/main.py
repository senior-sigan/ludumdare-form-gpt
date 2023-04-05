from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            print('received msg={}'.format(data))
            await websocket.send_text(f"Message text was: {data['answer']}")
    except WebSocketDisconnect:
        # TODO: handle disconnect
        pass