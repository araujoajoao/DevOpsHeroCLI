import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  Alert,
  Platform,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { ThemeColors } from '../theme/colors';
import { Mission, Track } from '../types';
import { CURRENT_DEVICE } from '../utils/deviceInfo';
import { LiquidGlassView } from '../components/LiquidGlassView';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { DynamicIslandBanner } from '../components/DynamicIslandBanner';
import { LiveActivityService } from '../services/LiveActivityService';

interface PracticeScreenProps {
  theme: 'light' | 'dark';
  track: Track;
  missionIndex: number;
  onClose: () => void;
  onGoToTracks?: () => void;
  onMissionComplete: (xpGained: number, newStreak: number) => void;
  onBreakStreak: () => void;
  onNextMission: () => void;
  streak: number;
  xp: number;
}

export interface AwardResult {
  xp: number;
  baseXP: number;
  factor: number;
  tierName: string;
  elapsedSeconds: number;
  tipsUsed: number;
  streakBonusPct: number;
  isNinja: boolean;
  solutionUsed: boolean;
}

export function calculateMissionAward(
  baseXP: number,
  elapsedSeconds: number,
  tipsUsed: number,
  currentStreak: number,
  solutionUsed: boolean
): AwardResult {
  if (solutionUsed) {
    return {
      xp: 0,
      baseXP,
      factor: 0,
      tierName: 'Gabarito Revelado (0 XP)',
      elapsedSeconds,
      tipsUsed,
      streakBonusPct: 0,
      isNinja: false,
      solutionUsed: true,
    };
  }

  let factor = 1.0;
  let isNinja = false;
  let tierName = '';

  if (tipsUsed === 0) {
    if (elapsedSeconds <= 5.0) {
      factor = 1.0;
      isNinja = true;
      tierName = '⚡ 100% Ninja Reflex (<5s sem dicas!)';
    } else {
      factor = 0.70;
      tierName = `⏱️ Tempo > 5s (${elapsedSeconds.toFixed(1)}s) - 70% XP`;
    }
  } else {
    if (tipsUsed === 1) {
      factor = 0.40;
      tierName = '💡 1 Dica Usada - 40% XP (-60%)';
    } else if (tipsUsed === 2) {
      factor = 0.20;
      tierName = '💡 2 Dicas Usadas - 20% XP (-80%)';
    } else {
      factor = 0.10;
      tierName = `💡 ${tipsUsed} Dicas Usadas - 10% XP (-90%)`;
    }
  }

  // Streak bonus: +5% per streak count up to a maximum of +50%
  const bonusPct = Math.min(50, currentStreak * 5);
  const calcXP = Math.round(baseXP * factor * (1 + bonusPct / 100.0));
  const earnedXP = Math.max(5, calcXP);

  return {
    xp: earnedXP,
    baseXP,
    factor,
    tierName,
    elapsedSeconds,
    tipsUsed,
    streakBonusPct: bonusPct,
    isNinja,
    solutionUsed: false,
  };
}

export function getMissionProgressiveTips(mission: Mission): string[] {
  const tokens = mission.exercise_types?.word_bank?.target_tokens || [];
  const solution = (mission.solution || '').trim();
  const rawTip = (mission.tip || '').trim();
  const objective = (mission.objective || '').trim();

  const firstCmd = tokens[0] || (solution.split(' ')[0] || 'comando');
  const numTokens = tokens.length;

  // Dica 1: Ponto de partida e utilitário conceitual
  const hint1 = `Início da operação: O comando inicia com o utilitário "${firstCmd}". Objetivo: ${objective}`;

  // Dica 2: Estrutura da sintaxe, flags e operadores
  let hint2 = '';
  if (numTokens <= 1) {
    hint2 = `Estrutura simples: Este comando não requer argumentos adicionais. Ele é composto por apenas um bloco no terminal.`;
  } else if (tokens.includes('&&') || tokens.includes('|')) {
    const ops = tokens.filter(t => ['&&', '|', '||', ';'].includes(t));
    hint2 = `Comando composto: Esta tarefa requer o operador "${ops.join(' ')}" conectando as operações em cadeia.`;
  } else {
    const flags = tokens.slice(1).filter(t => t.startsWith('-'));
    const args = tokens.slice(1).filter(t => !t.startsWith('-'));
    if (flags.length > 0 && args.length > 0) {
      hint2 = `Parâmetros e argumentos: Combine "${firstCmd}" com a flag ${flags[0]} apontando para "${args[0]}". (Total de ${numTokens} blocos).`;
    } else if (flags.length > 0) {
      hint2 = `Modificadores: Utilize a(s) opção(ões) ${flags.join(', ')} junto com "${firstCmd}".`;
    } else if (args.length > 0) {
      hint2 = `Argumento alvo: O comando atua sobre "${args[0]}". Linha montada com ${numTokens} blocos.`;
    } else {
      hint2 = `Estrutura da linha de comando: Selecione ${numTokens} blocos na ordem correta de execução.`;
    }
  }

  // Dica 3: Orientação técnica aprofundada
  const hint3 = `Orientação avançada: ${rawTip}`;

  return [hint1, hint2, hint3];
}

export function getSyntaxColor(token: string): string {
  const lower = token.toLowerCase();
  if (['docker', 'kubectl', 'git', 'chmod', 'aws', 'terraform', 'cat', 'grep', 'ls', 'pwd', 'mkdir', 'datadog-agent'].includes(lower)) {
    return '#fb7185'; // coral / command
  } else if (lower.startsWith('-')) {
    return '#fbbf24'; // amber / flags
  } else if (['run', 'build', 'commit', 'push', 'pull', 'apply', 'init', 'plan', 'exec', 'ps', 'stop', 'start', 'logs', 'create', 'delete', 'get'].includes(lower)) {
    return '#9e85ff'; // lilac / subcommands
  } else if (lower.includes(':') || lower.includes('/') || lower.includes('.') || lower.startsWith('"') || lower.startsWith("'")) {
    return '#00df89'; // mint green / parameters/values
  }
  return '#00f2fe'; // cyan / default args
}

interface TerminalMascotProps {
  isCorrect: boolean;
  solutionUsed: boolean;
  isDark: boolean;
}

export const TerminalMascot: React.FC<TerminalMascotProps> = ({
  isCorrect,
  solutionUsed,
  isDark,
}) => {
  return (
    <View style={styles.mascotContainer}>
      <View
        style={[
          styles.mascotBody,
          {
            backgroundColor: isDark ? '#e2e8f0' : '#475569',
          },
        ]}
      >
        {/* Inner CRT Screen */}
        <View style={styles.mascotScreen}>
          {!isCorrect ? (
            <Text style={styles.mascotScreenCross}>✕</Text>
          ) : solutionUsed ? (
            <View style={styles.mascotEyesRow}>
              <View style={styles.mascotDotEye} />
              <View style={styles.mascotDotEye} />
            </View>
          ) : (
            <Text style={styles.mascotScreenCheck}>✓</Text>
          )}
        </View>

        {/* LED Indicator Dot */}
        <View
          style={[
            styles.mascotLed,
            { backgroundColor: isCorrect ? '#00df89' : '#fb7185' },
          ]}
        />
      </View>

      {/* Monitor Feet */}
      <View style={styles.mascotFeetRow}>
        <View style={styles.mascotFoot} />
        <View style={styles.mascotFoot} />
      </View>
    </View>
  );
};

export const PracticeScreen: React.FC<PracticeScreenProps> = ({
  theme,
  track,
  missionIndex,
  onClose,
  onGoToTracks,
  onMissionComplete,
  onBreakStreak,
  onNextMission,
  streak,
  xp,
}) => {
  const colors = ThemeColors[theme];
  const isDark = theme === 'dark';
  const mission: Mission = track.missions[missionIndex] || track.missions[0];

  const missionTips = getMissionProgressiveTips(mission);
  const MAX_TIPS = Math.min(3, missionTips.length);

  const [placedChips, setPlacedChips] = useState<string[]>([]);
  const [availableChips, setAvailableChips] = useState<
    { id: string; text: string; placed: boolean }[]
  >([]);
  const [sheetVisible, setSheetVisible] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [tipModalVisible, setTipModalVisible] = useState(false);
  const [tipsUsed, setTipsUsed] = useState(0);
  const [currentTipText, setCurrentTipText] = useState('');
  const [hasMoreTips, setHasMoreTips] = useState(true);
  const [currentTipNumber, setCurrentTipNumber] = useState(1);
  const [solutionUsed, setSolutionUsed] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [lastAward, setLastAward] = useState<AwardResult | null>(null);

  // Pause Track & Navigation Controls
  const [pauseModalVisible, setPauseModalVisible] = useState(false);
  const accumulatedSecondsRef = useRef<number>(0);
  const startTimeRef = useRef<number>(Date.now());
  const timerIntervalRef = useRef<any>(null);

  const startTimer = () => {
    startTimeRef.current = Date.now();
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    timerIntervalRef.current = setInterval(() => {
      const currentRun = Math.floor((Date.now() - startTimeRef.current) / 1000);
      const totalSec = accumulatedSecondsRef.current + currentRun;
      setSecondsElapsed(totalSec);

      const mult = totalSec <= 5 ? 1.5 : (totalSec <= 15 ? 1.2 : 1.0);
      LiveActivityService.updateLabActivity({
        secondsElapsed: totalSec,
        speedScoreMultiplier: mult,
      });
    }, 1000);
  };

  const stopTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    const currentRun = Math.floor((Date.now() - startTimeRef.current) / 1000);
    accumulatedSecondsRef.current += currentRun;
  };

  const handlePause = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (_) {}
    stopTimer();
    setPauseModalVisible(true);
    LiveActivityService.updateLabActivity({ status: 'PAUSED' });
  };

  const handleResume = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
    setPauseModalVisible(false);
    LiveActivityService.updateLabActivity({ status: 'ONLINE' });
    startTimer();
  };

  const handleExitToHome = () => {
    stopTimer();
    setPauseModalVisible(false);
    LiveActivityService.endLabActivity();
    onClose();
  };

  const handleExitToTracks = () => {
    stopTimer();
    setPauseModalVisible(false);
    LiveActivityService.endLabActivity();
    if (onGoToTracks) {
      onGoToTracks();
    } else {
      onClose();
    }
  };

  useEffect(() => {
    const rawTokens =
      mission.exercise_types.word_bank.chips &&
      mission.exercise_types.word_bank.chips.length > 0
        ? mission.exercise_types.word_bank.chips
        : mission.exercise_types.word_bank.target_tokens;

    const shuffled = rawTokens
      .map((t, idx) => ({ id: `${idx}-${t}`, text: t, sort: Math.random() }))
      .sort((a, b) => a.sort - b.sort)
      .map(item => ({ id: item.id, text: item.text, placed: false }));

    setAvailableChips(shuffled);
    setPlacedChips([]);
    setSheetVisible(false);
    setTipsUsed(0);
    setCurrentTipText('');
    setHasMoreTips(true);
    setCurrentTipNumber(1);
    setSolutionUsed(false);
    setLastAward(null);

    accumulatedSecondsRef.current = 0;
    setSecondsElapsed(0);
    setPauseModalVisible(false);

    // Start Live Activity & Dynamic Island (ActivityKit)
    LiveActivityService.startLabActivity(
      {
        trackId: track.id,
        trackName: track.name,
        trackIcon: track.icon,
        operatorHandle: '@devops',
      },
      {
        missionId: mission.id,
        missionIndex,
        missionTitle: mission.title,
        objective: mission.objective,
        xpReward: mission.xp,
        status: 'ONLINE',
        secondsElapsed: 0,
        speedScoreMultiplier: 1.5,
        completedCount: missionIndex,
        totalMissions: track.missions.length,
      }
    );

    startTimer();

    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [track.id, mission.id]);

  const handleAddChip = (chipId: string, text: string) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}

    setPlacedChips(prev => [...prev, text]);
    setAvailableChips(prev =>
      prev.map(c => (c.id === chipId ? { ...c, placed: true } : c))
    );
  };

  const handleRemoveChip = (index: number) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}

    const textToRemove = placedChips[index];
    const newPlaced = [...placedChips];
    newPlaced.splice(index, 1);
    setPlacedChips(newPlaced);

    setAvailableChips(prev => {
      let restored = false;
      return prev.map(c => {
        if (!restored && c.text === textToRemove && c.placed) {
          restored = true;
          return { ...c, placed: false };
        }
        return c;
      });
    });
  };

  const handleOpenTip = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (_) {}

    if (tipsUsed < MAX_TIPS) {
      const nextCount = tipsUsed + 1;
      setTipsUsed(nextCount);
      setCurrentTipText(missionTips[nextCount - 1]);
      setHasMoreTips(true);
      setCurrentTipNumber(nextCount);
      setTipModalVisible(true);
    } else {
      // Limite de 3 dicas atingido: não repete e não soma deduções extras
      setCurrentTipText(
        '🛑 Não há mais dicas disponíveis para esta missão.\n\nVocê já visualizou todas as 3 orientações progressivas. Monte o comando no terminal com os blocos disponíveis ou use o Gabarito se precisar da resposta completa.'
      );
      setHasMoreTips(false);
      setCurrentTipNumber(MAX_TIPS);
      setTipModalVisible(true);
    }
  };

  const handleRevealSolution = () => {
    Alert.alert(
      '👁️ Revelar Gabarito (Gabarito CLI)',
      'Atenção Operador: Revelar a resposta oficial concede 0 XP nesta missão e zera sua sequência diária (streak = 0). Deseja continuar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Revelar Gabarito',
          style: 'destructive',
          onPress: () => {
            setSolutionUsed(true);
            onBreakStreak();

            // Populate terminal with target tokens so operator sees the correct command assembly
            const targetTokens = mission.exercise_types.word_bank.target_tokens;
            setPlacedChips([...targetTokens]);
            setAvailableChips(prev => {
              const remainingTarget = [...targetTokens];
              return prev.map(chip => {
                const matchIndex = remainingTarget.indexOf(chip.text);
                if (matchIndex !== -1) {
                  remainingTarget.splice(matchIndex, 1);
                  return { ...chip, placed: true };
                }
                return { ...chip, placed: false };
              });
            });

            executeVerification(mission.solution, true);
          },
        },
      ]
    );
  };

  const executeVerification = (userCmd: string, isExplicitSolution: boolean = false) => {
    stopTimer();
    const targetTokens = mission.exercise_types.word_bank.target_tokens;
    const targetCmd = targetTokens.join(' ');
    const correct = isExplicitSolution || (userCmd === targetCmd || userCmd === mission.solution);

    if (isExplicitSolution) {
      setSolutionUsed(true);
    }

    const elapsed = Math.max(0.5, secondsElapsed);
    const award = calculateMissionAward(
      mission.xp,
      elapsed,
      tipsUsed,
      streak,
      isExplicitSolution || solutionUsed
    );

    setIsCorrect(correct);
    setLastAward(award);
    setSheetVisible(true);

    if (correct) {
      try {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } catch (_) {}
      const newStreak = (isExplicitSolution || solutionUsed) ? 0 : streak + 1;
      onMissionComplete(award.xp, newStreak);
      LiveActivityService.updateLabActivity({
        status: 'COMPLETED',
        completedCount: missionIndex + 1,
      });
    } else {
      try {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      } catch (_) {}
      LiveActivityService.updateLabActivity({ status: 'TRY AGAIN' });
    }
  };

  const handleVerify = () => {
    if (placedChips.length === 0) return;
    executeVerification(placedChips.join(' '), false);
  };

  const handleSheetAction = () => {
    setSheetVisible(false);
    if (isCorrect) {
      onNextMission();
    } else {
      startTimer();
    }
  };

  const progressPct = ((missionIndex + 1) / track.missions.length) * 100;

  return (
    <View style={[styles.container, { backgroundColor: 'transparent' }]}>
      {/* 1. Pinned Apple HIG Navigation Header (Always Accessible) */}
      <View
        style={[
          styles.pinnedNavHeader,
          {
            backgroundColor: isDark ? 'rgba(15, 18, 35, 0.75)' : 'rgba(255, 255, 255, 0.82)',
            borderBottomColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)',
          },
        ]}
      >
        <View style={styles.practiceNavRow}>
          <TouchableOpacity
            style={styles.navBackBtn}
            onPress={handleExitToHome}
            activeOpacity={0.7}
            hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
          >
            <Text style={[styles.navBackIcon, { color: isDark ? '#00f2fe' : '#0284c7' }]}>‹</Text>
            <Text style={[styles.navBackText, { color: isDark ? '#00f2fe' : '#0284c7' }]}>
              Início
            </Text>
          </TouchableOpacity>

          <View style={styles.navTitleCenter}>
            <Text
              style={[styles.navTrackTitle, { color: colors.textMain }]}
              numberOfLines={1}
              ellipsizeMode="tail"
            >
              {track.name}
            </Text>
            <Text
              style={[styles.navMissionStep, { color: colors.textMuted }]}
              numberOfLines={1}
              ellipsizeMode="tail"
            >
              Missão {missionIndex + 1} de {track.missions.length}
            </Text>
          </View>

          {/* Right Header Controls: Pause Button & Live Time */}
          <View style={styles.navRightActions}>
            <TouchableOpacity
              style={[
                styles.pauseHeaderBtn,
                {
                  backgroundColor: isDark ? 'rgba(251, 191, 36, 0.15)' : 'rgba(217, 119, 6, 0.12)',
                  borderColor: isDark ? '#fbbf24' : '#d97706',
                },
              ]}
              onPress={handlePause}
              activeOpacity={0.75}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              accessibilityLabel="Pausar Missão"
              accessibilityRole="button"
            >
              <Text style={[styles.pauseHeaderBtnText, { color: isDark ? '#fbbf24' : '#d97706' }]}>
                ⏸ Pausar
              </Text>
            </TouchableOpacity>

            <View
              style={[
                styles.hudBadge,
                {
                  borderColor: secondsElapsed <= 5 ? (isDark ? '#00ff87' : '#16a34a') : colors.border,
                  backgroundColor: secondsElapsed <= 5 ? 'rgba(0, 255, 135, 0.1)' : colors.cardSubtle,
                },
              ]}
            >
              <Text
                style={[
                  styles.hudBadgeText,
                  { color: secondsElapsed <= 5 ? (isDark ? '#00ff87' : '#16a34a') : colors.textMain },
                ]}
                numberOfLines={1}
              >
                ⏱️ {secondsElapsed}s
              </Text>
            </View>
          </View>
        </View>

        {/* Progress Track */}
        <View style={[styles.progressTrack, { backgroundColor: colors.cardSubtle }]}>
          <View style={[styles.progressFill, { width: `${progressPct}%`, backgroundColor: isDark ? '#00f2fe' : '#0284c7' }]} />
        </View>
      </View>

      {/* Apple Live Activities & Dynamic Island Banner */}
      <DynamicIslandBanner />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >

        {/* Interactive Code Editor Window with Line Numbers & Syntax Highlighting (media_1793714309288_cf334ed3.png) */}
        <LiquidGlassView
          borderRadius={20}
          borderWidth={1.2}
          borderColor={isDark ? 'rgba(255, 255, 255, 0.16)' : 'rgba(0, 0, 0, 0.08)'}
          theme={theme}
          showSheen={true}
          intensity={65}
          style={styles.codeEditorWrapper}
          contentStyle={styles.codeEditorInterior}
        >
          {/* Editor Header Bar with Filename and XP */}
          <View style={styles.editorTabBar}>
            <View style={styles.editorWindowDots}>
              <View style={[styles.windowDot, { backgroundColor: '#FB7185' }]} />
              <View style={[styles.windowDot, { backgroundColor: '#FBBF24' }]} />
              <View style={[styles.windowDot, { backgroundColor: '#00DF89' }]} />
            </View>
            <Text style={[styles.editorTabFilename, { color: isDark ? '#A5B4FC' : '#475569' }]} numberOfLines={1}>
              {mission.title}.sh
            </Text>
            <View style={styles.editorXpBadge}>
              <Text style={styles.editorXpText}>⭐ {mission.xp} XP</Text>
            </View>
          </View>
          <View style={[styles.editorDivider, { backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)' }]} />

          {/* Line 1: Comment with Mission Objective */}
          <View style={[styles.codeLineRow, { alignItems: 'flex-start' }]}>
            <Text style={[styles.codeLineNumber, { color: isDark ? '#475569' : '#94a3b8', paddingTop: 2 }]}>
              1
            </Text>
            <Text style={[styles.codeCommentLine, { color: isDark ? '#8a94b8' : '#64748b' }]}>
              # {mission.objective}
            </Text>
          </View>

          {/* Line 2: Interactive Prompt & Command Assembly Slot */}
          <View style={[styles.codeLineRow, { marginTop: 10, alignItems: 'center' }]}>
            <Text style={[styles.codeLineNumber, { color: isDark ? '#475569' : '#94a3b8' }]}>
              2
            </Text>
            <View style={styles.promptAndSlotContainer}>
              <Text style={styles.codePromptDollar}>$</Text>
              <View
                style={[
                  styles.slotReceptacle,
                  placedChips.length === 0
                    ? [
                        styles.slotReceptacleEmpty,
                        {
                          borderColor: isDark ? 'rgba(158, 133, 255, 0.40)' : 'rgba(158, 133, 255, 0.50)',
                          backgroundColor: isDark ? 'rgba(158, 133, 255, 0.05)' : 'rgba(158, 133, 255, 0.04)',
                        },
                      ]
                    : [
                        styles.slotReceptacleFilled,
                        {
                          borderColor: isDark ? 'rgba(158, 133, 255, 0.30)' : 'rgba(158, 133, 255, 0.35)',
                          backgroundColor: isDark ? 'rgba(0, 0, 0, 0.25)' : 'rgba(255, 255, 255, 0.60)',
                        },
                      ],
                ]}
              >
                {placedChips.length === 0 ? (
                  <Text style={[styles.slotPlaceholderText, { color: isDark ? '#64748b' : '#94a3b8' }]}>
                    toque nos blocos abaixo para montar...
                  </Text>
                ) : (
                  placedChips.map((chip, i) => {
                    const tokenColor = getSyntaxColor(chip);
                    return (
                      <TouchableOpacity
                        key={i}
                        style={[
                          styles.syntaxPlacedToken,
                          {
                            backgroundColor: `${tokenColor}20`,
                            borderColor: `${tokenColor}70`,
                          },
                        ]}
                        onPress={() => handleRemoveChip(i)}
                        activeOpacity={0.7}
                        hitSlop={{ top: 6, bottom: 6, left: 4, right: 4 }}
                      >
                        <Text style={[styles.syntaxPlacedTokenText, { color: tokenColor }]}>
                          {chip}
                        </Text>
                      </TouchableOpacity>
                    );
                  })
                )}
              </View>
            </View>
          </View>
        </LiquidGlassView>

        {/* 4. Available Chips Tray (Word Bank) */}
        <LiquidGlassView
          borderRadius={20}
          borderWidth={1.2}
          borderColor={isDark ? 'rgba(255, 255, 255, 0.14)' : 'rgba(0, 0, 0, 0.08)'}
          theme={theme}
          variant="tray"
          showSheen={true}
          intensity={60}
          style={styles.wordBankWrapper}
          contentStyle={styles.wordBankInterior}
        >
          {/* Tray Header */}
          <View style={styles.wordBankHeader}>
            <View style={[styles.wordBankBadge, { backgroundColor: isDark ? '#161B2E' : '#E2E8F0' }]}>
              <Text style={styles.wordBankBadgeText}>⌨️ TOKENS</Text>
            </View>
            <Text style={[styles.wordBankHintText, { color: isDark ? '#64748B' : '#94A3B8' }]}>
              toque para selecionar
            </Text>
          </View>

          <View style={[styles.wordBankDivider, { backgroundColor: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)' }]} />

          {/* Chips Flow */}
          <View style={styles.chipsPool}>
            {availableChips.map(c => {
              const tokenColor = getSyntaxColor(c.text);
              return (
                <TouchableOpacity
                  key={c.id}
                  style={[
                    styles.poolChip,
                    {
                      backgroundColor: c.placed
                        ? isDark
                          ? 'rgba(255, 255, 255, 0.02)'
                          : 'rgba(0, 0, 0, 0.03)'
                        : isDark
                        ? 'rgba(255, 255, 255, 0.075)'
                        : 'rgba(255, 255, 255, 0.65)',
                      borderColor: c.placed
                        ? isDark
                          ? 'rgba(158, 133, 255, 0.15)'
                          : 'rgba(158, 133, 255, 0.20)'
                        : tokenColor,
                    },
                    c.placed && styles.poolChipDisabled,
                    !c.placed && isDark && {
                      shadowColor: tokenColor,
                      shadowOffset: { width: 0, height: 2 },
                      shadowOpacity: 0.18,
                      shadowRadius: 4,
                      elevation: 2,
                    },
                  ]}
                  onPress={() => !c.placed && handleAddChip(c.id, c.text)}
                  disabled={c.placed}
                  activeOpacity={0.7}
                  hitSlop={{ top: 6, bottom: 6, left: 6, right: 6 }}
                >
                  <Text
                    style={[
                      styles.poolChipText,
                      {
                        color: c.placed
                          ? colors.textMuted
                          : tokenColor,
                        opacity: c.placed ? 0.22 : 1,
                      },
                    ]}
                    numberOfLines={1}
                  >
                    {c.text}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </LiquidGlassView>
      </ScrollView>

      {/* 5. Sticky Bottom Action Bar with Liquid Glass Styling */}
      <View
        style={[
          styles.bottomBar,
          {
            backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.70)',
            borderTopColor: isDark ? 'rgba(255, 255, 255, 0.25)' : 'rgba(255, 255, 255, 0.92)',
            overflow: 'hidden',
          },
        ]}
      >
        <BlurView
          intensity={Platform.OS === 'ios' ? 85 : 95}
          tint={
            Platform.OS === 'ios'
              ? isDark
                ? 'systemUltraThinMaterialDark'
                : 'systemUltraThinMaterialLight'
              : isDark
              ? 'dark'
              : 'light'
          }
          style={StyleSheet.absoluteFill}
          pointerEvents="none"
        />
        <LinearGradient
          colors={
            isDark
              ? ['rgba(255, 255, 255, 0.25)', 'rgba(255, 255, 255, 0.04)', 'transparent']
              : ['rgba(255, 255, 255, 0.85)', 'rgba(255, 255, 255, 0.20)', 'transparent']
          }
          start={{ x: 0, y: 0 }}
          end={{ x: 0, y: 1 }}
          style={StyleSheet.absoluteFill}
          pointerEvents="none"
        />
        {/* Assist Actions Row (Dica e Gabarito reposicionados no rodapé) */}
        <View style={styles.bottomAssistRow}>
          <TouchableOpacity
            style={[
              styles.assistBtn,
              tipsUsed >= MAX_TIPS
                ? [
                    styles.assistBtnMaxed,
                    {
                      backgroundColor: isDark
                        ? 'rgba(255, 255, 255, 0.04)'
                        : 'rgba(0, 0, 0, 0.04)',
                      borderColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.10)',
                    },
                  ]
                : {
                    backgroundColor: isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(255, 255, 255, 0.70)',
                    borderColor: isDark ? 'rgba(251, 191, 36, 0.40)' : '#F59E0B',
                  },
            ]}
            onPress={handleOpenTip}
            activeOpacity={0.75}
            accessibilityRole="button"
            accessibilityLabel={
              tipsUsed >= MAX_TIPS
                ? 'Todas as dicas foram consultadas'
                : `Obter dica progressiva (${tipsUsed}/${MAX_TIPS})`
            }
          >
            <Text
              style={[
                styles.assistBtnText,
                {
                  color:
                    tipsUsed >= MAX_TIPS
                      ? (isDark ? '#64748B' : '#475569')
                      : isDark
                      ? '#fbbf24'
                      : '#B45309',
                },
              ]}
            >
              💡 DICA
            </Text>
            <View
              style={[
                styles.assistPillBadge,
                {
                  backgroundColor: tipsUsed >= MAX_TIPS
                    ? 'rgba(100, 116, 139, 0.15)'
                    : isDark ? 'rgba(251, 191, 36, 0.16)' : 'rgba(180, 83, 9, 0.12)',
                },
              ]}
            >
              <Text
                style={[
                  styles.assistPillBadgeText,
                  {
                    color: tipsUsed >= MAX_TIPS
                      ? (isDark ? '#64748B' : '#475569')
                      : isDark
                      ? '#fbbf24'
                      : '#B45309',
                  },
                ]}
              >
                {tipsUsed}/{MAX_TIPS}
              </Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.assistBtn,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(255, 255, 255, 0.70)',
                borderColor: isDark ? 'rgba(251, 113, 133, 0.40)' : '#BE123C',
              },
            ]}
            onPress={handleRevealSolution}
            activeOpacity={0.75}
            accessibilityRole="button"
            accessibilityLabel="Revelar gabarito oficial do comando"
          >
            <Text
              style={[
                styles.assistBtnText,
                { color: isDark ? '#fb7185' : '#BE123C' },
              ]}
            >
              👁️ GABARITO
            </Text>
            <View
              style={[
                styles.assistPillBadge,
                {
                  backgroundColor: isDark ? 'rgba(251, 113, 133, 0.15)' : 'rgba(190, 18, 60, 0.12)',
                },
              ]}
            >
              <Text
                style={[
                  styles.assistPillBadgeText,
                  { color: isDark ? '#fb7185' : '#BE123C' },
                ]}
              >
                0 XP
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Primary CTA Button: Lilac #9E85FF */}
        <TouchableOpacity
          style={[
            styles.verifyBtn,
            (placedChips.length > 0 || solutionUsed)
              ? styles.verifyBtnReady
              : [
                  styles.verifyBtnDisabled,
                  {
                    backgroundColor: isDark ? '#1E243E' : '#e2e8f0',
                    borderColor: isDark ? '#272E4F' : 'rgba(0, 0, 0, 0.08)',
                  },
                ],
          ]}
          onPress={solutionUsed ? onNextMission : handleVerify}
          disabled={placedChips.length === 0 && !solutionUsed}
          activeOpacity={0.85}
        >
          <Text
            style={[
              styles.verifyBtnText,
              (placedChips.length > 0 || solutionUsed)
                ? styles.verifyBtnTextReady
                : { color: isDark ? '#94A3B8' : '#475569' },
            ]}
          >
            {solutionUsed
              ? 'CONTINUAR PARA PRÓXIMA ETAPA ➔'
              : placedChips.length > 0
              ? 'VERIFICAR RESPOSTA ↵'
              : 'toque nos blocos para montar'}
          </Text>
        </TouchableOpacity>

        {/* Clear Pause & Exit Options (Always Accessible) */}
        <View style={styles.bottomSecondaryRow}>
          <TouchableOpacity
            style={[
              styles.bottomSecondaryBtn,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.05)',
                borderColor: isDark ? 'rgba(251, 191, 36, 0.35)' : 'rgba(180, 83, 9, 0.30)',
              },
            ]}
            onPress={handlePause}
            activeOpacity={0.7}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <Text style={[styles.bottomSecondaryText, { color: isDark ? '#fbbf24' : '#B45309' }]}>
              ⏸ Pausar Trilha
            </Text>
          </TouchableOpacity>

          <Text style={[styles.bottomDividerText, { color: isDark ? '#334155' : '#cbd5e1' }]}>•</Text>

          <TouchableOpacity
            style={[
              styles.bottomSecondaryBtn,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.05)',
                borderColor: isDark ? 'rgba(0, 242, 254, 0.35)' : 'rgba(3, 105, 161, 0.30)',
              },
            ]}
            onPress={handleExitToHome}
            activeOpacity={0.7}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <Text style={[styles.bottomSecondaryText, { color: isDark ? '#00f2fe' : '#0369A1' }]}>
              🏠 Voltar ao Início
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 6. Terminal Hint Modal */}
      <Modal
        visible={tipModalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setTipModalVisible(false)}
      >
        <View style={styles.tipModalOverlay}>
          <View
            style={[
              styles.tipModalCard,
              {
                backgroundColor: colors.terminalWindowBg,
                borderColor: hasMoreTips
                  ? (isDark ? '#fbbf24' : '#d97706')
                  : (isDark ? '#ef4444' : '#dc2626'),
              },
            ]}
          >
            <View style={[styles.tipCardHeader, { borderBottomColor: colors.border }]}>
              <Text
                style={[
                  styles.tipCardTitle,
                  {
                    color: hasMoreTips
                      ? (isDark ? '#fbbf24' : '#d97706')
                      : (isDark ? '#ef4444' : '#dc2626'),
                  },
                ]}
              >
                {hasMoreTips
                  ? `[!] ~/devopshero/hint_${currentTipNumber}_de_${MAX_TIPS}.txt`
                  : '[X] ~/devopshero/no_more_hints.txt'}
              </Text>
            </View>

            <Text style={[styles.tipModalBody, { color: colors.textMain }]}>
              # {currentTipText}
            </Text>

            {hasMoreTips ? (
              <View style={[styles.tipPenaltyBox, { borderColor: isDark ? '#fbbf24' : '#d97706' }]}>
                <Text style={[styles.tipPenaltyText, { color: isDark ? '#fbbf24' : '#d97706' }]}>
                  ⚠️ <Text style={{ fontWeight: '800' }}>REGRA DE DEDUÇÃO CLI</Text>: Dica {currentTipNumber} de {MAX_TIPS} consultada. Pontuação desta missão reduzida para{' '}
                  <Text style={{ fontWeight: '800' }}>
                    {currentTipNumber === 1 ? '40% (-60%)' : currentTipNumber === 2 ? '20% (-80%)' : '10% (-90%)'}
                  </Text>{' '}
                  do XP base.
                </Text>
              </View>
            ) : (
              <View
                style={[
                  styles.tipPenaltyBox,
                  {
                    backgroundColor: isDark ? 'rgba(239, 68, 68, 0.10)' : 'rgba(220, 38, 38, 0.08)',
                    borderColor: isDark ? '#ef4444' : '#dc2626',
                  },
                ]}
              >
                <Text style={[styles.tipPenaltyText, { color: isDark ? '#f87171' : '#b91c1c' }]}>
                  🛑 <Text style={{ fontWeight: '800' }}>FIM DAS DICAS</Text>: Não há mais dicas disponíveis para esta missão. Todas as {MAX_TIPS} orientações já foram fornecidas.
                </Text>
              </View>
            )}

            <TouchableOpacity
              style={[
                styles.tipModalBtn,
                {
                  backgroundColor: hasMoreTips
                    ? (isDark ? '#00f2fe' : '#0284c7')
                    : (isDark ? '#475569' : '#64748b'),
                },
              ]}
              onPress={() => setTipModalVisible(false)}
              activeOpacity={0.85}
            >
              <Text
                style={[
                  styles.tipModalBtnText,
                  {
                    color: isDark
                      ? (hasMoreTips ? '#0B0F19' : '#FFFFFF')
                      : '#FFFFFF',
                  },
                ]}
              >
                {hasMoreTips ? 'Entendido, continuar' : 'Voltar ao terminal'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* 7. Feedback Evaluation Window (Bottom Sheet Modal) */}
      <Modal
        visible={sheetVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setSheetVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View
            style={[
              styles.sheetContainer,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.72)',
                borderColor: isDark ? 'rgba(255, 255, 255, 0.28)' : 'rgba(255, 255, 255, 0.95)',
                overflow: 'hidden',
                position: 'relative',
              },
            ]}
          >
            {/* Real Apple Frosted Glass Backdrop */}
            <BlurView
              intensity={Platform.OS === 'ios' ? 85 : 95}
              tint={
                Platform.OS === 'ios'
                  ? isDark
                    ? 'systemUltraThinMaterialDark'
                    : 'systemUltraThinMaterialLight'
                  : isDark
                  ? 'dark'
                  : 'light'
              }
              style={StyleSheet.absoluteFill}
              pointerEvents="none"
            />

            {/* Specular Liquid Glass Sheen */}
            <LinearGradient
              colors={
                isDark
                  ? ['rgba(255, 255, 255, 0.22)', 'rgba(255, 255, 255, 0.05)', 'transparent']
                  : ['rgba(255, 255, 255, 0.85)', 'rgba(255, 255, 255, 0.30)', 'transparent']
              }
              start={{ x: 0, y: 0 }}
              end={{ x: 0.85, y: 0.85 }}
              style={StyleSheet.absoluteFill}
              pointerEvents="none"
            />

            {/* Chromatic Dispersion Bevel on Top Rim */}
            <LinearGradient
              colors={
                isDark
                  ? [
                      'rgba(158, 133, 255, 0.35)',
                      'rgba(0, 242, 254, 0.25)',
                      'rgba(255, 255, 255, 0.40)',
                      'rgba(0, 223, 137, 0.25)',
                      'transparent',
                    ]
                  : [
                      'rgba(158, 133, 255, 0.25)',
                      'rgba(0, 242, 254, 0.18)',
                      'rgba(255, 255, 255, 0.70)',
                      'rgba(0, 223, 137, 0.18)',
                      'transparent',
                    ]
              }
              start={{ x: 0.05, y: 0.0 }}
              end={{ x: 0.95, y: 0.0 }}
              style={styles.sheetChromaticBevel}
              pointerEvents="none"
            />

            {/* Sheet Drag Handle */}
            <View style={styles.sheetHandle} />

            <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 16 }}>
              {/* Header Pill Tag: 'Almost there..' / 'Excelente!' / 'Gabarito Oficial' */}
              <View style={styles.headerPillRow}>
                <View
                  style={[
                    styles.headerPillTag,
                    {
                      backgroundColor: solutionUsed
                        ? 'rgba(251, 191, 36, 0.16)'
                        : isCorrect
                        ? 'rgba(0, 223, 137, 0.16)'
                        : 'rgba(251, 113, 133, 0.16)',
                      borderColor: solutionUsed
                        ? 'rgba(251, 191, 36, 0.35)'
                        : isCorrect
                        ? 'rgba(0, 223, 137, 0.35)'
                        : 'rgba(251, 113, 133, 0.35)',
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.headerPillTagText,
                      {
                        color: solutionUsed
                          ? '#fbbf24'
                          : isCorrect
                          ? '#00df89'
                          : '#fb7185',
                      },
                    ]}
                  >
                    {solutionUsed ? 'Gabarito Oficial' : isCorrect ? 'Excelente!' : 'Almost there..'}
                  </Text>
                </View>
              </View>

              {/* Main Mascot & Speech Bubble Row */}
              <View style={styles.mascotAndBubbleRow}>
                {/* Left: Retro CRT Terminal Mascot */}
                <TerminalMascot
                  isCorrect={isCorrect}
                  solutionUsed={solutionUsed}
                  isDark={isDark}
                />

                {/* Right: Speech Guidance Bubble */}
                <View
                  style={[
                    styles.speechBubbleCard,
                    {
                      backgroundColor: isDark ? '#272e4f' : '#e2e8f0',
                      borderColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.speechBubbleText,
                      { color: isDark ? '#ffffff' : '#0f172a' },
                    ]}
                  >
                    {isCorrect
                      ? solutionUsed
                        ? 'Você consultou a solução oficial desta missão. Revise a sintaxe abaixo para fixar o aprendizado.'
                        : 'Comando validado e executado com sucesso no container!'
                      : mission.tip || 'A ordem dos parâmetros ou argumentos precisa de ajuste no terminal.'}
                  </Text>

                  {/* Sub Action Button: '✨ GET HELP' */}
                  {!isCorrect && (
                    <TouchableOpacity
                      style={[
                        styles.bubbleHelpBtn,
                        {
                          backgroundColor: isDark ? 'rgba(255, 255, 255, 0.14)' : '#272E4F',
                          borderColor: isDark ? 'rgba(255, 255, 255, 0.22)' : '#1E243E',
                        },
                      ]}
                      onPress={handleOpenTip}
                      activeOpacity={0.75}
                      accessibilityRole="button"
                      accessibilityLabel="Obter ajuda ou dica"
                    >
                      <Text style={[styles.bubbleHelpBtnText, { color: '#ffffff' }]}>
                        ✨ {tipsUsed >= MAX_TIPS ? 'DICAS ESGOTADAS' : 'GET HELP'}
                      </Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>

              {/* Solution Code Box (on success or gabarito) */}
              {(isCorrect || solutionUsed) && (
                <View
                  style={[
                    styles.solutionRevealCard,
                    {
                      backgroundColor: isDark ? '#141829' : '#f1f5f9',
                      borderColor: solutionUsed ? '#fbbf24' : '#00df89',
                    },
                  ]}
                >
                  <View style={[styles.solutionCardHeader, { borderBottomColor: colors.border }]}>
                    <Text
                      style={[
                        styles.solutionCardLabel,
                        { color: solutionUsed ? '#fbbf24' : '#00df89' },
                      ]}
                    >
                      {solutionUsed ? '📖 GABARITO OFICIAL' : '✓ COMANDO EXECUTADO COM SUCESSO'}
                    </Text>
                  </View>

                  <View
                    style={[
                      styles.solutionTerminalBox,
                      {
                        backgroundColor: isDark ? '#0b0f19' : '#ffffff',
                        borderColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.1)',
                      },
                    ]}
                  >
                    <Text style={[styles.solutionPromptSymbol, { color: isDark ? '#00f2fe' : '#0284c7' }]}>
                      ${' '}
                    </Text>
                    <Text
                      style={[
                        styles.solutionCommandCode,
                        { color: isDark ? '#00df89' : '#16a34a' },
                      ]}
                      selectable
                    >
                      {mission.solution}
                    </Text>
                  </View>

                  {solutionUsed && (
                    <View
                      style={[
                        styles.penaltyNoticeBox,
                        {
                          backgroundColor: isDark ? 'rgba(251, 113, 133, 0.12)' : 'rgba(225, 29, 72, 0.08)',
                          borderColor: isDark ? '#fb7185' : '#e11d48',
                        },
                      ]}
                    >
                      <Text style={[styles.penaltyNoticeText, { color: isDark ? '#fb7185' : '#e11d48' }]}>
                        ⚠️ <Text style={{ fontWeight: '800' }}>Penalidade</Text>: Por revelar o gabarito oficial, nenhum XP foi somado (0 XP) e a ofensiva diária foi reiniciada.
                      </Text>
                    </View>
                  )}
                </View>
              )}

              {/* XP Score & Streak Audit Card */}
              {isCorrect && !solutionUsed && lastAward && (
                <View
                  style={[
                    styles.scoreAuditCard,
                    {
                      backgroundColor: isDark ? '#272e4f' : '#e2e8f0',
                      borderColor: 'rgba(0, 223, 137, 0.35)',
                    },
                  ]}
                >
                  <View style={[styles.xpEarnedHeader, { borderBottomColor: 'rgba(255, 255, 255, 0.08)' }]}>
                    <Text style={[styles.xpEarnedNumber, { color: '#00df89' }]}>
                      +{lastAward.xp} XP
                    </Text>
                    <View
                      style={[
                        styles.tierBadge,
                        { borderColor: '#fbbf24', backgroundColor: 'rgba(251, 191, 36, 0.16)' },
                      ]}
                    >
                      <Text style={[styles.xpTierTag, { color: '#fbbf24' }]}>
                        {lastAward.tierName}
                      </Text>
                    </View>
                  </View>

                  <View style={styles.auditRow}>
                    <Text style={[styles.auditKey, { color: colors.textCyan }]}>⏱️ TEMPO TOTAL:</Text>
                    <Text style={[styles.auditVal, { color: colors.textMain }]}>
                      {Math.round(lastAward.elapsedSeconds)}s
                    </Text>
                  </View>

                  <View style={[styles.auditRow, { borderBottomWidth: 0 }]}>
                    <Text style={[styles.auditKey, { color: colors.textCyan }]}>🔥 BÔNUS STREAK:</Text>
                    <Text style={[styles.auditVal, { color: '#00f2fe' }]}>
                      +{lastAward.streakBonusPct}%
                    </Text>
                  </View>
                </View>
              )}
            </ScrollView>

            {/* Bottom Full-Width Action Button: Lilac #9E85FF */}
            <TouchableOpacity
              style={[
                styles.sheetActionBtn,
                {
                  backgroundColor: '#9E85FF',
                  shadowColor: '#9E85FF',
                  shadowOffset: { width: 0, height: 4 },
                  shadowOpacity: 0.35,
                  shadowRadius: 10,
                  elevation: 6,
                },
              ]}
              onPress={handleSheetAction}
              activeOpacity={0.85}
            >
              <Text style={[styles.sheetActionBtnText, { color: '#0B0F19' }]}>
                {!isCorrect
                  ? '↺ TRY AGAIN'
                  : solutionUsed
                  ? 'AVANÇAR ETAPA ➔'
                  : 'CONTINUAR ➔'}
              </Text>
            </TouchableOpacity>

            {solutionUsed && (
              <TouchableOpacity
                style={styles.sheetSecondaryBtn}
                onPress={() => setSheetVisible(false)}
                activeOpacity={0.7}
              >
                <Text style={[styles.sheetSecondaryBtnText, { color: isDark ? '#00f2fe' : '#0369A1' }]}>
                  Revisar comando no terminal ⤺
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      </Modal>

      {/* 8. Pause Mission Modal (Apple HIG Inset Modal) */}
      <Modal
        visible={pauseModalVisible}
        transparent
        animationType="fade"
        onRequestClose={handleResume}
      >
        <View style={styles.pauseModalOverlay}>
          <View
            style={[
              styles.pauseModalCard,
              {
                backgroundColor: colors.terminalWindowBg,
                borderColor: isDark ? '#fbbf24' : '#d97706',
              },
            ]}
          >
            {/* Header */}
            <View style={[styles.pauseHeaderRow, { borderBottomColor: colors.border }]}>
              <View style={styles.pauseIconBadge}>
                <Text style={styles.pauseIconText}>⏸</Text>
              </View>
              <View style={styles.pauseTitleCol}>
                <Text style={[styles.pauseModalTitle, { color: colors.textMain }]}>
                  Trilha Pausada
                </Text>
                <Text style={[styles.pauseModalSubtitle, { color: colors.textMuted }]}>
                  {track.name} · Missão {missionIndex + 1}/{track.missions.length}
                </Text>
              </View>
            </View>

            {/* Mission Info Box */}
            <View
              style={[
                styles.pauseMissionBox,
                {
                  backgroundColor: colors.cardSubtle,
                  borderColor: colors.border,
                },
              ]}
            >
              <Text style={[styles.pauseMissionName, { color: colors.textMain }]} numberOfLines={2}>
                {mission.title}
              </Text>
              <View style={styles.pauseStatsRow}>
                <Text style={[styles.pauseStatItem, { color: isDark ? '#00ff87' : '#16a34a' }]}>
                  ⏱️ Tempo: {secondsElapsed}s (pausado)
                </Text>
                <Text style={[styles.pauseStatItem, { color: colors.textCyan }]}>
                  ⭐ {xp} XP
                </Text>
              </View>
            </View>

            {/* Action 1: Resume (Primary CTA) */}
            <TouchableOpacity
              style={[
                styles.pauseResumeBtn,
                { backgroundColor: isDark ? '#00ff87' : '#16a34a' },
              ]}
              onPress={handleResume}
              activeOpacity={0.85}
            >
              <Text
                style={[
                  styles.pauseResumeBtnText,
                  { color: isDark ? '#06070a' : '#FFFFFF' },
                ]}
              >
                ▶ Continuar Prática
              </Text>
            </TouchableOpacity>

            {/* Action 2: Go to Home */}
            <TouchableOpacity
              style={[
                styles.pauseSecondaryBtn,
                {
                  backgroundColor: colors.cardSubtle,
                  borderColor: colors.border,
                },
              ]}
              onPress={handleExitToHome}
              activeOpacity={0.75}
            >
              <Text style={[styles.pauseSecondaryBtnText, { color: colors.textMain }]}>
                🏠 Voltar para a Tela Inicial
              </Text>
            </TouchableOpacity>

            {/* Action 3: Switch Track */}
            {onGoToTracks && (
              <TouchableOpacity
                style={[
                  styles.pauseTertiaryBtn,
                  {
                    backgroundColor: 'transparent',
                    borderColor: colors.border,
                  },
                ]}
                onPress={handleExitToTracks}
                activeOpacity={0.7}
              >
                <Text style={[styles.pauseTertiaryBtnText, { color: isDark ? '#00f2fe' : '#0369A1' }]}>
                  📚 Trocar de Trilha
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 210,
  },
  pinnedNavHeader: {
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 6,
    borderBottomWidth: StyleSheet.hairlineWidth,
    zIndex: 10,
  },
  practiceNavRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 44, // Apple HIG standard navigation bar touch height
    marginBottom: 6,
  },
  navBackBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingRight: 6,
    minHeight: 44,
    flexShrink: 0,
  },
  navBackIcon: {
    fontSize: 24,
    fontWeight: '700',
    marginRight: 2,
    lineHeight: 26,
  },
  navBackText: {
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: -0.2,
  },
  navTitleCenter: {
    flex: 1,
    paddingHorizontal: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  navTrackTitle: {
    fontSize: 15,
    fontWeight: '800',
    textAlign: 'center',
  },
  navMissionStep: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 1,
    textAlign: 'center',
  },
  navRightActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    flexShrink: 0,
  },
  pauseHeaderBtn: {
    borderRadius: 8,
    borderWidth: 1.2,
    paddingHorizontal: 10,
    paddingVertical: 6,
    minHeight: 36,
    minWidth: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pauseHeaderBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '800',
    textAlign: 'center',
  },
  hudBadge: {
    borderRadius: 8,
    borderWidth: 1.2,
    paddingHorizontal: 7,
    paddingVertical: 4,
    minHeight: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  hudBadgeText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '800',
    textAlign: 'center',
  },
  progressTrack: {
    height: 4,
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  terminalCard: {
    borderRadius: 18,
    borderWidth: 1.2,
    overflow: 'hidden',
    marginBottom: 14,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderBottomWidth: 1,
    flexWrap: 'wrap',
    gap: 8,
  },
  trackInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flexShrink: 1,
  },
  trackIconText: {
    fontSize: 20,
  },
  trackNameText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '800',
  },
  briefingBadge: {
    borderRadius: 8,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  briefingBadgeText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '800',
  },
  bottomAssistRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 10,
  },
  assistBtn: {
    flex: 1,
    borderRadius: 14,
    borderWidth: 1.2,
    paddingVertical: 10,
    paddingHorizontal: 12,
    minHeight: 46, // Apple HIG touch target
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  assistBtnMaxed: {
    opacity: 0.65,
    borderStyle: 'dashed',
  },
  assistBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '900',
    letterSpacing: 0.5,
    textAlign: 'center',
  },
  assistPillBadge: {
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  assistPillBadgeText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11,
    fontWeight: '800',
  },
  briefingBody: {
    padding: 16,
  },
  missionTitle: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 20,
    fontWeight: '800',
    lineHeight: 26,
    marginBottom: 8,
  },
  missionObjective: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    lineHeight: 23,
  },
  // Code Editor Window (Lines 1 & 2 with Syntax Highlighting)
  codeEditorWrapper: {
    marginBottom: 18,
    width: '100%',
  },
  codeEditorInterior: {
    padding: 16,
  },
  wordBankWrapper: {
    marginBottom: 20,
    width: '100%',
  },
  wordBankInterior: {
    padding: 16,
  },
  codeEditorWindow: {
    borderRadius: 16,
    borderWidth: 1.2,
    padding: 14,
    marginBottom: 18,
  },
  editorTabBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 10,
  },
  editorWindowDots: {
    flexDirection: 'row',
    gap: 6,
    alignItems: 'center',
  },
  windowDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  editorTabFilename: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '800',
    flexShrink: 1,
    marginHorizontal: 8,
  },
  editorXpBadge: {
    backgroundColor: 'rgba(0, 242, 254, 0.12)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: 'rgba(0, 242, 254, 0.3)',
  },
  editorXpText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11,
    fontWeight: '800',
    color: '#00F2FE',
  },
  editorDivider: {
    height: 1,
    marginBottom: 12,
  },
  codeLineRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  codeLineNumber: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '700',
    width: 18,
    textAlign: 'right',
  },
  codeCommentLine: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    lineHeight: 20,
    fontStyle: 'italic',
    flex: 1,
  },
  promptAndSlotContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  codePromptDollar: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    fontWeight: '900',
    color: '#00df89',
    marginTop: 0,
    lineHeight: 18,
  },
  slotReceptacle: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    alignItems: 'center',
    minHeight: 40,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1.2,
  },
  slotReceptacleEmpty: {
    borderStyle: 'dashed',
    justifyContent: 'center',
  },
  slotReceptacleFilled: {
    borderStyle: 'solid',
  },
  slotPlaceholderText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12.5,
    fontStyle: 'italic',
    paddingVertical: 2,
    textAlign: 'center',
  },
  syntaxPlacedToken: {
    borderWidth: 1.2,
    paddingHorizontal: 9,
    paddingVertical: 4.5,
    minHeight: 28,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 1,
  },
  syntaxPlacedTokenText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '800',
  },

  // Retro CRT Terminal Mascot
  mascotContainer: {
    alignItems: 'center',
    width: 64,
  },
  mascotBody: {
    width: 58,
    height: 48,
    borderRadius: 12,
    padding: 6,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 3,
    position: 'relative',
  },
  mascotScreen: {
    width: 44,
    height: 34,
    borderRadius: 8,
    backgroundColor: '#0b0f19',
    alignItems: 'center',
    justifyContent: 'center',
  },
  mascotScreenCross: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 18,
    fontWeight: '900',
    color: '#fb7185',
  },
  mascotEyesRow: {
    flexDirection: 'row',
    gap: 6,
  },
  mascotDotEye: {
    width: 5,
    height: 5,
    borderRadius: 2.5,
    backgroundColor: '#fbbf24',
  },
  mascotScreenCheck: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 18,
    fontWeight: '900',
    color: '#00df89',
  },
  mascotLed: {
    position: 'absolute',
    bottom: 3,
    right: 5,
    width: 4,
    height: 4,
    borderRadius: 2,
  },
  mascotFeetRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 2,
  },
  mascotFoot: {
    width: 14,
    height: 5,
    borderRadius: 2.5,
    backgroundColor: '#94a3b8',
  },

  // Sheet Header Tag & Mascot + Bubble Row
  headerPillRow: {
    flexDirection: 'row',
    marginBottom: 14,
  },
  headerPillTag: {
    borderRadius: 12,
    borderWidth: 1.2,
    paddingHorizontal: 14,
    paddingVertical: 6,
    alignSelf: 'flex-start',
  },
  headerPillTagText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 15,
    fontWeight: '800',
  },
  mascotAndBubbleRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 16,
  },
  speechBubbleCard: {
    flex: 1,
    borderRadius: 16,
    borderWidth: 1,
    padding: 14,
  },
  speechBubbleText: {
    fontSize: 14,
    fontWeight: '600',
    lineHeight: 20,
    marginBottom: 10,
  },
  bubbleHelpBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.18)',
    minHeight: 32,
  },
  bubbleHelpBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '800',
    color: '#ffffff',
  },
  terminalWindow: {
    borderRadius: 18,
    borderWidth: 1.2,
    overflow: 'hidden',
    marginBottom: 18,
  },
  terminalHeader: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderBottomWidth: 1,
  },
  terminalFilename: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '800',
  },
  terminalBody: {
    padding: 16,
  },
  codeComment: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    lineHeight: 20,
    fontStyle: 'italic',
    marginBottom: 12,
  },
  commandRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
  },
  wordBankTray: {
    borderRadius: 18,
    borderWidth: 1.2,
    paddingHorizontal: 14,
    paddingVertical: 14,
    marginTop: 14,
    marginBottom: 16,
  },
  wordBankHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 2,
  },
  wordBankBadge: {
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  wordBankBadgeText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11,
    fontWeight: '800',
    color: '#9E85FF',
    letterSpacing: 0.5,
  },
  wordBankHintText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11.5,
    fontStyle: 'italic',
  },
  wordBankDivider: {
    height: 1,
    marginVertical: 10,
  },
  chipsPool: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    justifyContent: 'center',
  },
  poolChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    minHeight: 40,
    borderRadius: 10,
    borderWidth: 1.5,
    maxWidth: '100%',
    alignItems: 'center',
    justifyContent: 'center',
  },
  poolChipDisabled: {
    borderStyle: 'dashed',
    opacity: 0.35,
  },
  poolChipText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13.5,
    fontWeight: '800',
    textAlign: 'center',
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 16,
    paddingBottom: Math.max(CURRENT_DEVICE.insets.bottom, 16) + 8,
    paddingTop: 10,
    borderTopWidth: StyleSheet.hairlineWidth,
  },
  verifyBtn: {
    borderRadius: 16,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56,
  },
  verifyBtnReady: {
    backgroundColor: '#9E85FF',
    shadowColor: '#9E85FF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.38,
    shadowRadius: 12,
    elevation: 6,
  },
  verifyBtnDisabled: {
    borderWidth: 1.2,
  },
  verifyBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 15,
    fontWeight: '900',
    letterSpacing: 0.5,
    textAlign: 'center',
    alignSelf: 'center',
  },
  verifyBtnTextReady: {
    color: '#0B0F19',
    fontWeight: '900',
  },
  bottomSecondaryRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
    marginTop: 10,
  },
  bottomSecondaryBtn: {
    paddingVertical: 7,
    paddingHorizontal: 14,
    borderRadius: 10,
    borderWidth: 1,
    minHeight: 38,
    alignItems: 'center',
    justifyContent: 'center',
  },
  bottomSecondaryText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '800',
    textAlign: 'center',
  },
  bottomDividerText: {
    fontSize: 14,
    fontWeight: '700',
  },
  tipModalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    padding: 20,
  },
  tipModalCard: {
    width: '100%',
    maxWidth: 380,
    borderRadius: 20,
    borderWidth: 1.5,
    padding: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.5,
    shadowRadius: 24,
    elevation: 12,
  },
  tipCardHeader: {
    paddingBottom: 8,
    borderBottomWidth: StyleSheet.hairlineWidth,
    marginBottom: 12,
  },
  tipCardTitle: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    fontWeight: '900',
  },
  tipModalBody: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 16,
  },
  tipPenaltyBox: {
    backgroundColor: 'rgba(251, 191, 36, 0.08)',
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 16,
  },
  tipPenaltyText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    lineHeight: 20,
  },
  tipModalBtn: {
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
    width: '100%',
  },
  tipModalBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    fontWeight: '900',
    color: '#06070a',
    textAlign: 'center',
    alignSelf: 'center',
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0, 0, 0, 0.65)',
  },
  sheetContainer: {
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    borderWidth: 1.5,
    padding: 18,
    paddingBottom: Math.max(CURRENT_DEVICE.insets.bottom, 24) + 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -12 },
    shadowOpacity: 0.45,
    shadowRadius: 24,
    elevation: 16,
  },
  sheetHandle: {
    width: 44,
    height: 5,
    borderRadius: 2.5,
    backgroundColor: '#94a3b8',
    opacity: 0.4,
    alignSelf: 'center',
    marginBottom: 14,
  },
  sheetChromaticBevel: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 1.5,
  },
  sheetHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sheetTitle: {
    fontSize: 18,
    fontWeight: '800',
    flexShrink: 1,
  },
  sheetStatusBadge: {
    borderWidth: 1.2,
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  sheetStatusTag: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '900',
  },
  statusBanner: {
    width: '100%',
    borderRadius: 18,
    borderWidth: 1.5,
    paddingVertical: 18,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 10,
  },
  statusBannerText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 32,
    fontWeight: '900',
    letterSpacing: 3,
    marginBottom: 4,
  },
  statusBannerSub: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  scoreAuditCard: {
    width: '100%',
    borderRadius: 16,
    borderWidth: 1.2,
    padding: 14,
    marginTop: 8,
    marginBottom: 16,
  },
  solutionRevealCard: {
    width: '100%',
    borderRadius: 16,
    borderWidth: 1.5,
    padding: 14,
    marginTop: 8,
    marginBottom: 14,
  },
  solutionCardHeader: {
    paddingBottom: 8,
    borderBottomWidth: StyleSheet.hairlineWidth,
    marginBottom: 10,
  },
  solutionCardLabel: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  solutionTerminalBox: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    marginBottom: 10,
  },
  solutionPromptSymbol: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 18,
    fontWeight: '900',
  },
  solutionCommandCode: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    fontWeight: '800',
    flex: 1,
  },
  solutionContextBox: {
    marginBottom: 8,
  },
  solutionContextTitle: {
    fontSize: 13,
    fontWeight: '800',
    marginBottom: 4,
  },
  solutionContextText: {
    fontSize: 14,
    lineHeight: 20,
  },
  penaltyNoticeBox: {
    borderRadius: 10,
    borderWidth: 1,
    padding: 10,
    marginTop: 6,
  },
  penaltyNoticeText: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '600',
  },
  sheetSecondaryBtn: {
    width: '100%',
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  sheetSecondaryBtnText: {
    fontSize: 15,
    fontWeight: '700',
    textAlign: 'center',
  },
  xpEarnedHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    paddingBottom: 8,
    borderBottomWidth: StyleSheet.hairlineWidth,
    flexWrap: 'wrap',
    gap: 6,
  },
  xpEarnedNumber: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 32,
    fontWeight: '900',
  },
  tierBadge: {
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  xpTierTag: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '800',
  },
  auditRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: 'rgba(255, 255, 255, 0.06)',
    flexWrap: 'wrap',
    gap: 6,
  },
  auditKey: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 15,
    fontWeight: '800',
    flexShrink: 0,
  },
  auditVal: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 15,
    fontWeight: '700',
    flexShrink: 1,
    textAlign: 'right',
  },
  messageCard: {
    width: '100%',
    borderRadius: 16,
    borderWidth: 1.2,
    padding: 14,
    marginTop: 8,
    marginBottom: 16,
  },
  errorHeader: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    fontWeight: '900',
    marginBottom: 6,
  },
  messageText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 15,
    lineHeight: 22,
  },
  sheetActionBtn: {
    width: '100%',
    borderRadius: 16,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56, // Apple HIG touch target
  },
  sheetActionBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 17,
    fontWeight: '900',
    letterSpacing: 0.5,
    textAlign: 'center',
    alignSelf: 'center',
  },
  pauseModalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.78)',
    padding: 20,
  },
  pauseModalCard: {
    width: '100%',
    maxWidth: 380,
    borderRadius: 24,
    borderWidth: 1.5,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 14 },
    shadowOpacity: 0.5,
    shadowRadius: 28,
    elevation: 14,
  },
  pauseHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingBottom: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    marginBottom: 16,
  },
  pauseIconBadge: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: 'rgba(251, 191, 36, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  pauseIconText: {
    fontSize: 22,
  },
  pauseTitleCol: {
    flex: 1,
  },
  pauseModalTitle: {
    fontSize: 20,
    fontWeight: '900',
    letterSpacing: -0.3,
  },
  pauseModalSubtitle: {
    fontSize: 13,
    fontWeight: '600',
    marginTop: 2,
  },
  pauseMissionBox: {
    borderWidth: 1,
    borderRadius: 14,
    padding: 14,
    marginBottom: 18,
  },
  pauseMissionName: {
    fontSize: 16,
    fontWeight: '700',
    lineHeight: 22,
    marginBottom: 8,
  },
  pauseStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  pauseStatItem: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '800',
  },
  pauseResumeBtn: {
    width: '100%',
    borderRadius: 16,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
    marginBottom: 10,
    shadowColor: '#00ff87',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 10,
    elevation: 6,
  },
  pauseResumeBtnText: {
    fontSize: 16,
    fontWeight: '900',
    color: '#06070a',
    letterSpacing: 0.3,
    textAlign: 'center',
    alignSelf: 'center',
  },
  pauseSecondaryBtn: {
    width: '100%',
    borderRadius: 14,
    borderWidth: 1.2,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
    marginBottom: 8,
  },
  pauseSecondaryBtnText: {
    fontSize: 15,
    fontWeight: '700',
    textAlign: 'center',
    alignSelf: 'center',
  },
  pauseTertiaryBtn: {
    width: '100%',
    borderRadius: 14,
    borderWidth: 1,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  pauseTertiaryBtnText: {
    fontSize: 14,
    fontWeight: '700',
    textAlign: 'center',
    alignSelf: 'center',
  },
});
