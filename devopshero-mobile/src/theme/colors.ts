export const Gradients = {
  math: ['#071321', '#0b1d33'] as const,
  physics: ['#18080c', '#2b0f16'] as const,
  chemistry: ['#181205', '#2e2108'] as const,
  reasoning: ['#0f0b1a', '#1e1436'] as const,
  docker: ['#05141c', '#092636'] as const,
  k8s: ['#0a0f24', '#121a42'] as const,
  git: ['#061c12', '#0c3622'] as const,
  datadog: ['#130a21', '#241340'] as const,
  hero: ['#090b10', '#0f172a'] as const,
  avatar: ['#9E85FF', '#00DF89', '#00F2FE'] as const,
  activePill: ['#9E85FF', '#8B5CF6'] as const,
  liquidLilac: ['#B39DFF', '#9E85FF', '#7C5CFC'] as const,
  glassSheen: ['rgba(255, 255, 255, 0.20)', 'rgba(255, 255, 255, 0.04)', 'transparent'] as const,
  glassSheenLight: ['rgba(255, 255, 255, 0.70)', 'rgba(255, 255, 255, 0.20)', 'transparent'] as const,
};

export const ThemeColors = {
  light: {
    bgPage: '#f1f5f9',
    appBg: '#f8fafc',
    terminalWindowBg: 'rgba(255, 255, 255, 0.85)',
    terminalHeaderBg: 'rgba(241, 245, 249, 0.90)',
    cardBg: '#EDF0F7',
    cardSubtle: '#f8fafc',
    border: 'rgba(0, 0, 0, 0.08)',
    borderAccentCyan: '#0284c7',
    borderAccentGreen: '#16a34a',
    borderAccentAmber: '#d97706',
    borderAccentRose: '#e11d48',

    liquidGlassBg: 'rgba(255, 255, 255, 0.76)',
    liquidGlassBorder: 'rgba(255, 255, 255, 0.65)',
    liquidGlassBorderSubtle: 'rgba(0, 0, 0, 0.07)',
    liquidGlassLilac: '#9E85FF',
    liquidGlassLilacGlow: 'rgba(158, 133, 255, 0.25)',

    textMain: '#0f172a',
    textMuted: '#64748b',
    textCyan: '#0284c7',
    textGreen: '#16a34a',
    textAmber: '#b45309',
    textRose: '#e11d48',

    codeBg: '#0f172a',
    codeText: '#4ade80',
    codeComment: '#94a3b8',
    codePrompt: '#38bdf8',

    dotRed: '#ef4444',
    dotYellow: '#eab308',
    dotGreen: '#22c55e',

    glassDockBg: 'rgba(255, 255, 255, 0.88)',
    glassDockBorder: 'rgba(0, 0, 0, 0.08)',
    glassDockText: '#475569',
    glassDockActiveText: '#ffffff',

    glassBtnBg: 'rgba(255, 255, 255, 0.85)',
    glassBtnBorder: 'rgba(0, 0, 0, 0.08)',
    sheetBg: 'rgba(255, 255, 255, 0.94)',
    sheetBorder: 'rgba(0, 0, 0, 0.08)',

    pillCorrectBg: 'rgba(22, 163, 74, 0.12)',
    pillCorrectText: '#16a34a',
    pillWrongBg: 'rgba(225, 29, 72, 0.12)',
    pillWrongText: '#e11d48',

    primaryBtn: '#9E85FF',
    successBtn: '#16a34a',
    errorBtn: '#e11d48',
  },
  dark: {
    bgPage: '#0c0d1a',
    appBg: '#131627', // Official dark violet-navy (AGENTS.md Section 4)
    terminalWindowBg: 'rgba(22, 27, 46, 0.80)',
    terminalHeaderBg: 'rgba(17, 21, 31, 0.85)',
    cardBg: '#272E4F', // Official slate-navy
    cardSubtle: '#1E243E',
    border: 'rgba(255, 255, 255, 0.12)',
    borderAccentCyan: '#00F2FE',
    borderAccentGreen: '#00DF89',
    borderAccentAmber: '#FBBF24',
    borderAccentRose: '#FB7185',

    liquidGlassBg: 'rgba(39, 46, 79, 0.68)',
    liquidGlassBorder: 'rgba(255, 255, 255, 0.16)',
    liquidGlassBorderSubtle: 'rgba(255, 255, 255, 0.08)',
    liquidGlassLilac: '#9E85FF',
    liquidGlassLilacGlow: 'rgba(158, 133, 255, 0.35)',

    textMain: '#f1f5f9',
    textMuted: '#94a3b8',
    textCyan: '#00F2FE',
    textGreen: '#00DF89',
    textAmber: '#FBBF24',
    textRose: '#FB7185',

    codeBg: '#090B12',
    codeText: '#00DF89',
    codeComment: '#8A94B8',
    codePrompt: '#00F2FE',

    dotRed: '#FB7185',
    dotYellow: '#FBBF24',
    dotGreen: '#00DF89',

    glassDockBg: 'rgba(19, 22, 39, 0.88)',
    glassDockBorder: 'rgba(255, 255, 255, 0.16)',
    glassDockText: '#94a3b8',
    glassDockActiveText: '#ffffff',

    glassBtnBg: 'rgba(39, 46, 79, 0.65)',
    glassBtnBorder: 'rgba(255, 255, 255, 0.16)',
    sheetBg: 'rgba(19, 22, 39, 0.94)',
    sheetBorder: 'rgba(255, 255, 255, 0.14)',

    pillCorrectBg: 'rgba(0, 223, 137, 0.14)',
    pillCorrectText: '#00DF89',
    pillWrongBg: 'rgba(251, 113, 133, 0.14)',
    pillWrongText: '#FB7185',

    primaryBtn: '#9E85FF',
    successBtn: '#00DF89',
    errorBtn: '#FB7185',
  },
};
