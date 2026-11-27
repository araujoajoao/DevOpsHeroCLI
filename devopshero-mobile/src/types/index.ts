export type ThemeMode = 'light' | 'dark';

export interface MissionOption {
  text: string;
  is_correct: boolean;
  explanation: string;
}

export interface WordBankExercise {
  type: string;
  target_tokens: string[];
  chips: string[];
}

export interface Mission {
  id: string;
  order: number;
  title: string;
  difficulty: 'Iniciante' | 'Intermediário' | 'Avançado';
  xp: number;
  objective: string;
  real_world_context: string;
  tip: string;
  solution: string;
  exercise_types: {
    word_bank: WordBankExercise;
    fill_blank: {
      type: string;
      template: string;
      missing_token: string;
      options: string[];
    };
    multiple_choice: {
      type: string;
      question: string;
      options: MissionOption[];
    };
  };
}

export interface Track {
  id: string;
  name: string;
  icon: string;
  description: string;
  required_xp?: number;
  required_seniority?: string;
  gradient: [string, string];
  missions: Mission[];
}

export interface MobileDataset {
  app_name: string;
  version: string;
  total_tracks: number;
  total_missions: number;
  tracks: Track[];
}

export type TabType = 'home' | 'tracks' | 'practice' | 'profile';

