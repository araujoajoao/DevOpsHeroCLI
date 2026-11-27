import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  Platform,
  Alert,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { ThemeColors } from '../theme/colors';
import { Track } from '../types';
import { TrackIcon } from '../components/TrackIcon';
import { LiquidGlassView } from '../components/LiquidGlassView';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

interface TracksScreenProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  currentTrackIndex: number;
  onSelectTrack: (trackIndex: number) => void;
  onStartMission: (trackIndex: number, missionIndex: number) => void;
  onBackToHome: () => void;
  tracks: Track[];
  xp?: number;
  completedMissionIds?: Set<string>;
}

export const TracksScreen: React.FC<TracksScreenProps> = ({
  theme,
  onToggleTheme,
  currentTrackIndex,
  onSelectTrack,
  onStartMission,
  onBackToHome,
  tracks,
  xp = 0,
  completedMissionIds = new Set(),
}) => {
  const colors = ThemeColors[theme];
  const isDark = theme === 'dark';

  const [isSelectPathVisible, setIsSelectPathVisible] = useState(false);

  const activeTrack = tracks[currentTrackIndex] || tracks[0];
  const missions = activeTrack?.missions || [];

  const triggerHaptic = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
  };

  const triggerWarningHaptic = () => {
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    } catch (_) {}
  };

  const isTrackUnlocked = (track: Track) => {
    return (track.required_xp || 0) <= xp;
  };

  const isMissionUnlocked = (idx: number) => {
    if (!isTrackUnlocked(activeTrack)) return false;
    if (idx === 0) return true;
    const currMission = missions[idx];
    if (currMission && completedMissionIds.has(currMission.id)) return true;
    const prevMission = missions[idx - 1];
    return prevMission ? completedMissionIds.has(prevMission.id) : false;
  };

  const isMissionCompleted = (missionId: string) => {
    return completedMissionIds.has(missionId);
  };

  const completedCount = missions.filter(m => completedMissionIds.has(m.id)).length;
  const totalCount = missions.length > 0 ? missions.length : 10;
  const progressRatio = totalCount > 0 ? completedCount / totalCount : 0;

  const renderCareerPathCard = (track: Track, index: number) => {
    const isUnlocked = isTrackUnlocked(track);
    const isSelected = index === currentTrackIndex;
    const completed = track.missions.filter(m => completedMissionIds.has(m.id)).length;
    const total = track.missions.length || 10;
    const progressPercent = Math.min(Math.max((completed / total) * 100, 8), 100);

    return (
      <View key={track.id} style={styles.modalCardTouchable}>
        <LiquidGlassView
          onPress={() => {
            triggerHaptic();
            if (isUnlocked) {
              setIsSelectPathVisible(false);
              onSelectTrack(index);
            } else {
              triggerWarningHaptic();
              Alert.alert(
                'Trilha Bloqueada',
                `Esta trilha requer nível ${track.required_seniority || 'superior'} (${track.required_xp || 0} XP).`
              );
            }
          }}
          interactive={true}
          isSelected={isSelected}
          selectedBorderColor="#9E85FF"
          selectedGlowColor="#9E85FF"
          borderRadius={20}
          borderWidth={isSelected ? 2.2 : 1.2}
          borderColor={
            isSelected
              ? '#9E85FF'
              : 'rgba(255, 255, 255, 0.22)'
          }
          theme="dark"
          showSheen={true}
          intensity={40}
          contentStyle={styles.modalCardContent}
        >
          <View style={styles.modalCardBadgesRow}>
            <View style={styles.modalBadgeBox}>
              <TrackIcon
                trackId={track.id}
                size={20}
                badgeSize={34}
                showBadge={true}
              />
            </View>
          </View>

          <Text style={styles.modalCardTitle}>{track.name}</Text>

          <View style={styles.modalCardProgressHeader}>
            <Text style={styles.modalCardSectionLabel}>SECTION</Text>
            <Text style={styles.modalCardFractionLabel}>
              {completed}/{total}
            </Text>
          </View>

          <View style={styles.modalCardProgressBarBg}>
            <View
              style={[
                styles.modalCardProgressBarFill,
                { width: `${progressPercent}%`, backgroundColor: '#9E85FF' },
              ]}
            >
              <LinearGradient
                colors={['rgba(255, 255, 255, 0.40)', 'rgba(255, 255, 255, 0.0)']}
                start={{ x: 0, y: 0 }}
                end={{ x: 0, y: 1 }}
                style={StyleSheet.absoluteFill}
              />
            </View>
          </View>
        </LiquidGlassView>
      </View>
    );
  };

  return (
    <View
      style={[
        styles.root,
        {
          backgroundColor: 'transparent',
        },
      ]}
    >
      {/* 1. Header Row ('✕' Dismiss, 'DevOps Path' Centered, Theme Toggle) */}
      <View style={styles.topBar}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => {
            triggerHaptic();
            onBackToHome();
          }}
          activeOpacity={0.7}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          accessibilityLabel="Voltar para tela inicial"
        >
          <Text style={[styles.backIcon, { color: isDark ? '#A5B4FC' : '#475569' }]}>
            ✕
          </Text>
        </TouchableOpacity>

        <Text style={[styles.topBarTitle, { color: isDark ? '#D8E2FD' : '#1E293B' }]}>
          DevOps Path
        </Text>

        <TouchableOpacity
          style={styles.themeToggleBtn}
          onPress={() => {
            triggerHaptic();
            onToggleTheme();
          }}
          activeOpacity={0.7}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          accessibilityLabel="Alternar tema"
        >
          <Text style={styles.themeToggleIcon}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* 2. Track Title Row with '⇄' Switch Button */}
        <View style={styles.trackTitleRow}>
          <Text
            style={[
              styles.trackTitleText,
              { color: isDark ? '#FFFFFF' : '#0F172A' },
            ]}
            numberOfLines={2}
          >
            {activeTrack?.name || 'Full-Stack DevOps'}
          </Text>

          <TouchableOpacity
            style={styles.switchTrackBtn}
            onPress={() => {
              triggerHaptic();
              setIsSelectPathVisible(true);
            }}
            activeOpacity={0.75}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            accessibilityLabel="Alternar trilha"
          >
            <Text style={styles.switchTrackIcon}>⇄</Text>
          </TouchableOpacity>
        </View>

        {/* 3. Section Counter & Lilac Progress Bar */}
        <View style={styles.sectionRow}>
          <Text
            style={[
              styles.sectionLabel,
              { color: isDark ? '#94A3B8' : '#64748B' },
            ]}
          >
            SECTION
          </Text>
          <Text
            style={[
              styles.fractionLabel,
              { color: isDark ? '#94A3B8' : '#64748B' },
            ]}
          >
            {completedCount}/{totalCount}
          </Text>
        </View>

        <View
          style={[
            styles.progressBarTrack,
            { backgroundColor: isDark ? 'rgba(255, 255, 255, 0.10)' : 'rgba(0, 0, 0, 0.08)' },
          ]}
        >
          <View
            style={[
              styles.progressBarFill,
              {
                width: `${Math.max(progressRatio * 100, 6)}%`,
                backgroundColor: '#9E85FF',
              },
            ]}
          />
        </View>

        {/* 4. Questions / Missions Cards List (Fidelity to Reference Screenshot) */}
        <View style={styles.missionsList}>
          {missions.map((mission, idx) => {
            const unlocked = isMissionUnlocked(idx);
            const completed = isMissionCompleted(mission.id);

            return (
              <View key={mission.id} style={styles.missionCardTouchable}>
                <LiquidGlassView
                  onPress={() => {
                    triggerHaptic();
                    if (unlocked) {
                      onStartMission(currentTrackIndex, idx);
                    } else {
                      triggerWarningHaptic();
                      Alert.alert(
                        'Etapa Bloqueada',
                        `A missão "${mission.title}" requer a conclusão das etapas anteriores desta trilha.`
                      );
                    }
                  }}
                  interactive={true}
                  isSelected={false}
                  borderRadius={18}
                  borderWidth={1.2}
                  borderColor={
                    isDark
                      ? completed
                        ? 'rgba(0, 223, 137, 0.40)'
                        : unlocked
                        ? 'rgba(158, 133, 255, 0.35)'
                        : 'rgba(255, 255, 255, 0.16)'
                      : 'rgba(0, 0, 0, 0.08)'
                  }
                  theme={theme}
                  showSheen={true}
                  intensity={40}
                  contentStyle={styles.missionCardInner}
                >
                  {/* Mission Title on Left */}
                  <Text
                    style={[
                      styles.missionTitle,
                      {
                        color: unlocked
                          ? (isDark ? '#FFFFFF' : '#0F172A')
                          : (isDark ? '#94A3B8' : '#64748B'),
                      },
                    ]}
                    numberOfLines={2}
                  >
                    {mission.title}
                  </Text>

                  {/* Status Icon on Right (Lock, Checkmark, or Play) */}
                  <View style={styles.statusCol}>
                    {completed ? (
                      <View style={styles.completedBadge}>
                        <Text style={styles.completedIcon}>✓</Text>
                      </View>
                    ) : !unlocked ? (
                      <View
                        style={[
                          styles.lockBadge,
                          {
                            backgroundColor: isDark
                              ? 'rgba(255, 255, 255, 0.08)'
                              : 'rgba(0, 0, 0, 0.06)',
                            borderColor: isDark
                              ? 'rgba(255, 255, 255, 0.16)'
                              : 'rgba(0, 0, 0, 0.10)',
                          },
                        ]}
                      >
                        <Text style={styles.lockIcon}>🔒</Text>
                      </View>
                    ) : (
                      <View style={styles.playBadge}>
                        <Text style={styles.playIcon}>▶</Text>
                      </View>
                    )}
                  </View>
                </LiquidGlassView>
              </View>
            );
          })}
        </View>
      </ScrollView>

      {/* 5. Select Path Modal Bottom Sheet */}
      <Modal
        visible={isSelectPathVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setIsSelectPathVisible(false)}
      >
        <View style={styles.modalBackdrop}>
          <View
            style={[
              styles.modalSheet,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.75)',
                borderColor: isDark ? 'rgba(255, 255, 255, 0.28)' : 'rgba(255, 255, 255, 0.95)',
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
                  ? ['rgba(255, 255, 255, 0.25)', 'rgba(255, 255, 255, 0.04)', 'transparent']
                  : ['rgba(255, 255, 255, 0.85)', 'rgba(255, 255, 255, 0.20)', 'transparent']
              }
              start={{ x: 0, y: 0 }}
              end={{ x: 0.85, y: 0.85 }}
              style={StyleSheet.absoluteFill}
              pointerEvents="none"
            />
            <View style={styles.modalHeader}>
              <TouchableOpacity
                onPress={() => setIsSelectPathVisible(false)}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                style={styles.modalCloseBtn}
              >
                <Text style={[styles.modalCloseIcon, { color: isDark ? '#A5B4FC' : '#1E293B' }]}>✕</Text>
              </TouchableOpacity>

              <Text style={[styles.modalHeaderTitle, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>Select Path</Text>

              <View style={styles.modalHeaderSpacer} />
            </View>

            <Text style={[styles.modalSectionHeader, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>Career Paths</Text>

            <ScrollView
              style={styles.modalScrollView}
              contentContainerStyle={styles.modalScrollContent}
              showsVerticalScrollIndicator={false}
            >
              {tracks.map((track, idx) => (
                <View key={track.id} style={{ marginBottom: 16 }}>
                  {renderCareerPathCard(track, idx)}
                </View>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    height: 52,
    marginTop: Platform.OS === 'ios' ? 8 : 12,
  },
  backButton: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'flex-start',
  },
  backIcon: {
    fontSize: 20,
    fontWeight: '700',
  },
  topBarTitle: {
    fontSize: 17,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    textAlign: 'center',
  },
  themeToggleBtn: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'flex-end',
  },
  themeToggleIcon: {
    fontSize: 18,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 110,
  },
  trackTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  trackTitleText: {
    flex: 1,
    fontSize: 24,
    fontWeight: '800',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: -0.3,
  },
  switchTrackBtn: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12,
  },
  switchTrackIcon: {
    fontSize: 22,
    fontWeight: '700',
    color: '#9E85FF',
  },
  sectionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 18,
    marginBottom: 8,
  },
  sectionLabel: {
    fontSize: 12,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 0.5,
  },
  fractionLabel: {
    fontSize: 12,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  progressBarTrack: {
    height: 5,
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 20,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  missionsList: {
    gap: 14,
  },
  missionCardTouchable: {
    width: '100%',
  },
  missionCardInner: {
    minHeight: 68,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  missionCard: {
    minHeight: 68,
    borderRadius: 18,
    borderWidth: 1.2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  missionTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginRight: 16,
    lineHeight: 22,
  },
  statusCol: {
    width: 42,
    alignItems: 'center',
    justifyContent: 'center',
  },
  lockBadge: {
    width: 38,
    height: 38,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  lockIcon: {
    fontSize: 16,
  },
  completedBadge: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: 'rgba(0, 223, 137, 0.16)',
    borderWidth: 1,
    borderColor: 'rgba(0, 223, 137, 0.40)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  completedIcon: {
    fontSize: 18,
    fontWeight: '800',
    color: '#00DF89',
  },
  playBadge: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: 'rgba(158, 133, 255, 0.20)',
    borderWidth: 1,
    borderColor: 'rgba(158, 133, 255, 0.50)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  playIcon: {
    fontSize: 15,
    fontWeight: '800',
    color: '#9E85FF',
    marginLeft: 2,
  },

  // Modal Bottom Sheet
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    justifyContent: 'flex-end',
  },
  modalSheet: {
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    backgroundColor: 'rgba(19, 22, 39, 0.95)',
    borderWidth: 1.2,
    borderColor: 'rgba(255, 255, 255, 0.16)',
    maxHeight: '84%',
    paddingTop: 16,
    paddingBottom: 24,
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  modalCloseBtn: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalCloseIcon: {
    fontSize: 18,
    fontWeight: '700',
    color: '#A5B4FC',
  },
  modalHeaderTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  modalHeaderSpacer: {
    width: 44,
  },
  modalSectionHeader: {
    fontSize: 18,
    fontWeight: '800',
    color: '#FFFFFF',
    paddingHorizontal: 20,
    marginTop: 6,
    marginBottom: 16,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  modalScrollView: {
    paddingHorizontal: 20,
  },
  modalScrollContent: {
    paddingBottom: 20,
    gap: 14,
  },
  modalCardTouchable: {
    width: '100%',
  },
  modalCardContent: {
    padding: 18,
    gap: 10,
  },
  modalCard: {
    borderRadius: 18,
    borderWidth: 1.2,
    padding: 18,
  },
  modalBadgeBox: {
    padding: 2,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.18)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalCardBadgesRow: {
    flexDirection: 'row',
    gap: 6,
    marginBottom: 6,
  },
  modalCardBadge: {
    width: 26,
    height: 26,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalCardBadgeIcon: {
    fontSize: 14,
  },
  modalCardTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 12,
  },
  modalCardProgressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  modalCardSectionLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#A5B4FC',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  modalCardFractionLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#A5B4FC',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  modalCardProgressBarBg: {
    height: 5,
    borderRadius: 3,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    overflow: 'hidden',
  },
  modalCardProgressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
});
