import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  Alert,
  PermissionsAndroid,
  Platform
} from 'react-native';
import { Audio } from 'expo-av';
import Icon from 'react-native-vector-icons/MaterialIcons';

const API_BASE_URL = 'http://192.168.1.100:8000'; // Replace with your Pi's IP

const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recording, setRecording] = useState(null);
  const [commands, setCommands] = useState({});
  const [lastCommand, setLastCommand] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  // Command data from your BRD
  const commandData = [
    { id: 1, action: "Turn Left", malayalam: "ഇടത്താനെ", hindi: "बाएं", gujarati: "ડાબે" },
    { id: 2, action: "Turn Right", malayalam: "വലത്താനെ", hindi: "दाएं", gujarati: "જમણે" },
    { id: 3, action: "Walk Forward", malayalam: "നടയാനെ", hindi: "चल", gujarati: "ચાલ" },
    { id: 4, action: "Walk Backward", malayalam: "സെറ്റാനെ", hindi: "पीछे", gujarati: "પાછળ" },
    { id: 5, action: "Stop", malayalam: "നില്ലാനെ", hindi: "ठहर", gujarati: "થોભ" },
    // Add all 23 commands
  ];

  useEffect(() => {
    requestPermissions();
    fetchCommands();
  }, []);

  const requestPermissions = async () => {
    if (Platform.OS === 'android') {
      await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
        {
          title: "Audio Recording Permission",
          message: "This app needs access to microphone to record voice commands",
          buttonNeutral: "Ask Me Later",
          buttonNegative: "Cancel",
          buttonPositive: "OK"
        }
      );
    }
  };

  const fetchCommands = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/commands`);
      const data = await response.json();
      setCommands(data.commands);
      setConnectionStatus('connected');
    } catch (error) {
      console.error('Failed to fetch commands:', error);
      setConnectionStatus('error');
    }
  };

  const startRecording = async () => {
    try {
      console.log('Requesting permissions..');
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log('Starting recording..');
      const { recording } = await Audio.Recording.createAsync(
        Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
      console.log('Recording started');
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  const stopRecording = async () => {
    console.log('Stopping recording..');
    setIsRecording(false);
    setRecording(undefined);
    
    if (recording) {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      console.log('Recording stopped and stored at', uri);
      
      // Process the audio
      await processVoiceCommand(uri);
    }
  };

  const processVoiceCommand = async (audioUri) => {
    try {
      // Convert audio to base64 for API
      const response = await fetch(audioUri);
      const audioBlob = await response.blob();
      const reader = new FileReader();
      
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        try {
          const apiResponse = await fetch(`${API_BASE_URL}/voice/process`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              audio: base64Audio
            })
          });
          
          const result = await apiResponse.json();
          
          if (result.success) {
            setLastCommand({
              text: result.recognized_text,
              command: result.command,
              language: result.language,
              timestamp: new Date().toLocaleTimeString()
            });
            
            Alert.alert(
              "Command Executed",
              `Recognized: "${result.command}"\nLanguage: ${result.language}`,
              [
                { text: "👍 Correct", onPress: () => submitFeedback(true, result) },
                { text: "👎 Incorrect", onPress: () => submitFeedback(false, result) }
              ]
            );
          } else {
            Alert.alert("Error", result.error || "Command not recognized");
          }
        } catch (error) {
          console.error('API Error:', error);
          Alert.alert("Error", "Failed to process voice command");
        }
      };
      
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Processing error:', error);
    }
  };

  const executeManualCommand = async (commandId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/command/manual/${commandId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        Alert.alert("Success", `Command executed: ${commandData.find(c => c.id === commandId)?.action}`);
      } else {
        Alert.alert("Error", "Failed to execute command");
      }
    } catch (error) {
      console.error('Manual command error:', error);
      Alert.alert("Error", "Failed to execute command");
    }
  };

  const submitFeedback = async (isCorrect, commandResult) => {
    try {
      await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          detected_command: commandResult.command,
          is_correct: isCorrect,
          language: commandResult.language,
          voice_sample: null // Would include audio data in production
        })
      });
    } catch (error) {
      console.error('Feedback error:', error);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🐘 AI Elephant</Text>
        <Text style={styles.subtitle}>Mahout Command Module</Text>
        <View style={[styles.statusIndicator, 
          { backgroundColor: connectionStatus === 'connected' ? '#4CAF50' : '#F44336' }]}>
          <Text style={styles.statusText}>
            {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
          </Text>
        </View>
      </View>

      {/* Voice Control Section */}
      <View style={styles.voiceSection}>
        <TouchableOpacity
          style={[styles.micButton, isRecording && styles.micButtonActive]}
          onPressIn={startRecording}
          onPressOut={stopRecording}
        >
          <Icon 
            name={isRecording ? "mic" : "mic-none"} 
            size={40} 
            color={isRecording ? "#F44336" : "#2196F3"} 
          />
        </TouchableOpacity>
        <Text style={styles.micInstruction}>
          {isRecording ? "Recording... Release to stop" : "Hold to speak"}
        </Text>
      </View>

      {/* Last Command Display */}
      {lastCommand && (
        <View style={styles.lastCommandContainer}>
          <Text style={styles.lastCommandTitle}>Last Command:</Text>
          <Text style={styles.lastCommandText}>{lastCommand.command}</Text>
          <Text style={styles.lastCommandDetail}>
            "{lastCommand.text}" ({lastCommand.language}) - {lastCommand.timestamp}
          </Text>
        </View>
      )}

      {/* Manual Commands */}
      <ScrollView style={styles.commandsContainer}>
        <Text style={styles.sectionTitle}>Manual Commands</Text>
        {commandData.map((command) => (
          <TouchableOpacity
            key={command.id}
            style={styles.commandButton}
            onPress={() => executeManualCommand(command.id)}
          >
            <View style={styles.commandContent}>
              <Text style={styles.commandAction}>{command.action}</Text>
              <View style={styles.languageContainer}>
                <Text style={styles.languageText}>മല: {command.malayalam}</Text>
                <Text style={styles.languageText}>हि: {command.hindi}</Text>
                <Text style={styles.languageText}>ગુ: {command.gujarati}</Text>
              </View>
            </View>
            <Icon name="play-arrow" size={24} color="#2196F3" />
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 50,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    marginTop: 5,
  },
  statusIndicator: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 10,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  voiceSection: {
    alignItems: 'center',
    padding: 30,
    backgroundColor: 'white',
    margin: 10,
    borderRadius: 10,
    elevation: 2,
  },
  micButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 3,
  },
  micButtonActive: {
    backgroundColor: '#FFEBEE',
  },
  micInstruction: {
    marginTop: 10,
    fontSize: 14,
    color: '#666',
  },
  lastCommandContainer: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    elevation: 2,
  },
  lastCommandTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  lastCommandText: {
    fontSize: 18,
    color: '#2196F3',
    fontWeight: 'bold',
    marginTop: 5,
  },
  lastCommandDetail: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  commandsContainer: {
    flex: 1,
    margin: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  commandButton: {
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 8,
    borderRadius: 8,
    elevation: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  commandContent: {
    flex: 1,
  },
  commandAction: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  languageContainer: {
    marginTop: 5,
  },
  languageText: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
});

export default App;