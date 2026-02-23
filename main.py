import fastapi
import fastapi_chameleon
from fastapi_chameleon import template
from starlette.staticfiles import StaticFiles
import uvicorn
import data_service

app = fastapi.FastAPI()


def setup_chameleon():
    fastapi_chameleon.global_init('templates')


@app.on_event("startup")
def startup_event():
    setup_chameleon()


app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/')
@template(template_file='home/index.pt')
def index():
    return {
        'rooms': data_service.get_rooms()
    }


@app.post('/set_temp/{room_id}')
def set_temp(room_id: str, setpoint: float = fastapi.Form(...)):
    data_service.update_room_setpoint(room_id, setpoint)
    return fastapi.responses.RedirectResponse(url='/', status_code=303)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
