import fastapi
from fastapi_chameleon import template
from starlette.requests import Request
from starlette.responses import Response

from fastapi.responses import FileResponse
from app.viewmodels.home.about_view_model import AboutViewModel
from app.config.load_environment import resolve_path

router = fastapi.APIRouter()


@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    file_path = resolve_path('app/static/img/favicon.ico')
    if file_path.exists():
        return FileResponse(file_path)
    return fastapi.Response(status_code=404)



@router.get('/', include_in_schema=False)
@template(template_file='home/about.pt')
async def about(request: Request, response: Response):

    vm = AboutViewModel(request, response)
    await vm.load()
    return vm.to_dict()
