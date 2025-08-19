import { useState } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

export default function useVoiceRecognition() {
  const [language, setLanguage] = useState<'ml' | 'hi' | 'gu'>('ml');
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  const startListening = () => {
    SpeechRecognition.startListening({
      continuous: true,
      language: language === 'ml' ? 'ml-IN' : language === 'hi' ? 'hi-IN' : 'gu-IN'
    });
  };

  const stopListening = () => {
    SpeechRecognition.stopListening();
    resetTranscript();
  };

  return {
    transcript,
    listening,
    startListening,
    stopListening,
    setLanguage,
    browserSupportsSpeechRecognition
  };
}