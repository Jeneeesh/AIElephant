export interface Command {
  id: number;
  action: string;
  malayalam: string;
  hindi: string;
  gujarati: string;
}

export const commands: Command[] = [
  {
    id: 1,
    action: 'Turn Left',
    malayalam: 'ഇടത്താനെ (Idathāne)',
    hindi: 'बाएं (Bāẽ)',
    gujarati: 'ડાબે (Ḍābe)'
  },
  // ... all other commands
];