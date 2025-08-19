import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

export const sendCommand = async (command: string, language: string) => {
  return api.post('/commands', { command, language });
};

export const sendFeedback = async (data: {
  commandId: number;
  correct: boolean;
  audio?: Blob;
}) => {
  const formData = new FormData();
  formData.append('commandId', data.commandId.toString());
  formData.append('correct', data.correct.toString());
  if (data.audio) {
    formData.append('audio', data.audio);
  }
  return api.post('/feedback', formData);
};