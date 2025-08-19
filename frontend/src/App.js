import React from 'react';
import { Container } from '@mui/material';
import SensorDisplay from './components/SensorDisplay';
import ControlPanel from './components/ControlPanel';

function App() {
  return (
    <Container maxWidth="md">
      <h1>AI Elephant Controller</h1>
      <SensorDisplay />
      <ControlPanel />
    </Container>
  );
}

export default App;