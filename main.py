from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from pathlib import Path
from app.config import settings
from app.fastcore.user.auth import authentication, get_user_from_token
from app.fastcore.common.constant import MSG
from app.fastcore.common.middlewares import RateLimitMiddleware
from app.modules.customer.routes import router as customer_router


app = FastAPI()

IMAGE_DIRECTORY = settings.IMAGE_DIRECTORY
IMAGE_UPLOAD_DIR = Path(IMAGE_DIRECTORY)
IMAGE_UPLOAD_DIR.mkdir(exist_ok=True)


# Thêm middleware Ratelimiting chính thức
app.add_middleware(
    RateLimitMiddleware,
    rate=settings.RATELIMITING,
    identifier=lambda req: get_user_from_token(req),
)

# Thêm CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Nếu bạn đặt detail là dict, sẽ lấy trực tiếp luôn
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    # Nếu detail là string, chuyển thành message
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": str(exc.detail)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "422",
            "message": "Dữ liệu đầu vào không hợp lệ",
            # "data": exc.errors()
        },
    )

app.include_router(customer_router, prefix='/customer')

# In tất cả route sau khi app khởi tạo
@app.get("/routes")
def get_all_routes():
    return [
        {
            "path": route.path,
            "methods": list(route.methods),
            "name": route.name
        }
        for route in app.routes
        if hasattr(route, "methods") and route.name != "openapi"
    ]

@app.get("/")
def public_home():
    return RedirectResponse('https://tmsc-vn.com/')
