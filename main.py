from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uvicorn
import os

app = FastAPI(title="Bean Haven AI Assistant")

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),   # 直接写死Key
    base_url="https://api.deepseek.com",
    temperature=0.7
)

chat_history = []

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Bean Haven AI Assistant</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; background: #f5e8d3; color: #3c2f2f; }
            h1 { color: #8d5524; text-align: center; }
            #chat { height: 500px; overflow-y: scroll; border: 2px solid #8d5524; padding: 15px; background: white; border-radius: 15px; }
            .user { text-align: right; color: #8d5524; margin: 10px 0; }
            .ai { text-align: left; color: #3c2f2f; margin: 10px 0; }
            input { width: 75%; padding: 15px; font-size: 16px; border-radius: 10px; border: 2px solid #8d5524; }
            button { padding: 15px 30px; background: #8d5524; color: white; border: none; border-radius: 10px; font-size: 16px; }
            .coffee { font-size: 60px; text-align: center; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="coffee">☕</div>
        <h1>Bean Haven Coffee Shop</h1>
        <h2 style="text-align:center;color:#8d5524;">Your 24/7 AI Store Assistant is Online!</h2>
        <div id="chat"></div>
        <input type="text" id="userInput" placeholder="Type your message... (e.g. Hi, can I order a latte?)">
        <button onclick="sendMessage()">Send</button>

        <script>
            async function sendMessage() {
                const input = document.getElementById("userInput");
                const msg = input.value.trim();
                if (!msg) return;
                
                const chat = document.getElementById("chat");
                chat.innerHTML += `<p class="user">You: ${msg}</p>`;
                input.value = "";
                
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                
                chat.innerHTML += `<p class="ai">Bean: ${data.reply}</p>`;
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: ChatRequest):
    global chat_history
    
    if len(chat_history) == 0:
        system_prompt = "You are Bean, a friendly and professional AI assistant for Bean Haven Coffee Shop. Help with ordering, reservations, menu questions, and order follow-ups. Always reply in natural, friendly English. Remember customer names and preferences if mentioned."
        chat_history.append(SystemMessage(content=system_prompt))
    
    chat_history.append(HumanMessage(content=request.message))
    response = llm.invoke(chat_history)
    chat_history.append(AIMessage(content=response.content))
    
    return {"reply": response.content}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
