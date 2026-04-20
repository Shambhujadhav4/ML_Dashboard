from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, predict, preprocess, train, upload, visualize
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(upload.router, prefix=settings.api_prefix)
app.include_router(preprocess.router, prefix=settings.api_prefix)
app.include_router(train.router, prefix=settings.api_prefix)
app.include_router(predict.router, prefix=settings.api_prefix)
app.include_router(visualize.router, prefix=settings.api_prefix)
