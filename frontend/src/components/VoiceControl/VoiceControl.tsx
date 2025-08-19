import { useState } from 'react';
import { Mic, MicOff } from '@mui/icons-material';
import { IconButton, CircularProgress, Box, Typography } from '@mui/material'; // Added Typography here
import useVoiceRecognition from '../../hooks/useVoiceRecognition';

export default function VoiceControl() {
  const [isListening, setIsListening] = useState(false);
  const { transcript, startListening, stopListening } = useVoiceRecognition();

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
    setIsListening(!isListening);
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <IconButton
        color={isListening ? 'secondary' : 'default'}
        onClick={toggleListening}
        size="large"
      >
        {isListening ? <MicOff /> : <Mic />}
      </IconButton>
      {isListening && <CircularProgress size={24} color="secondary" />}
      {transcript && <Typography variant="body1">{transcript}</Typography>}
    </Box>
  );
}