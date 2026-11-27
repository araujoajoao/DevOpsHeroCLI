import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  FlatList,
  TouchableOpacity,
  Dimensions,
  Modal,
  Platform,
  Alert,
  NativeSyntheticEvent,
  NativeScrollEvent,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { ThemeColors } from '../theme/colors';
import { Track, Mission } from '../types';
import { TrackIcon } from '../components/TrackIcon';
import { LiquidGlassView } from '../components/LiquidGlassView';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const CARD_WIDTH = Math.min(SCREEN_WIDTH - 44, 400);
const CARD_SPACING = 12;

export interface HomeScreenProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  onSelectTrack: (trackIndex: number) => void;
  onStartMission: (trackIndex: number, missionIndex: number) => void;
  onViewAllTracks: () => void;
  onOpenProfile: () => void;
  currentTrack?: Track;
  currentMission?: Mission;
  currentTrackIndex?: number;
  currentMissionIndex?: number;
  tracks?: Track[];
  xp: number;
  streak?: number;
  userName?: string;
  userRole?: string;
  isGuest?: boolean;
  hasUpdate?: boolean;
  onOpenUpdateModal?: () => void;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({
  theme,
  onToggleTheme,
  onSelectTrack,
  onStartMission,
  onViewAllTracks,
  onOpenProfile,
  currentTrack,
  currentMission,
  currentTrackIndex = 0,
  currentMissionIndex = 0,
  tracks = [],
  xp,
  streak = 3,
  userName = 'joao_araujo',
  userRole = 'DevOps Engineer',
  isGuest = false,
  hasUpdate = false,
  onOpenUpdateModal,
}) => {
  const colors = ThemeColors[theme];
  const isDark = theme === 'dark';

  const [activeIndex, setActiveIndex] = useState(0);
  const flatListRef = useRef<FlatList<Track>>(null);

  const activeTrack = tracks[activeIndex] || currentTrack || tracks[0];

  const triggerHaptic = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
  };

  const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const offsetX = event.nativeEvent.contentOffset.x;
    const index = Math.round(offsetX / (CARD_WIDTH + CARD_SPACING));
    if (index !== activeIndex && index >= 0 && index < tracks.length) {
      setActiveIndex(index);
      triggerHaptic();
    }
  };

  const handleCardPress = (index: number, track: Track) => {
    triggerHaptic();
    setActiveIndex(index);
    if ((track.required_xp || 0) <= xp || isGuest) {
      onSelectTrack(index);
    } else {
      Alert.alert(
        'Trilha Bloqueada',
        `Esta trilha requer ${track.required_xp} XP (${track.required_seniority || 'Nível Superior'}). Conclua as missões das trilhas anteriores para desbloquear.`
      );
    }
  };

  const renderPathCard = (track: Track, index: number, isSelected: boolean) => {
    const isUnlocked = (track.required_xp || 0) <= xp || isGuest;
    const completed = isGuest ? 0 : (index === 0 ? 8 : (index === 1 ? 1 : 6));
    const total = track.missions?.length || 10;
    const progressPercent = Math.min(Math.max((completed / total) * 100, 10), 100);

    return (
      <View key={track.id} style={styles.pathCardTouchable}>
        <LiquidGlassView
          onPress={() => handleCardPress(index, track)}
          interactive={true}
          isSelected={isSelected}
          selectedBorderColor="#9E85FF"
          selectedGlowColor="#9E85FF"
          borderRadius={24}
          borderWidth={isSelected ? 2.4 : 1.2}
          borderColor={
            isSelected
              ? '#9E85FF'
              : isDark
              ? 'rgba(255, 255, 255, 0.28)'
              : 'rgba(255, 255, 255, 0.90)'
          }
          theme={theme}
          showSheen={true}
          intensity={40}
          contentStyle={styles.pathCardInterior}
        >
          {/* Row 1: Single Tech Badge with Real Logo */}
          <View style={styles.badgeRow}>
            <View
              style={[
                styles.techBadgeContainer,
                {
                  backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
                  borderColor: isDark ? 'rgba(255, 255, 255, 0.18)' : 'rgba(0, 0, 0, 0.08)',
                },
              ]}
            >
              <TrackIcon
                trackId={track.id}
                size={20}
                badgeSize={34}
                showBadge={true}
              />
            </View>

            {!isUnlocked && (
              <View
                style={[
                  styles.lockedPill,
                  {
                    backgroundColor: isDark ? 'rgba(0, 0, 0, 0.40)' : 'rgba(245, 158, 11, 0.15)',
                    borderColor: isDark ? 'rgba(252, 211, 77, 0.35)' : 'rgba(180, 83, 9, 0.25)',
                  },
                ]}
              >
                <Text
                  style={[
                    styles.lockedPillText,
                    { color: isDark ? '#FCD34D' : '#B45309' },
                  ]}
                >
                  🔒 {track.required_xp} XP
                </Text>
              </View>
            )}
          </View>

          {/* Row 2: Track Title */}
          <Text
            style={[
              styles.pathCardTitle,
              { color: isDark ? '#FFFFFF' : '#0F172A' },
            ]}
            numberOfLines={1}
          >
            {track.name}
          </Text>

          {/* Row 3: Section / Ratio Label */}
          <View style={styles.sectionRow}>
            <Text
              style={[
                styles.sectionLabel,
                { color: isDark ? '#A5B4FC' : '#6366F1' },
              ]}
            >
              SECTION
            </Text>
            <Text
              style={[
                styles.sectionRatio,
                { color: isDark ? '#C7D2FE' : '#334155' },
              ]}
            >
              {completed}/{total}
            </Text>
          </View>

          {/* Row 4: Lilac Rounded Progress Bar with Liquid Sheen */}
          <View
            style={[
              styles.progressTrack,
              { backgroundColor: isDark ? 'rgba(255, 255, 255, 0.10)' : 'rgba(0, 0, 0, 0.08)' },
            ]}
          >
            <View
              style={[
                styles.progressBarFill,
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
    <View style={[styles.root, { backgroundColor: 'transparent' }]}>
      {/* 1. Top Bar */}
      <View style={styles.topBar}>
        <TouchableOpacity
          style={styles.avatarButton}
          onPress={() => {
            triggerHaptic();
            onOpenProfile();
          }}
          activeOpacity={0.8}
          accessibilityLabel="Perfil do Operador"
          accessibilityRole="button"
        >
          <LinearGradient
            colors={['#9E85FF', '#00DF89', '#00F2FE']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.avatarRing}
          >
            <View style={[styles.avatarInner, { backgroundColor: isDark ? '#1E2238' : '#FFFFFF' }]}>
              <Text style={styles.avatarEmoji}>👨‍💻</Text>
            </View>
          </LinearGradient>
        </TouchableOpacity>

        <Text style={[styles.topBarTitle, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>
          DevOpsHero
        </Text>

        <View style={styles.topRightActions}>
          {hasUpdate && (
            <TouchableOpacity
              style={styles.updatePillBtn}
              onPress={() => {
                triggerHaptic();
                onOpenUpdateModal?.();
              }}
              activeOpacity={0.7}
              hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            >
              <Text style={styles.updatePillText}>UPDATE</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            style={[
              styles.themeToggleBtn,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)',
                borderColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)',
              },
            ]}
            onPress={() => {
              triggerHaptic();
              onToggleTheme();
            }}
            activeOpacity={0.7}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            accessibilityLabel="Alternar tema"
            accessibilityRole="button"
          >
            <Text style={styles.themeToggleIcon}>
              {theme === 'dark' ? '☀️' : '🌙'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* 2. Career Paths Header */}
        <View style={styles.sectionHeaderRow}>
          <Text style={[styles.careerPathsTitle, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>
            Career Paths
          </Text>
        </View>

        {isGuest && (
          <View
            style={[
              styles.guestNoticePill,
              {
                backgroundColor: isDark ? 'rgba(158, 133, 255, 0.12)' : 'rgba(158, 133, 255, 0.14)',
              },
            ]}
          >
            <Text style={[styles.guestNoticeText, { color: isDark ? '#C4B5FD' : '#4338CA' }]}>
              👤 Modo Visitante · Pontos e histórico desativados
            </Text>
          </View>
        )}

        {/* 3. Official Vertical Stack of Career Path Cards (Fidelity to media_1793711946097_66ec69ab.png) */}
        <View style={styles.verticalCardsList}>
          {tracks.map((track, idx) => (
            <View key={track.id} style={styles.verticalCardItem}>
              {renderPathCard(track, idx, idx === activeIndex)}
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  contentContainer: {
    paddingBottom: 120,
  },

  // 1. Top Bar
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 14,
    height: 60,
  },
  avatarCenterAbsolute: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarButton: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarRing: {
    width: 44,
    height: 44,
    borderRadius: 22,
    padding: 2,
    alignItems: 'center',
    justifyContent: 'center',
    ...Platform.select({
      ios: {
        shadowColor: '#9E85FF',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.5,
        shadowRadius: 6,
      },
      android: {
        elevation: 6,
      },
    }),
  },
  avatarInner: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#1E2238',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarEmoji: {
    fontSize: 18,
  },
  navIconButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#1E243D',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  navIconText: {
    fontSize: 18,
    textAlign: 'center',
  },
  iconButtonDots: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  topBarTitle: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 20,
    fontWeight: '800',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  themeToggleBtn: {
    width: 44,
    height: 44,
    borderRadius: 14,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  themeToggleIcon: {
    fontSize: 20,
  },
  topRightActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  updatePillBtn: {
    backgroundColor: '#E05236',
    paddingHorizontal: 8,
    height: 30,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
  },
  updatePillText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 0.5,
  },

  // 2. Section Header
  sectionHeaderRow: {
    paddingHorizontal: 22,
    paddingTop: 10,
    paddingBottom: 14,
  },
  careerPathsTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 0.5,
  },
  guestNoticePill: {
    marginHorizontal: 20,
    marginBottom: 16,
    paddingVertical: 9,
    paddingHorizontal: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(158, 133, 255, 0.40)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  guestNoticeText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '700',
    color: '#C4B5FD',
    textAlign: 'center',
  },

  // 3. Vertical Stack of Career Path Cards (media_1793711946097_66ec69ab.png)
  verticalCardsList: {
    paddingHorizontal: 20,
    gap: 16,
  },
  verticalCardItem: {
    width: '100%',
  },

  pathCardTouchable: {
    width: '100%',
  },
  pathCardInterior: {
    padding: 20,
    gap: 13,
  },
  badgeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  techBadgeContainer: {
    padding: 2,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.18)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeIconsGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  techBadgeBox: {
    width: 26,
    height: 26,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  techBadgeIconText: {
    fontSize: 14,
  },
  lockedPill: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 14,
    borderWidth: 1,
  },
  lockedPillText: {
    fontSize: 11,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  pathCardTitle: {
    fontSize: 18.5,
    fontWeight: '800',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 0.3,
  },
  sectionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionLabel: {
    fontSize: 11.5,
    fontWeight: '800',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 0.5,
  },
  sectionRatio: {
    fontSize: 12.5,
    fontWeight: '800',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  progressTrack: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
    position: 'relative',
  },

  // 5. Centered FAB
  fabContainer: {
    position: 'absolute',
    bottom: 82,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  fabButton: {
    width: 62,
    height: 62,
    borderRadius: 31,
    borderWidth: 1.5,
    borderColor: 'rgba(255, 255, 255, 0.35)',
    overflow: 'hidden',
    ...Platform.select({
      ios: {
        shadowColor: '#9E85FF',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.65,
        shadowRadius: 18,
      },
      android: {
        elevation: 10,
      },
    }),
  },
  fabGradient: {
    width: 59,
    height: 59,
    borderRadius: 29.5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  fabIcon: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0D1022',
    marginLeft: 2,
  },
});
