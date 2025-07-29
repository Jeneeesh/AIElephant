from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from typing import List, Dict, Optional
import logging
from datetime import datetime

from app.services.llm_supervisor import LLMSupervisor
from app.services.language_understanding import LanguageUnderstanding
from app.services.voice_processor import VoiceProcessor
from app.services.hardware_controller import HardwareController
from app.models.command import Command, CommandFeedback
from app.database.connection import get_db

# Initialize FastAPI app
app = FastAPI(title="AI Elephant Control API", version="1.0.0")

# CORS middleware for web and mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_supervisor = LLMSupervisor()
language_understanding = LanguageUnderstanding()
voice_processor = VoiceProcessor()
hardware_controller = HardwareController()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Predefined commands based on your BRD
COMMANDS = {
    1: {"action": "Turn Left", "malayalam": "ഇടത്താനെ", "hindi": "बाएं", "gujarati": "ડાબે"},
    2: {"action": "Turn Right", "malayalam": "വലത്താനെ", "hindi": "दाएं", "gujarati": "જમણે"},
    3: {"action": "Walk Forward", "malayalam": "നടയാനെ", "hindi": "चल", "gujarati": "ચાલ"},
    4: {"action": "Walk Backward", "malayalam": "സെറ്റാനെ", "hindi": "पीछे", "gujarati": "પાછળ"},
    5: {"action": "Stop", "malayalam": "നില്ലാനെ", "hindi": "ठहर", "gujarati": "થોભ"},
    # Add all 23 commands from your table
}

@app.get("/")
async def root():
    return {"message": "AI Elephant Control API is running"}

@app.get("/commands")
async def get_commands():
    """Get all available commands"""
    return {"commands": COMMANDS}

@app.post("/voice/process")
async def process_voice_command(audio_data: dict):
    """Process voice command through the AI pipeline"""
    try:
        # Step 1: Convert speech to text using Whisper
        text_input = await voice_processor.speech_to_text(audio_data["audio"])
        
        # Step 2: Pass to LLM Supervisor
        supervisor_response = await llm_supervisor.classify_input(text_input)
        
        if supervisor_response["type"] != "command":
            return {"error": "Input not recognized as a command"}
        
        # Step 3: Language Understanding sub-agent
        command_result = await language_understanding.understand_command(
            text_input, 
            supervisor_response["language"]
        )
        
        if not command_result["success"]:
            return {"error": "Command not recognized", "text": text_input}
        
        # Step 4: Execute command
        execution_result = await hardware_controller.execute_command(
            command_result["command_id"]
        )
        
        # Broadcast to connected clients
        await manager.broadcast({
            "type": "command_executed",
            "command": command_result["command_name"],
            "text": text_input,
            "language": supervisor_response["language"],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "recognized_text": text_input,
            "command": command_result["command_name"],
            "language": supervisor_response["language"],
            "execution_status": execution_result["status"]
        }
        
    except Exception as e:
        logging.error(f"Error processing voice command: {str(e)}")
        return {"error": "Internal server error"}

@app.post("/command/manual/{command_id}")
async def execute_manual_command(command_id: int, interval: Optional[int] = None):
    """Execute command manually from the web interface"""
    try:
        if command_id not in COMMANDS:
            raise HTTPException(status_code=404, detail="Command not found")
        
        result = await hardware_controller.execute_command(command_id, interval)
        
        await manager.broadcast({
            "type": "manual_command",
            "command": COMMANDS[command_id]["action"],
            "command_id": command_id,
            "interval": interval,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(feedback_data: dict):
    """Submit user feedback for command recognition"""
    try:
        # Store feedback in database
        db = next(get_db())
        feedback = CommandFeedback(
            voice_sample=feedback_data.get("voice_sample"),
            detected_command=feedback_data.get("detected_command"),
            user_feedback=feedback_data.get("is_correct"),
            language=feedback_data.get("language"),
            timestamp=datetime.now()
        )
        db.add(feedback)
        db.commit()
        
        # Trigger retraining if enough negative feedback
        await language_understanding.process_feedback(feedback_data)
        
        return {"message": "Thank you for your feedback!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/status")
async def get_system_status():
    """Get current system status"""
    return {
        "llm_status": await llm_supervisor.health_check(),
        "hardware_status": await hardware_controller.get_status(),
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)