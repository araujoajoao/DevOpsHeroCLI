import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  LayoutAnimation,
  Platform,
  UIManager,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { TrackIcon } from './TrackIcon';
import {
  LiveActivityService,
  LiveActivitySnapshot,
} from '../services/LiveActivityService';

if (
  Platform.OS === 'android' &&
  UIManager.setLayoutAnimationEnabledExperimental
) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

export const DynamicIslandBanner: React.FC = () => {
  const [snapshot, setSnapshot] = useState<LiveActivitySnapshot>(() =>
    LiveActivityService.getSnapshot()
  );
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const unsubscribe = LiveActivityService.subscribe((newSnapshot) => {
      setSnapshot(newSnapshot);
    });
    return unsubscribe;
  }, []);

  if (!snapshot.isActive || !snapshot.attributes || !snapshot.state) {
    return null;
  }

  const { attributes, state } = snapshot;
  const progressRatio =
    state.totalMissions > 0 ? state.completedCount / state.totalMissions : 0;

  const toggleExpand = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setIsExpanded(!isExpanded);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        activeOpacity={0.9}
        onPress={toggleExpand}
        style={[styles.islandBase, isExpanded && styles.islandExpanded]}
        hitSlop={{ top: 6, bottom: 6, left: 6, right: 6 }}
        accessibilityLabel="Dynamic Island DevOps Activity"
      >
        {isExpanded ? (
          // Expanded Dynamic Island View
          <View style={styles.expandedContent}>
            {/* Row 1: Leading Track + Trailing XP */}
            <View style={styles.expandedHeaderRow}>
              <View style={styles.leadingCol}>
                <View style={styles.techBadgeContainer}>
                  <TrackIcon
                    trackId={attributes.trackId}
                    size={16}
                    badgeSize={28}
                    showBadge={false}
                  />
                </View>
                <View style={styles.trackTitles}>
                  <Text style={styles.trackTitleText} numberOfLines={1}>
                    {attributes.trackName}
                  </Text>
                  <Text style={styles.trackSubText}>DevOpsHero Lab</Text>
                </View>
              </View>

              <View style={styles.trailingCol}>
                <View style={styles.xpPill}>
                  <Text style={styles.xpPillText}>⭐ +{state.xpReward} XP</Text>
                </View>
                <View style={styles.statusRow}>
                  <View
                    style={[
                      styles.statusDot,
                      {
                        backgroundColor:
                          state.status === 'ONLINE' ||
                          state.status === 'COMPLETED'
                            ? '#00DF89'
                            : '#FBBF24',
                      },
                    ]}
                  />
                  <Text
                    style={[
                      styles.statusText,
                      {
                        color:
                          state.status === 'ONLINE' ||
                          state.status === 'COMPLETED'
                            ? '#00DF89'
                            : '#FBBF24',
                      },
                    ]}
                  >
                    {state.status}
                  </Text>
                </View>
              </View>
            </View>

            {/* Row 2: Terminal Line Comment & Prompt */}
            <View style={styles.terminalBox}>
              <View style={styles.terminalLine}>
                <Text style={styles.lineNumber}>1</Text>
                <Text style={styles.commentText} numberOfLines={1}>
                  # {state.objective}
                </Text>
              </View>
              <View style={styles.terminalLine}>
                <Text style={styles.lineNumber}>2</Text>
                <Text style={styles.promptSymbol}>➜</Text>
                <Text style={styles.promptText}>
                  ~ {attributes.trackId} $
                </Text>
              </View>
            </View>

            {/* Row 3: Progress & Speed Score */}
            <View style={styles.progressRow}>
              <Text style={styles.sectionFraction}>
                SECTION {state.completedCount}/{state.totalMissions}
              </Text>
              <Text style={styles.speedScoreText}>
                ⚡ {state.speedScoreMultiplier.toFixed(1)}x XP Boost
              </Text>
              <Text style={styles.timerText}>⏱️ {state.secondsElapsed}s</Text>
            </View>

            <View style={styles.progressBarTrack}>
              <View
                style={[
                  styles.progressBarFill,
                  { width: `${Math.max(progressRatio * 100, 8)}%` },
                ]}
              />
            </View>
          </View>
        ) : (
          // Compact Dynamic Island Pill
          <View style={styles.compactRow}>
            <View style={styles.compactLeading}>
              <TrackIcon
                trackId={attributes.trackId}
                size={14}
                badgeSize={22}
                showBadge={false}
              />
              <Text style={styles.compactTrackName} numberOfLines={1}>
                {attributes.trackName}
              </Text>
            </View>

            <View style={styles.compactTrailing}>
              <Text style={styles.compactXp}>+{state.xpReward} XP</Text>
              <Text style={styles.compactTimer}>⏱️ {state.secondsElapsed}s</Text>
            </View>
          </View>
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 4,
    zIndex: 99,
  },
  islandBase: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#000000',
    borderRadius: 22,
    borderWidth: 1.2,
    borderColor: 'rgba(158, 133, 255, 0.35)',
    paddingHorizontal: 12,
    paddingVertical: 7,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 8,
  },
  islandExpanded: {
    borderRadius: 28,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  compactRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 28,
  },
  compactLeading: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
    flex: 1,
  },
  compactTrackName: {
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11,
    fontWeight: '700',
  },
  compactTrailing: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  compactXp: {
    color: '#FBBF24',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 10,
    fontWeight: '800',
  },
  compactTimer: {
    color: '#A5B4FC',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 10,
    fontWeight: '600',
  },
  expandedContent: {
    width: '100%',
    gap: 10,
  },
  expandedHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  leadingCol: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flex: 1,
  },
  techBadgeContainer: {
    width: 30,
    height: 30,
    borderRadius: 9,
    backgroundColor: '#1E243E',
    borderWidth: 1,
    borderColor: 'rgba(158, 133, 255, 0.35)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  trackTitles: {
    flex: 1,
  },
  trackTitleText: {
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12.5,
    fontWeight: '700',
  },
  trackSubText: {
    color: '#A5B4FC',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 9.5,
    fontWeight: '600',
  },
  trailingCol: {
    alignItems: 'flex-end',
    gap: 3,
  },
  xpPill: {
    backgroundColor: 'rgba(251, 191, 36, 0.15)',
    paddingHorizontal: 6,
    paddingVertical: 2.5,
    borderRadius: 6,
    borderWidth: 0.8,
    borderColor: 'rgba(251, 191, 36, 0.35)',
  },
  xpPillText: {
    color: '#FBBF24',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 10,
    fontWeight: '800',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  statusDot: {
    width: 5.5,
    height: 5.5,
    borderRadius: 3,
  },
  statusText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 9,
    fontWeight: '700',
  },
  terminalBox: {
    backgroundColor: '#0F1220',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#272E4F',
    padding: 7,
    gap: 3,
  },
  terminalLine: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  lineNumber: {
    color: '#475569',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 10,
    fontWeight: '600',
    width: 12,
  },
  commentText: {
    color: '#A5B4FC',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 10.5,
    fontWeight: '600',
    flex: 1,
  },
  promptSymbol: {
    color: '#00DF89',
    fontWeight: '800',
    fontSize: 10.5,
  },
  promptText: {
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 10.5,
    fontWeight: '700',
  },
  progressRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionFraction: {
    color: '#9E85FF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 9.5,
    fontWeight: '800',
  },
  speedScoreText: {
    color: '#00DF89',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 9.5,
    fontWeight: '700',
  },
  timerText: {
    color: '#D8E2FD',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 9.5,
    fontWeight: '600',
  },
  progressBarTrack: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: 4,
    backgroundColor: '#9E85FF',
    borderRadius: 2,
  },
});

