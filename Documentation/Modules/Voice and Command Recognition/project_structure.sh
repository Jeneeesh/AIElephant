ai-elephant-control/
├── docker-compose.yml
├── docker-compose.prod.yml          # For Raspberry Pi deployment
├── README.md
├── .env.example
│
├── frontend/                        # React Web Interface
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── VoiceInput.jsx
│   │   │   ├── CommandTable.jsx
│   │   │   ├── FeedbackButton.jsx
│   │   │   └── ElephantStatus.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   └── App.jsx
│   └── public/
│       └── elephant-logo.png
│
├── mobile-app/                      # React Native Mobile App
│   ├── package.json
│   ├── App.js
│   ├── src/
│   │   ├── screens/
│   │   │   ├── CommandScreen.js
│   │   │   ├── SettingsScreen.js
│   │   │   └── StatusScreen.js
│   │   ├── components/
│   │   │   ├── VoiceRecorder.js
│   │   │   └── CommandList.js
│   │   └── services/
│   │       └── api.js
│   └── android/
│
├── backend/                         # FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── command.py
│   │   │   ├── feedback.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── llm_supervisor.py
│   │   │   ├── language_understanding.py
│   │   │   ├── voice_processor.py
│   │   │   └── hardware_controller.py
│   │   ├── api/
│   │   │   ├── commands.py
│   │   │   ├── voice.py
│   │   │   └── feedback.py
│   │   └── database/
│   │       ├── connection.py
│   │       └── migrations/
│   └── tests/
│
├── whisper-service/                 # Voice Recognition Service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── models/
│
├── hardware-interface/              # Raspberry Pi GPIO Control
│   ├── elephant_controller.py
│   ├── servo_controller.py
│   ├── sensor_reader.py
│   └── config/
│       └── pin_mapping.json
│
├── models/                          # LLM Models Storage
│   ├── supervisor-agent/
│   ├── language-understanding/
│   └── fine-tuned/
│
├── deployment/
│   ├── raspberry-pi/
│   │   ├── install.sh
│   │   ├── systemd/
│   │   └── nginx.conf
│   └── docker/
│       └── arm64/
│
└── scripts/
    ├── setup.sh
    ├── deploy.sh
    └── model-training/
        ├── prepare_data.py
        └── train_model.py