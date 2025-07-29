# AI Elephant Multi-Agent System with LLM Integration
# Enhanced version with local LLM for each agent and RL preparation

import rospy
import cv2
import numpy as np
import threading
import time
import json
import requests
from queue import Queue
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import speech_recognition as sr
import pyttsx3
from transformers import pipeline
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import serial
import subprocess
import pickle
import os
from collections import deque

# ROS imports
from std_msgs.msg import String, Int32, Bool, Float32
from sensor_msgs.msg import Image, CompressedImage
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

# ==================== GLOBAL CONFIGURATION ====================

LLM_MODEL = "llama3.2:3b"  # Default local LLM model
LLM_CACHE_DIR = "llm_cache"  # Directory for storing LLM context
RL_DATA_DIR = "rl_data"  # Directory for reinforcement learning data

# Create directories if they don't exist
os.makedirs(LLM_CACHE_DIR, exist_ok=True)
os.makedirs(RL_DATA_DIR, exist_ok=True)

# ==================== UTILITY FUNCTIONS ====================

def get_llm_response(prompt: str, agent_name: str, context: List[str] = None) -> str:
    """Get response from local LLM with context management"""
    try:
        # Build full prompt with context
        full_prompt = "\n".join(context or []) + "\n" + prompt if context else prompt
        
        # Check cache first
        cache_key = hash(full_prompt)
        cache_file = os.path.join(LLM_CACHE_DIR, f"{agent_name}_{cache_key}.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        # Run LLM
        response = subprocess.run(
            ['ollama', 'run', LLM_MODEL, full_prompt],
            capture_output=True, text=True, timeout=10
        ).stdout.strip()
        
        # Cache the response
        with open(cache_file, 'wb') as f:
            pickle.dump(response, f)
            
        return response
        
    except Exception as e:
        rospy.logwarn(f"LLM query failed: {e}")
        return ""

def save_rl_data(agent_name: str, state: Dict, action: str, reward: float, next_state: Dict):
    """Save reinforcement learning data for later training"""
    try:
        timestamp = int(time.time())
        data = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'timestamp': timestamp
        }
        
        filename = os.path.join(RL_DATA_DIR, f"{agent_name}_{timestamp}.pkl")
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
            
    except Exception as e:
        rospy.logwarn(f"Failed to save RL data: {e}")

# ==================== DATA STRUCTURES ====================

@dataclass
class MahoutInfo:
    rfid_id: Optional[int] = None
    face_recognized: bool = False
    voice_recognized: bool = False
    distance: float = 0.0
    confidence: float = 0.0

@dataclass
class Command:
    text: str
    confidence: float
    timestamp: float
    source: str  # 'voice', 'gesture', 'touch'

@dataclass
class SensorData:
    touch_sensors: Dict[str, float] = None
    proximity: Dict[str, float] = None
    camera_feed: np.ndarray = None

@dataclass
class AgentContext:
    short_term_memory: deque
    long_term_memory: Dict
    last_actions: List[str]

# ==================== SUPERVISING AGENT ====================

class SupervisingAgent:
    """Central coordinator agent managing all other agents with enhanced LLM capabilities"""
    
    def __init__(self):
        rospy.init_node('supervising_agent', anonymous=True)
        
        # Agent communication
        self.command_queue = Queue()
        self.mahout_info = MahoutInfo()
        self.current_state = "idle"
        self.last_command_time = time.time()
        
        # Context management
        self.context = AgentContext(
            short_term_memory=deque(maxlen=20),
            long_term_memory={},
            last_actions=[]
        )
        
        # ROS Publishers
        self.movement_pub = rospy.Publisher('/elephant/movement_cmd', String, queue_size=10)
        self.gesture_pub = rospy.Publisher('/elephant/gesture_cmd', String, queue_size=10)
        self.status_pub = rospy.Publisher('/elephant/status', String, queue_size=10)
        self.llm_pub = rospy.Publisher('/elephant/llm_debug', String, queue_size=10)
        
        # ROS Subscribers
        rospy.Subscriber('/elephant/mahout_detected', String, self.mahout_callback)
        rospy.Subscriber('/elephant/command_received', String, self.command_callback)
        rospy.Subscriber('/elephant/obstacle_detected', String, self.obstacle_callback)
        rospy.Subscriber('/elephant/touch_event', String, self.touch_callback)
        
        # Initialize local LLM
        self.setup_local_llm()
        
        # Command mappings with enhanced capabilities
        self.command_map = {
            'move forward': 'forward',
            'move backward': 'backward',
            'turn left': 'turn_left',
            'turn right': 'turn_right',
            'stop': 'stop',
            'trunk up': 'trunk_raise',
            'trunk down': 'trunk_lower',
            'flap ears': 'ear_flap',
            'blink': 'eye_blink',
            'wag tail': 'tail_wag',
            'look left': 'look_left',
            'look right': 'look_right',
            'dance': 'perform_dance',
            'greet': 'perform_greeting',
            'sleep': 'go_to_sleep'
        }
        
        rospy.loginfo("Enhanced Supervising Agent initialized")
    
    def setup_local_llm(self):
        """Initialize local LLM for command interpretation"""
        try:
            # Check if Ollama is running
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if LLM_MODEL not in result.stdout:
                rospy.logwarn(f"Installing local LLM model {LLM_MODEL}...")
                subprocess.run(['ollama', 'pull', LLM_MODEL])
            
            self.llm_available = True
            rospy.loginfo(f"Local LLM {LLM_MODEL} initialized successfully")
            
            # Load context if available
            context_file = os.path.join(LLM_CACHE_DIR, "supervising_context.pkl")
            if os.path.exists(context_file):
                with open(context_file, 'rb') as f:
                    self.context = pickle.load(f)
                    
        except Exception as e:
            rospy.logwarn(f"Local LLM not available: {e}")
            self.llm_available = False
    
    def save_context(self):
        """Save the agent's context to disk"""
        try:
            context_file = os.path.join(LLM_CACHE_DIR, "supervising_context.pkl")
            with open(context_file, 'wb') as f:
                pickle.dump(self.context, f)
        except Exception as e:
            rospy.logwarn(f"Failed to save context: {e}")
    
    def interpret_command(self, command_text: str) -> str:
        """Enhanced command interpretation with LLM context"""
        if not command_text.strip():
            return "unknown"
        
        # First try direct mapping
        command_lower = command_text.lower().strip()
        if command_lower in self.command_map:
            return self.command_map[command_lower]
        
        # Use LLM for interpretation with context
        if self.llm_available:
            try:
                # Build context prompt
                context_lines = list(self.context.short_term_memory)[-5:]  # Last 5 context items
                context_prompt = "\n".join(context_lines)
                
                prompt = f"""
                Context (most recent first):
                {context_prompt}
                
                Interpret this command for a robotic elephant and return only the action name:
                Command: "{command_text}"
                
                Available actions: {', '.join(self.command_map.values())}
                
                Consider the current state: {self.current_state}
                Mahout presence: {bool(self.mahout_info.rfid_id or self.mahout_info.face_recognized)}
                
                Return only the action name or 'unknown' if unclear:
                """
                
                action = get_llm_response(prompt, "supervising_agent")
                
                # Debug publish LLM interaction
                self.llm_pub.publish(json.dumps({
                    'input': command_text,
                    'output': action,
                    'timestamp': time.time()
                }))
                
                # Update context
                self.context.short_term_memory.append(f"Command: {command_text} -> Action: {action}")
                
                if action in self.command_map.values():
                    return action
                    
            except Exception as e:
                rospy.logwarn(f"LLM interpretation failed: {e}")
        
        return "unknown"
    
    def execute_complex_action(self, action: str):
        """Handle complex actions that require multi-step execution"""
        if action == "perform_dance":
            rospy.loginfo("Performing dance routine")
            # Sequence of movements and gestures
            self.movement_pub.publish("turn_left")
            time.sleep(1)
            self.movement_pub.publish("turn_right")
            time.sleep(1)
            self.gesture_pub.publish("ear_flap")
            self.gesture_pub.publish("tail_wag")
            time.sleep(2)
            self.movement_pub.publish("stop")
            
        elif action == "perform_greeting":
            rospy.loginfo("Performing greeting routine")
            self.gesture_pub.publish("trunk_raise")
            self.gesture_pub.publish("eye_blink")
            time.sleep(1)
            self.gesture_pub.publish("trunk_lower")
            
        elif action == "go_to_sleep":
            rospy.loginfo("Going to sleep mode")
            self.movement_pub.publish("stop")
            self.gesture_pub.publish("trunk_lower")
            time.sleep(1)
            self.gesture_pub.publish("eye_blink")
            self.current_state = "sleeping"
    
    def execute_action(self, action: str):
        """Enhanced action execution with RL data collection"""
        rospy.loginfo(f"Executing action: {action}")
        
        # Capture state before action
        prev_state = {
            'current_state': self.current_state,
            'mahout_present': bool(self.mahout_info.rfid_id or self.mahout_info.face_recognized),
            'last_actions': self.context.last_actions[-3:] if self.context.last_actions else []
        }
        
        movement_actions = ['forward', 'backward', 'turn_left', 'turn_right', 'stop']
        gesture_actions = ['trunk_raise', 'trunk_lower', 'ear_flap', 'eye_blink', 
                          'tail_wag', 'look_left', 'look_right']
        complex_actions = ['perform_dance', 'perform_greeting', 'go_to_sleep']
        
        if action in movement_actions:
            self.movement_pub.publish(action)
            reward = 0.5  # Base reward for movement
        elif action in gesture_actions:
            self.gesture_pub.publish(action)
            reward = 0.3  # Base reward for gestures
        elif action in complex_actions:
            self.execute_complex_action(action)
            reward = 1.0  # Higher reward for complex actions
        else:
            rospy.logwarn(f"Unknown action: {action}")
            reward = -0.1  # Negative reward for unknown actions
        
        # Capture state after action
        next_state = {
            'current_state': self.current_state,
            'mahout_present': bool(self.mahout_info.rfid_id or self.mahout_info.face_recognized),
            'last_actions': (self.context.last_actions + [action])[-3:]
        }
        
        # Save RL data
        save_rl_data("supervising_agent", prev_state, action, reward, next_state)
        
        # Update context
        self.context.last_actions.append(action)
        if len(self.context.last_actions) > 10:
            self.context.last_actions.pop(0)
    
    # ... (rest of the SupervisingAgent methods remain the same)
    # Add context saving to the run method
    def run(self):
        """Main supervision loop with context saving"""
        try:
            rate = rospy.Rate(10)
            while not rospy.is_shutdown():
                # Existing loop code...
                rate.sleep()
        finally:
            self.save_context()

# ==================== VISION AGENT ====================

class VisionAgent:
    """Enhanced Vision Agent with LLM for scene understanding"""
    
    def __init__(self):
        rospy.init_node('vision_agent', anonymous=True)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # ROS setup
        self.bridge = CvBridge()
        self.mahout_pub = rospy.Publisher('/elephant/mahout_detected', String, queue_size=10)
        self.obstacle_pub = rospy.Publisher('/elephant/obstacle_detected', String, queue_size=10)
        self.scene_pub = rospy.Publisher('/elephant/scene_description', String, queue_size=10)
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Context management
        self.context = AgentContext(
            short_term_memory=deque(maxlen=20),
            long_term_memory={},
            last_actions=[]
        )
        
        # LLM setup
        self.setup_local_llm()
        
        # Scene understanding parameters
        self.last_scene_analysis = 0
        self.scene_analysis_interval = 5  # seconds
        
        rospy.loginfo("Enhanced Vision Agent initialized")
    
    def setup_local_llm(self):
        """Initialize local LLM for scene understanding"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if LLM_MODEL not in result.stdout:
                rospy.logwarn(f"Installing local LLM model {LLM_MODEL}...")
                subprocess.run(['ollama', 'pull', LLM_MODEL])
            
            self.llm_available = True
            rospy.loginfo(f"Local LLM {LLM_MODEL} initialized successfully")
        except Exception as e:
            rospy.logwarn(f"Local LLM not available: {e}")
            self.llm_available = False
    
    def analyze_scene(self, frame):
        """Use LLM to analyze the scene and provide context"""
        if not self.llm_available or time.time() - self.last_scene_analysis < self.scene_analysis_interval:
            return
        
        try:
            # Convert frame to base64 for LLM input
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            prompt = f"""
            Analyze this scene from a robotic elephant's perspective:
            Image: {frame_base64}
            
            Describe:
            1. The environment (indoor/outdoor, lighting conditions)
            2. Notable objects or people
            3. Any potential obstacles or interesting elements
            4. Emotional tone of the scene
            
            Return your analysis in JSON format with these keys:
            environment, objects, obstacles, emotional_tone
            """
            
            response = get_llm_response(prompt, "vision_agent")
            
            try:
                analysis = json.loads(response)
                self.scene_pub.publish(json.dumps(analysis))
                self.last_scene_analysis = time.time()
                
                # Update context
                self.context.short_term_memory.append(f"Scene analysis: {analysis.get('environment', '')}")
                
            except json.JSONDecodeError:
                rospy.logwarn("Failed to parse LLM scene analysis")
                
        except Exception as e:
            rospy.logwarn(f"Scene analysis failed: {e}")
    
    def detect_faces(self, frame):
        """Enhanced face detection with LLM context"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0 and self.llm_available:
            # Use LLM to analyze facial expressions
            try:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                prompt = f"""
                Analyze the facial expressions in this image:
                Image: {frame_base64}
                
                Return a JSON with:
                - dominant_emotion
                - confidence
                - description
                """
                
                response = get_llm_response(prompt, "vision_agent")
                emotion_data = json.loads(response)
                
                # Update context
                self.context.short_term_memory.append(
                    f"Face emotion: {emotion_data.get('dominant_emotion', 'unknown')}"
                )
                
            except Exception as e:
                rospy.logwarn(f"Face emotion analysis failed: {e}")
        
        return faces
    
    def run(self):
        """Enhanced vision processing loop with scene analysis"""
        rate = rospy.Rate(30)
        
        while not rospy.is_shutdown():
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Scene analysis
            self.analyze_scene(frame)
            
            # Existing vision processing...
            rate.sleep()

# ==================== AUDIO AGENT ====================

class AudioAgent:
    """Enhanced Audio Agent with LLM for conversation and context"""
    
    def __init__(self):
        rospy.init_node('audio_agent', anonymous=True)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # ROS Publishers
        self.command_pub = rospy.Publisher('/elephant/command_received', String, queue_size=10)
        self.audio_status_pub = rospy.Publisher('/elephant/audio_status', String, queue_size=10)
        self.conversation_pub = rospy.Publisher('/elephant/conversation', String, queue_size=10)
        
        # Context management
        self.context = AgentContext(
            short_term_memory=deque(maxlen=20),
            long_term_memory={},
            last_actions=[]
        )
        
        # LLM setup
        self.setup_local_llm()
        self.conversation_mode = False
        
        rospy.loginfo("Enhanced Audio Agent initialized")
    
    def setup_local_llm(self):
        """Initialize local LLM for conversation"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if LLM_MODEL not in result.stdout:
                rospy.logwarn(f"Installing local LLM model {LLM_MODEL}...")
                subprocess.run(['ollama', 'pull', LLM_MODEL])
            
            self.llm_available = True
            rospy.loginfo(f"Local LLM {LLM_MODEL} initialized successfully")
        except Exception as e:
            rospy.logwarn(f"Local LLM not available: {e}")
            self.llm_available = False
    
    def handle_conversation(self, text: str):
        """Use LLM to generate conversational responses"""
        if not self.llm_available:
            return
        
        try:
            # Build context prompt
            context = "\n".join(self.context.short_term_memory)
            
            prompt = f"""
            You are a friendly robotic elephant. Respond to the human conversation naturally.
            
            Previous context:
            {context}
            
            Human says: "{text}"
            
            Your response (keep it short and friendly):
            """
            
            response = get_llm_response(prompt, "audio_agent")
            
            # Publish conversation
            self.conversation_pub.publish(json.dumps({
                'human': text,
                'elephant': response,
                'timestamp': time.time()
            }))
            
            # Speak the response
            self.speak_response(response)
            
            # Update context
            self.context.short_term_memory.append(f"Human: {text}")
            self.context.short_term_memory.append(f"Elephant: {response}")
            
        except Exception as e:
            rospy.logwarn(f"Conversation failed: {e}")
    
    def listen_for_commands(self):
        """Enhanced listening with conversation mode"""
        while not rospy.is_shutdown():
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    
                    # Check if this is a command or conversation
                    if self.conversation_mode or any(word in text.lower() for word in ['hello', 'hi', 'how are you']):
                        self.handle_conversation(text)
                    else:
                        command_data = {
                            'text': text,
                            'confidence': 0.8,
                            'timestamp': time.time(),
                            'source': 'voice'
                        }
                        self.command_pub.publish(json.dumps(command_data))
                    
                except sr.UnknownValueError:
                    pass
                    
            except Exception as e:
                rospy.logwarn(f"Audio processing error: {e}")
                time.sleep(0.1)

# ==================== MOVEMENT AGENT ====================

class MovementAgent:
    """Enhanced Movement Agent with LLM for adaptive movement strategies"""
    
    def __init__(self):
        rospy.init_node('movement_agent', anonymous=True)
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Servo setup...
        
        # Context management
        self.context = AgentContext(
            short_term_memory=deque(maxlen=20),
            long_term_memory={},
            last_actions=[]
        )
        
        # LLM setup
        self.setup_local_llm()
        
        # Adaptive movement parameters
        self.movement_strategies = {}
        
        rospy.loginfo("Enhanced Movement Agent initialized")
    
    def setup_local_llm(self):
        """Initialize local LLM for movement optimization"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if LLM_MODEL not in result.stdout:
                rospy.logwarn(f"Installing local LLM model {LLM_MODEL}...")
                subprocess.run(['ollama', 'pull', LLM_MODEL])
            
            self.llm_available = True
            rospy.loginfo(f"Local LLM {LLM_MODEL} initialized successfully")
        except Exception as e:
            rospy.logwarn(f"Local LLM not available: {e}")
            self.llm_available = False
    
    def optimize_movement(self, command: str, environment: Dict):
        """Use LLM to optimize movement based on environment"""
        if not self.llm_available:
            return command
        
        try:
            prompt = f"""
            Suggest optimal movement parameters for a robotic elephant based on:
            - Command: {command}
            - Environment: {environment}
            
            Consider:
            - Speed adjustments
            - Step patterns
            - Obstacle navigation
            
            Return JSON with:
            - action (must match original command)
            - speed_factor (0.1-1.0)
            - step_pattern (description)
            """
            
            response = get_llm_response(prompt, "movement_agent")
            strategy = json.loads(response)
            
            # Update context
            self.context.short_term_memory.append(
                f"Movement strategy: {command} -> {strategy.get('step_pattern', 'default')}"
            )
            
            return strategy
            
        except Exception as e:
            rospy.logwarn(f"Movement optimization failed: {e}")
            return {'action': command, 'speed_factor': 1.0, 'step_pattern': 'default'}
    
    def execute_optimized_movement(self, strategy: Dict):
        """Execute movement with optimized parameters"""
        command = strategy['action']
        speed_factor = strategy.get('speed_factor', 1.0)
        
        # Adjust movement based on optimization
        if command == "forward":
            self.adaptive_move_forward(speed_factor)
        # ... other commands

# ==================== GESTURE AGENT ====================

class GestureAgent:
    """Enhanced Gesture Agent with LLM for expressive behavior"""
    
    def __init__(self):
        rospy.init_node('gesture_agent', anonymous=True)
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Servo setup...
        
        # Context management
        self.context = AgentContext(
            short_term_memory=deque(maxlen=20),
            long_term_memory={},
            last_actions=[]
        )
        
        # LLM setup
        self.setup_local_llm()
        
        # Emotional state
        self.emotional_state = "neutral"
        
        rospy.loginfo("Enhanced Gesture Agent initialized")
    
    def setup_local_llm(self):
        """Initialize local LLM for expressive gestures"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if LLM_MODEL not in result.stdout:
                rospy.logwarn(f"Installing local LLM model {LLM_MODEL}...")
                subprocess.run(['ollama', 'pull', LLM_MODEL])
            
            self.llm_available = True
            rospy.loginfo(f"Local LLM {LLM_MODEL} initialized successfully")
        except Exception as e:
            rospy.logwarn(f"Local LLM not available: {e}")
            self.llm_available = False
    
    def adapt_gesture_to_emotion(self, gesture: str, emotion: str):
        """Use LLM to adapt gestures based on emotional context"""
        if not self.llm_available:
            return gesture
        
        try:
            prompt = f"""
            Adjust this robotic elephant gesture for the current emotional context:
            - Base gesture: {gesture}
            - Current emotion: {emotion}
            
            Suggest modifications to:
            - Speed of movement
            - Amplitude
            - Repetition
            
            Return JSON with:
            - gesture (name)
            - speed_factor (0.1-2.0)
            - amplitude_factor (0.1-2.0)
            - repeat_count (1-5)
            """
            
            response = get_llm_response(prompt, "gesture_agent")
            adapted_gesture = json.loads(response)
            
            # Update context
            self.context.short_term_memory.append(
                f"Adapted {gesture} for {emotion}: {adapted_gesture}"
            )
            
            return adapted_gesture
            
        except Exception as e:
            rospy.logwarn(f"Gesture adaptation failed: {e}")
            return {
                'gesture': gesture,
                'speed_factor': 1.0,
                'amplitude_factor': 1.0,
                'repeat_count': 1
            }

# ==================== TOUCH AGENT ====================

class TouchAgent:
    """Enhanced Touch Agent with LLM for adaptive responses"""
    
    def __init__(self):
        rospy.init_node('touch_agent', anonymous=True)
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Touch sensor setup...
        
        # Context management
        self.context = AgentContext(
            short_term_memory=deque(maxlen=20),
            long_term_memory={},
            last_actions=[]
        )
        
        # LLM setup
        self.setup_local_llm()
        
        # Touch response patterns
        self.response_patterns = {}
        
        rospy.loginfo("Enhanced Touch Agent initialized")
    
    def setup_local_llm(self):
        """Initialize local LLM for touch interpretation"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if LLM_MODEL not in result.stdout:
                rospy.logwarn(f"Installing local LLM model {LLM_MODEL}...")
                subprocess.run(['ollama', 'pull', LLM_MODEL])
            
            self.llm_available = True
            rospy.loginfo(f"Local LLM {LLM_MODEL} initialized successfully")
        except Exception as e:
            rospy.logwarn(f"Local LLM not available: {e}")
            self.llm_available = False
    
    def interpret_touch_pattern(self, touch_data: Dict):
        """Use LLM to interpret complex touch patterns"""
        if not self.llm_available:
            return "basic_response"
        
        try:
            prompt = f"""
            Interpret this touch pattern for a robotic elephant:
            Location: {touch_data['location']}
            Duration: {touch_data['duration']}
            Intensity: {touch_data['intensity']}
            Recent touches: {list(self.context.short_term_memory)[-3:]}
            
            Suggest an appropriate response from:
            - affectionate (gentle trunk movement)
            - playful (ear flapping and tail wagging)
            - defensive (move back slightly)
            - curious (turn toward touch)
            - none (no response)
            
            Return only the response type:
            """
            
            response = get_llm_response(prompt, "touch_agent").strip().lower()
            
            # Update context
            self.context.short_term_memory.append(
                f"Touch at {touch_data['location']} -> {response}"
            )
            
            return response
            
        except Exception as e:
            rospy.logwarn(f"Touch interpretation failed: {e}")
            return "basic_response"

# ==================== RFID AGENT ====================

class RFIDAgent:
    """Enhanced RFID Agent with LLM for mahout interaction"""
    
    def __init__(self):
        rospy.init_node('rfid_agent', anonymous=True)
        
        # Initialize RFID reader...
        
        # Context management
        self.context = AgentContext(
            short_term_memory=deque(maxlen=20),
            long_term_memory={},
            last_actions=[]
        )
        
        # LLM setup
        self.setup_local_llm()
        
        # Mahout interaction history
        self.interaction_history = {}
        
        rospy.loginfo("Enhanced RFID Agent initialized")
    
    def setup_local_llm(self):
        """Initialize local LLM for mahout interaction"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if LLM_MODEL not in result.stdout:
                rospy.logwarn(f"Installing local LLM model {LLM_MODEL}...")
                subprocess.run(['ollama', 'pull', LLM_MODEL])
            
            self.llm_available = True
            rospy.loginfo(f"Local LLM {LLM_MODEL} initialized successfully")
        except Exception as e:
            rospy.logwarn(f"Local LLM not available: {e}")
            self.llm_available = False
    
    def personalize_interaction(self, mahout_id: int):
        """Use LLM to personalize interaction based on mahout history"""
        if not self.llm_available:
            return "standard_greeting"
        
        try:
            history = self.interaction_history.get(mahout_id, [])
            
            prompt = f"""
            Generate a personalized interaction for mahout {mahout_id} based on:
            Previous interactions: {history[-3:] if history else 'None'}
            
            Suggest:
            - greeting_style (formal, playful, affectionate)
            - preferred_gestures (list)
            - interaction_length (short, medium, long)
            
            Return JSON with these keys:
            """
            
            response = get_llm_response(prompt, "rfid_agent")
            personalization = json.loads(response)
            
            # Update context
            self.context.short_term_memory.append(
                f"Personalized interaction for {mahout_id}: {personalization}"
            )
            
            return personalization
            
        except Exception as e:
            rospy.logwarn(f"Personalization failed: {e}")
            return {
                'greeting_style': 'standard',
                'preferred_gestures': ['ear_flap'],
                'interaction_length': 'short'
            }

# ==================== MAIN LAUNCHER ====================

def main():
    """Main function to launch enhanced agents"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ai_elephant_agents.py <agent_name>")
        print("Available agents:")
        print("  - supervising")
        print("  - vision")
        print("  - audio")
        print("  - movement")
        print("  - gesture")
        print("  - touch")
        print("  - rfid")
        return
    
    agent_name = sys.argv[1].lower()
    
    try:
        if agent_name == "supervising":
            agent = SupervisingAgent()
        elif agent_name == "vision":
            agent = VisionAgent()
        elif agent_name == "audio":
            agent = AudioAgent()
        elif agent_name == "movement":
            agent = MovementAgent()
        elif agent_name == "gesture":
            agent = GestureAgent()
        elif agent_name == "touch":
            agent = TouchAgent()
        elif agent_name == "rfid":
            agent = RFIDAgent()
        else:
            print(f"Unknown agent: {agent_name}")
            return
        
        agent.run()
        
    except KeyboardInterrupt:
        rospy.loginfo(f"{agent_name.capitalize()} Agent shutting down")
    except Exception as e:
        rospy.logerr(f"Error running {agent_name} agent: {e}")

if __name__ == '__main__':
    main()