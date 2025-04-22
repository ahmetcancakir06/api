from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Ahmet'in API'si yayında!"}

@app.post("/chat")
async def chatBot(request: Requests):
    body = await Request.json()
    getMessage = body.get("message", "")
    print(getMessage)
    response = {
        "message": "Bu bir yanıt mesajıdır: " + getMessage,
    }
    return response