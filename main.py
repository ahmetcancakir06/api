from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Request modeli
class Requests(BaseModel):
    message: str
    chatId: str | None = None  # default None

# CORS middleware
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

# FastAPI instance
app = FastAPI(middleware=middleware)

@app.get("/")
def read_root():
    return {"message": "Ahmet'in API'si yayında!"}

@app.post("/chat")
async def chatBot(request: Requests):
    getMessage = request.message
    chatId = request.chatId
    print(f"Mesaj: {getMessage}, ChatID: {chatId}")

    return {
        "message": f"Cevap: {getMessage}",
        "chatId": chatId
    }
