import { Box, Typography, Button } from '@mui/material';
import { ThumbUp, ThumbDown } from '@mui/icons-material';

export default function FeedbackSystem() {
  return (
    <Box sx={{ mt: 4, p: 2, border: '1px solid #ccc', borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Command Feedback
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Typography>Was this command recognized correctly?</Typography>
        <Button variant="outlined" startIcon={<ThumbUp />} color="success">
          Correct
        </Button>
        <Button variant="outlined" startIcon={<ThumbDown />} color="error">
          Incorrect
        </Button>
      </Box>
    </Box>
  );
}