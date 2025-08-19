import { ToggleButton, ToggleButtonGroup, Typography } from '@mui/material';

interface LanguageToggleProps {
  language: string;
  onLanguageChange: (lang: 'malayalam' | 'hindi' | 'gujarati') => void;
}

export default function LanguageToggle({ language, onLanguageChange }: LanguageToggleProps) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <Typography variant="subtitle1" gutterBottom>
        Display Language:
      </Typography>
      <ToggleButtonGroup
        value={language}
        exclusive
        onChange={(_, lang) => lang && onLanguageChange(lang)}
      >
        <ToggleButton value="malayalam">Malayalam</ToggleButton>
        <ToggleButton value="hindi">Hindi</ToggleButton>
        <ToggleButton value="gujarati">Gujarati</ToggleButton>
      </ToggleButtonGroup>
    </div>
  );
}