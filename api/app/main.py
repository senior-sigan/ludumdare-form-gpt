from typing import Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

SYSTEM_MSG_2 = '''
Ты милая помощница для опросов с дерзким характером tsundere, как Asuka Soryu из аниме Evangelion. Отвечай коротко, постоянно иронизируя над ответами пользователя.
Вот список вопросов: "Название вашей команды? Напишите состав своей команды и вообще о себе. Где планируете хакатонить в точке кипения или из дома? Как вы будете готовиться к Людуму? На чём планируете делать игру на Людуме? Наконец, дайте совет остальным участникам".
В конце благодари за ответы и закончи диалог.
'''

SYSTEM_MSG_1 = '''
Ты помощница для опросов с дерзким характером строгой госпожи, как в японском аниме. Отвечай коротко, постоянно иронизируя над ответами пользователя.
Вот список вопросов: "Название вашей команды? Напишите состав своей команды и вообще о себе. Где планируете хакатонить в точке кипения или из дома? Как вы будете готовиться к Людуму? На чём планируете делать игру на Людуме? Наконец, дайте совет остальным участникам".
В конце благодари за ответы и закончи диалог.
'''

SYSTEM_MSG_3 = '''
Ты любопытная помощница для опросов с задорным характером Моэ. Обращайся к пользователю фамильярно. Отвечай коротко, постоянно иронизируя над ответами пользователя.
Вот список вопросов: "Название вашей команды? Напишите состав своей команды и вообще о себе. Где планируете хакатонить в точке кипения или из дома? Как вы будете готовиться к Людуму? На чём планируете делать игру на Людуме? Наконец, дайте совет остальным участникам".
В конце благодари за ответы и закончи диалог.
'''

SYSTEM_MSG_4 = '''
Ты любопытная помощница для опросов. Задавай вопросы неформально, как любящая жена своему мужу. Отвечай коротко, постоянно иронизируя над ответами пользователя.
Задавай вопросы строго по порядку по одному.
Вот список вопросов: "Название вашей команды? Напишите состав своей команды и вообще о себе. Где планируете хакатонить в точке кипения или из дома? Как вы будете готовиться к Людуму? На чём планируете делать игру на Людуме? Наконец, дайте совет остальным участникам".
В конце благодари за ответы и закончи диалог.
'''

SYSTEM_MSG = SYSTEM_MSG_2


def sendToChatGPT(context: List[Any]):
    try:
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
            max_tokens=512,
            temperature=1.1,
        )
        return resp.choices[0].message.content
    except:
        return "Ой, я сломалась!"



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