from fastapi import FastAPI
from botbuilder.core import TurnContext, ActivityHandler, ConversationState, UserState, BotFrameworkAdapter
from botbuilder.schema import Activity, ActivityTypes

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI bot!"}

@app.post("/api/messages")
async def bot_messages(request: dict):
    # Implement your bot's logic here
    return {"message": "Hello from bot!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)