
from starlette.requests import Request
from starlette.responses import Response
from typing import Optional
from app.config.load_environment import get_settings
# from services import user_service
from app.viewmodels.shared.view_model_base import ViewModelBase


class AboutViewModel(ViewModelBase):

    def __init__(self, request: Request, response: Optional[Response] = None):
        super().__init__(request, response)
        self.user = None
        self.is_logged_in = True
        self.about_image_path = ''

    async def load(self):
        self.about_image_path = get_settings().ABOUT_IMAGE_FILE_NAME
        self.user = 'Knut'
