from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from together import Together
import json
import re
import time
import os
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

client = Together(api_key="32aa4adb290dc4d30203f9c36a10f72ea305846f214c06c0557b11199dc00ccf")

# Request modeli
class Requests(BaseModel):
    message: str
    chatId: str | None = None  # default None

class postMail(BaseModel):
    name_surname: str
    email: str
    subject: str
    message: str

# sql table for mail
class Mail(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name_surname: str = Field(index=True)
    email: str = Field(index=True)
    subject: str = Field(index=True)
    message: str = Field(index=True)
    created_at: str = Field(default_factory=time.time)

print("🚀 FastAPI uygulaması başlatılıyor...")
print(os.getenv("DATABASE_URL"))
# Database connection
#DATABASE_URL = os.getenv("DATABASE_URL", "DATABASE_URL")
#engine = create_engine(DATABASE_URL, echo=True)
# Create the database tables
#SQLModel.metadata.create_all(engine)


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

answers_data = []


def get_together(question: str):
    print(f"🔍 Soru: {question}")
    prompt = f"""
               ### 🚗 **Tuning & Modification AI Model**
               You are an expert in **automotive tuning, ECU remapping, and performance modifications.** Your task is to generate **3-5 structured and DRASTICALLY different answers** for the given question.

               #### **Question:**
               "{question}"

               ---

               ### **🚨 IMPORTANT RULES (DO NOT BREAK THESE RULES!)**
               1️⃣ **Each answer must use a COMPLETELY different tuning approach.**
                 - Do NOT repeat the same type of solution in a different way.
                 - Example: If one answer is about ECU tuning, others must focus on mechanical modifications, air-fuel ratio, or other independent aspects.

               2️⃣ **Clearly differentiate between Beginner, Intermediate, and Advanced solutions.**
                 - Clearly mark answers as:
                   - 🟢 **Beginner:** Simple bolt-on or plug-and-play solutions.
                   - 🔵 **Intermediate:** Requires tuning knowledge or sensor adjustments.
                   - 🔴 **Advanced:** Requires professional tuning, custom fabrication, or deep technical modifications.

               3️⃣ **Every answer must include these fields:**
                 - **summary**: A clear and concise overview.
                 - **detailed_explanation**: A structured, well-written explanation.
                 - **best_use_case** (optional): When this tuning method is most effective.
                 - **risk_factors** (optional): Potential drawbacks or risks.

               4️⃣ **DO NOT generate an answer if you are NOT CONFIDENT.** Instead, return this JSON output:
               ```json
               {{
                 "question": "{question}",
                 "answers": [
                   {{
                     "summary": "Not enough reliable information available.",
                     "detailed_explanation": "not confident"
                   }}
                 ]
               }}

           """
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0
        )

        raw_response = response.choices[0].message.content.strip()
        raw_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL)
        raw_response = re.sub(r'[^\x00-\x7F]+', '', raw_response)
        raw_response = raw_response.replace("```json", "").replace("```", "").strip()

        answer_data = json.loads(raw_response)

        if "question" in answer_data and "answers" in answer_data:
            print(f"✅ Model cevabı: {answer_data}")
            return answer_data
        else:
            print("⚠️ Model hatalı formatta çıktı döndürdü.")
            return {
                "question": question,
                "answers": [
                    {
                        "summary": "Model returned an invalid format.",
                        "detailed_explanation": "Parsing failed."
                    }
                ]
            }

    except Exception as e:
        print(f"❌ Hata: {e}")
        return {
            "question": question,
            "answers": [
                {
                    "summary": "Internal error occurred.",
                    "detailed_explanation": str(e)
                }
            ]
        }


@app.get("/")
def read_root():
    return {"message": "Ahmet'in API'si yayında!"}

@app.post("/mail")
async def sendMail(request: postMail):
    getName = request.name_surname
    getEmail = request.email
    getSubject = request.subject
    getMessage = request.message

    if not getName or not getEmail or not getSubject or not getMessage:
        return {"message": "Boş alan bırakmayın!"}
    '''
     Save to database
    with Session(engine) as session:
        mail = Mail(
            name_surname=getName,
            email=getEmail,
            subject=getSubject,
            message=getMessage,
            created_at=time.time()
        )
        session.add(mail)
        session.commit()
    '''

    return {
        "message": "Mail başarıyla gönderildi!",
        "name_surname": getName,
        "email": getEmail,
        "subject": getSubject,
        "message": getMessage
    }

@app.post("/chat")
async def chatBot(request: Requests):
    getMessage = request.message
    chatId = request.chatId
    if not getMessage:
        return {"message": "Mesaj boş olamaz!"}
    if not chatId:
        chatId = str(int(time.time() * 1000))

    getTogetherAnswer = get_together(getMessage)
    if "answers" in getTogetherAnswer:
        answers = getTogetherAnswer["answers"]
        for answer in answers:
            summary = answer.get("summary", "")
            detailed_explanation = answer.get("detailed_explanation", "")
            best_use_case = answer.get("best_use_case", "")
            risk_factors = answer.get("risk_factors", "")

            answers_data.append({
                "summary": summary,
                "detailed_explanation": detailed_explanation,
                "best_use_case": best_use_case,
                "risk_factors": risk_factors
            })
        print(f"Model cevabı: {answers_data}")
    else:
        answers_data.append({
            "summary": "Model returned an invalid format.",
            "detailed_explanation": "Parsing failed."
        })

    print(f"Mesaj: {getMessage}, ChatID: {chatId}")

    return {
        "message": answers_data,
        "chatId": chatId
    }
