import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.app.routers.auth import auth
from api.app.routers.manager import manager
from api.app.routers.sales import sales

app = FastAPI()

app.include_router(auth, prefix="/auth")
app.include_router(manager, prefix="/manager")
app.include_router(sales)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("api.app.main:app", host="0.0.0.0", port=8000, reload=True)