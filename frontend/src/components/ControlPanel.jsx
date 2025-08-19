import React from 'react';
import { sendCommand } from '../services/api';
import { Button, Stack } from '@mui/material';

export default function ControlPanel() {
  const handleCommand = (cmd) => {
    sendCommand(cmd).then(() => alert(`${cmd} sent!`));
  };

  return (
    <Stack direction="row" spacing={2}>
      <Button variant="contained" onClick={() => handleCommand('MOVE_FORWARD')}>
        Move Forward
      </Button>
      <Button variant="contained" onClick={() => handleCommand('STOP')}>
        Stop
      </Button>
    </Stack>
  );
}