import React, { useEffect, useState } from 'react';
import { getSensorData } from '../services/api';
import { Box, Typography, LinearProgress } from '@mui/material';

export default function SensorDisplay() {
  const [sensors, setSensors] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const { data } = await getSensorData();
      setSensors(data);
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <Box>
      <Typography variant="h6">Elephant Sensors</Typography>
      {sensors ? (
        <div>
          <p>Temperature: {sensors.temp}°C</p>
          <p>Humidity: {sensors.humidity}%</p>
          <LinearProgress 
            variant="determinate" 
            value={sensors.touchPressure} 
          />
        </div>
      ) : <p>Loading...</p>}
    </Box>
  );
}