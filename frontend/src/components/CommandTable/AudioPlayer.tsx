import { IconButton } from '@mui/material';
import { VolumeUp } from '@mui/icons-material';

interface AudioPlayerProps {
  text: string;
  language: 'malayalam' | 'hindi' | 'gujarati';
}

export default function AudioPlayer({ text, language }: AudioPlayerProps) {
  const playAudio = () => {
    // Implement text-to-speech here
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set language based on selection
    utterance.lang = 
      language === 'malayalam' ? 'ml-IN' :
      language === 'hindi' ? 'hi-IN' : 'gu-IN';
    
    window.speechSynthesis.speak(utterance);
  };

  return (
    <IconButton onClick={playAudio} size="small">
      <VolumeUp fontSize="small" />
    </IconButton>
  );
}