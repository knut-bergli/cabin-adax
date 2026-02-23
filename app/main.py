from contextlib import asynccontextmanager

import fastapi
import fastapi_chameleon
import uvicorn
from fastapi import FastAPI
from fastapi_chameleon import template
from starlette.staticfiles import StaticFiles

from app.services import data_service

from routers import display_panel

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    """

    yield
    # Possible clean up code here

app = FastAPI(lifespan=lifespan)


def setup_chameleon():
    fastapi_chameleon.global_init('templates')


@app.on_event("startup")
def startup_event():
    setup_chameleon()


def configure(dev_mode: bool):
    """
    Configures the application by setting up templates and routes.

    This function initializes the application by configuring templates and
    routes. It accepts a parameter to determine whether the application
    should be configured in development mode.

    Args:
        dev_mode (bool): Indicates whether to configure the application in
                         development mode.
    """
    configure_templates(dev_mode)
    configure_routes()


def configure_templates(dev_mode: bool):
    fastapi_chameleon.global_init('templates', auto_reload=dev_mode)


def configure_routes():
    app.mount('/static', StaticFiles(directory='static'), name='static')

    app.include_router(display_panel.router)


def main():
    # dev_mode = get_settings().DEV_MODE
    dev_mode = True
    configure(dev_mode=dev_mode)
    # If log_config is None, uvicorn might disable existing logging.
    # Use the default or specified config.
    # log_cfg = str(resolve_path('config_files/logging.yaml'))
    # if not Path(log_cfg).exists():
    #     log_cfg = None
    uvicorn.run(app, host='0.0.0.0', port=8080, log_config=log_cfg)



if __name__ == '__main__':
    main()
else:
    pass
    # configure(dev_mode=get_settings().DEV_MODE)

