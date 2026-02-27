import logging
from contextlib import asynccontextmanager
from pathlib import Path

import fastapi_chameleon
import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.config.load_environment import get_settings, resolve_path
from app.models import db_session
from app.routers import heaters_dashboard, admin, home

logger = logging.getLogger(get_settings().LOGGER_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    """
    # :TODO: cabin_adax_storage/db into .env
    db_file = resolve_path('cabin_adax_storage/db') / get_settings().DB_NAME
    if not db_file:
        raise FileNotFoundError("You must specify a database file.")
    await db_session.global_init_database(str(db_file))
    logger.debug(f"Cabin-heater started and database initialized at {db_file}")
    yield
    # Possible clean up code here

app = FastAPI(lifespan=lifespan)


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
    template_folder = Path(__file__).parent / 'templates'
    fastapi_chameleon.global_init(str(template_folder), auto_reload=dev_mode)


def configure_routes():
    static_folder = Path(__file__).parent / 'static'
    app.mount('/static', StaticFiles(directory=str(static_folder)), name='static')

    app.include_router(home.router)
    app.include_router(heaters_dashboard.router)
    app.include_router(admin.router)


def main():
    # dev_mode = get_settings().DEV_MODE
    dev_mode = True
    configure(dev_mode=dev_mode)
    # If log_config is None, uvicorn might disable existing logging.
    # Use the default or specified config.
    # log_cfg = str(resolve_path('config_files/logging.yaml'))
    # if not Path(log_cfg).exists():
    #     log_cfg = None
    uvicorn.run(app, host='0.0.0.0', port=8080) #, log_config=log_cfg)



if __name__ == '__main__':
    main()
else:
    # Configure when module is imported (e.g., by uvicorn)
    configure(dev_mode=True)

