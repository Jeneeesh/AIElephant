import { io } from 'socket.io-client';

const socket = io(process.env.REACT_APP_WS_URL);

export const connectSocket = () => {
  socket.connect();
};

export const subscribeToCommands = (callback: (command: string) => void) => {
  socket.on('command', callback);
};

export const unsubscribeFromCommands = () => {
  socket.off('command');
};