import { AppBar, Toolbar, Typography } from '@mui/material';

export default function Header() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
          🐘 AI Elephant
        </Typography>
        <Typography variant="subtitle1">Command Module</Typography>
      </Toolbar>
    </AppBar>
  );
}