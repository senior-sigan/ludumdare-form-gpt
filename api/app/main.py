from typing import Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

SYSTEM_MSG = '''
Ты помощник для опросов с характером цундере, как Аска из Евангелиона. Отвечай коротко, но с постиронией и шутками.
Вот список вопросов: "Название вашей команды? Напишите состав своей команды и вообще о себе. Где планируете хакатонить в точке кипения или из дома? Как вы будете готовиться к Людуму? На чём планируете делать игру на Людуме? Наконец, дайте совет остальным участникам".
В конце благодари за ответы и закончи диалог.
'''

def sendToChatGPT(context: List[Any]):
    system_msgs = [{
        "role": "system", 
        "content": SYSTEM_MSG.strip()
    },{
        'role': 'user',
        'content': 'Задай первый вопрос'
    }
    ]
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=system_msgs + context,
    )
    return resp.choices[0].message.content



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    prompts = []
    try:
        while True:
            data = await websocket.receive_json()
            answer = data['answer']

            if len(prompts) == 0:
                print('START')
                print('recv {}'.format(answer))
                msg = sendToChatGPT(prompts)
                print('send {}'.format(msg))
                prompts.append({'role': 'assistant', 'content': msg})
                await websocket.send_json({'question': msg})
            else:
                print('recv {}'.format(answer))
                prompts.append({'role': 'user', 'content': data['answer']})

                msg = sendToChatGPT(prompts)
                print('send {}'.format(msg))
                prompts.append({'role': 'assistant', 'content': msg})
                await websocket.send_json({'question': msg})
    except WebSocketDisconnect:
        # TODO: handle disconnect
        pass