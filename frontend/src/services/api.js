import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api', // Your backend URL
});

// Sensor Data
export const getSensorData = () => API.get('/sensors');
export const sendCommand = (command) => API.post('/commands', { command });

// Camera Stream
export const getCameraFeed = () => `${API.defaults.baseURL}/camera_feed`;