import React from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Header from './components/Header';
import VoiceControl from './components/VoiceControl';
import CommandTable from './components/CommandTable';
import FeedbackSystem from './components/FeedbackSystem';

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Header />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <VoiceControl />
        <CommandTable />
        <FeedbackSystem />
      </Container>
    </ThemeProvider>
  );
}

export default App;