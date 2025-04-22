from fastapi import FastAPI
from pydantic import BaseModel

class Requests(BaseModel):
    message: str
    chatId: str | None

app = FastAPI()



@app.get("/")
def read_root():
    return {"message": "Ahmet'in API'si yayında!"}

@app.post("/chat")
async def chatBot(request: Requests):
    body = await request.json()
    getMessage = body.get("message", "")
    print(getMessage)
    response = {
        "message": "Bu bir yanıt mesajıdır: " + getMessage,
    }

    return response