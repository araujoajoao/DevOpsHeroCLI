import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  StyleSheet,
  StatusBar as RNStatusBar,
  Platform,
  LogBox,
  Animated,
  Easing,
} from 'react-native';

// Suppress transient gesture responder desync & React Native codegen warnings
LogBox.ignoreLogs([
  'Cannot record touch move without a touch start',
  'Cannot record touch end without a touch start',
  "Codegen didn't run for",
  'View config not found for component',
  'No native ExponentConstants module found',
]);
import { StatusBar } from 'expo-status-bar';
import { ThemeColors } from './src/theme/colors';
import { TabType, Track, MobileDataset } from './src/types';
import { HomeScreen } from './src/screens/HomeScreen';
import { TracksScreen } from './src/screens/TracksScreen';
import { PracticeScreen } from './src/screens/PracticeScreen';
import { ProfileScreen } from './src/screens/ProfileScreen';
import { AuthScreen } from './src/screens/AuthScreen';
import { FloatingDock } from './src/components/FloatingDock';
import { AppUpdateModal } from './src/components/AppUpdateModal';
import { AmbientGlassBackground } from './src/components/AmbientGlassBackground';
import { useDeviceInfo } from './src/utils/deviceInfo';

// Load official 80 missions dataset
const DATA: MobileDataset = require('./assets/data/missions.json');

const shuffleArray = <T,>(arr: T[]): T[] => {
  const result = [...arr];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
};

export default function App() {
  const deviceInfo = useDeviceInfo();
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [activeTab, setActiveTab] = useState<TabType>('home');
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [currentMissionIndex, setCurrentMissionIndex] = useState(0);
  const [xp, setXp] = useState(0);
  const [streak, setStreak] = useState(0);
  const [completedMissionIds, setCompletedMissionIds] = useState<Set<string>>(new Set());
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [userRole, setUserRole] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [isUpdateModalVisible, setIsUpdateModalVisible] = useState(false);
  const [hasUpdate, setHasUpdate] = useState(false);
  const [targetVersion, setTargetVersion] = useState('0.21.0');

  // Apple iOS 27 Fluid Tab Transition Physics (Spring & Scale Shift)
  const tabTransitionOpacity = useRef(new Animated.Value(1)).current;
  const tabTransitionScale = useRef(new Animated.Value(1)).current;
  const tabTransitionTranslateY = useRef(new Animated.Value(0)).current;
  const dockAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    tabTransitionOpacity.setValue(0.80);
    tabTransitionScale.setValue(0.988);
    tabTransitionTranslateY.setValue(4);

    Animated.parallel([
      Animated.timing(tabTransitionOpacity, {
        toValue: 1,
        duration: 180,
        easing: Easing.out(Easing.quad),
        useNativeDriver: true,
      }),
      Animated.spring(tabTransitionScale, {
        toValue: 1,
        tension: 180,
        friction: 12,
        useNativeDriver: true,
      }),
      Animated.spring(tabTransitionTranslateY, {
        toValue: 0,
        tension: 180,
        friction: 12,
        useNativeDriver: true,
      }),
      Animated.spring(dockAnim, {
        toValue: activeTab === 'practice' ? 0 : 1,
        tension: 180,
        friction: 12,
        useNativeDriver: true,
      }),
    ]).start();
  }, [activeTab]);

  useEffect(() => {
    const checkRemoteUpdate = async () => {
      try {
        const res = await fetch(
          'https://raw.githubusercontent.com/araujoajoao/DevOpsHeroCLI/main/pyproject.toml'
        );
        if (res.ok) {
          const text = await res.text();
          const match = text.match(/version\s*=\s*["']([^"']+)["']/);
          if (match && match[1]) {
            const remoteVer = match[1];
            const curVer = '1.0.0';
            const rParts = remoteVer.split('.').map(Number);
            const cParts = curVer.split('.').map(Number);
            let isNewer = false;
            for (let i = 0; i < Math.max(rParts.length, cParts.length); i++) {
              const r = rParts[i] || 0;
              const c = cParts[i] || 0;
              if (r > c) { isNewer = true; break; }
              if (r < c) { break; }
            }
            if (isNewer) {
              setHasUpdate(true);
              setTargetVersion(remoteVer);
            }
          }
        }
      } catch (_) {}
    };
    checkRemoteUpdate();
  }, []);

  // Dynamic shuffled state for tracks & tasks
  const [tracksState, setTracksState] = useState<Track[]>(() =>
    DATA.tracks.map(t => ({
      ...t,
      missions: shuffleArray(t.missions),
    }))
  );

  const colors = ThemeColors[theme];
  const currentTrack: Track = tracksState[currentTrackIndex] || tracksState[0];

  const handleToggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleLogin = (user: string) => {
    const guestMode = user.toLowerCase() === 'visitante';
    setUserName(user);
    setUserRole(guestMode ? 'Visitante (sem histórico de pontos)' : 'DevOps Operator · Nível 2');
    setIsGuest(guestMode);
    if (!guestMode) {
      setXp(350);
      setStreak(3);
    } else {
      setXp(0);
      setStreak(0);
    }
    setIsLoggedIn(true);
  };

  const handleRegister = (user: string, role?: string) => {
    setUserName(user);
    setUserRole(role || 'DevOps Junior · Nível 1');
    setIsGuest(false);
    setXp(100);
    setStreak(1);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setIsGuest(false);
    setUserName('');
    setUserEmail('');
    setUserRole('');
    setXp(0);
    setStreak(0);
  };

  const handleSelectTrack = (trackIndex: number) => {
    const targetTrack = tracksState[trackIndex];
    if (!isGuest && targetTrack && (targetTrack.required_xp || 0) > xp) {
      return;
    }
    // Re-shuffle missions for this track on each entry so order is randomized
    setTracksState(prev => {
      const updated = [...prev];
      const baseMissions = DATA.tracks[trackIndex]?.missions || updated[trackIndex].missions;
      updated[trackIndex] = {
        ...updated[trackIndex],
        missions: shuffleArray(baseMissions),
      };
      return updated;
    });
    setCurrentTrackIndex(trackIndex);
    setCurrentMissionIndex(0);
    setActiveTab('practice');
  };

  const handleStartMission = (trackIndex: number, missionIndex: number = 0) => {
    const targetTrack = tracksState[trackIndex];
    if (!isGuest && targetTrack && (targetTrack.required_xp || 0) > xp) {
      return;
    }
    setCurrentTrackIndex(trackIndex);
    setCurrentMissionIndex(missionIndex);
    setActiveTab('practice');
  };

  const handleMissionComplete = (xpGained: number, newStreak: number) => {
    if (!isGuest) {
      setXp(prev => prev + xpGained);
      setStreak(newStreak);
    }
    const currMission = currentTrack.missions[currentMissionIndex];
    if (currMission) {
      setCompletedMissionIds(prev => new Set([...prev, currMission.id]));
    }
  };

  const handleBreakStreak = () => {
    setStreak(0);
  };

  const handleNextMission = () => {
    if (currentMissionIndex + 1 < currentTrack.missions.length) {
      setCurrentMissionIndex(prev => prev + 1);
    } else if (currentTrackIndex + 1 < tracksState.length) {
      const nextTrack = tracksState[currentTrackIndex + 1];
      if (nextTrack && (nextTrack.required_xp || 0) <= xp) {
        setTracksState(prev => {
          const updated = [...prev];
          const baseMissions = DATA.tracks[currentTrackIndex + 1]?.missions || updated[currentTrackIndex + 1].missions;
          updated[currentTrackIndex + 1] = {
            ...updated[currentTrackIndex + 1],
            missions: shuffleArray(baseMissions),
          };
          return updated;
        });
        setCurrentTrackIndex(prev => prev + 1);
        setCurrentMissionIndex(0);
      } else {
        setActiveTab('home');
      }
    } else {
      setActiveTab('home');
    }
  };

  return (
    <AmbientGlassBackground theme={theme}>
      <View
        style={[
          styles.root,
          {
            paddingTop: deviceInfo.insets.top,
          },
        ]}
      >
        <StatusBar style={theme === 'dark' ? 'light' : 'dark'} />

      <View
        style={[
          styles.container,
          deviceInfo.isDesktop && styles.desktopContainer,
        ]}
      >
        {!isLoggedIn ? (
          <AuthScreen
            theme={theme}
            onToggleTheme={handleToggleTheme}
            onAuthSuccess={({ userName: uName, email: uEmail, role: uRole }) => {
              const guestMode = uName.toLowerCase() === 'visitante' || !uEmail;
              setUserName(uName);
              setUserEmail(uEmail);
              setUserRole(uRole);
              setIsGuest(guestMode);
              if (guestMode) {
                setXp(0);
                setStreak(0);
              } else {
                setXp(350);
                setStreak(3);
              }
              setIsLoggedIn(true);
              setActiveTab('home');
            }}
          />
        ) : (
          <>
            <Animated.View
              style={[
                styles.content,
                {
                  opacity: tabTransitionOpacity,
                  transform: [
                    { scale: tabTransitionScale },
                    { translateY: tabTransitionTranslateY },
                  ],
                },
              ]}
            >
              {activeTab === 'home' && (
                <HomeScreen
                  theme={theme}
                  onToggleTheme={handleToggleTheme}
                  onSelectTrack={idx => {
                    setCurrentTrackIndex(idx);
                    setCurrentMissionIndex(0);
                    setActiveTab('tracks');
                  }}
                  onStartMission={handleStartMission}
                  onViewAllTracks={() => setActiveTab('tracks')}
                  onOpenProfile={() => setActiveTab('profile')}
                  currentTrack={currentTrack}
                  currentMission={currentTrack.missions[currentMissionIndex] || currentTrack.missions[0]}
                  currentTrackIndex={currentTrackIndex}
                  currentMissionIndex={currentMissionIndex}
                  tracks={tracksState}
                  xp={xp}
                  streak={streak}
                  userName={userName}
                  userRole={userRole}
                  isGuest={isGuest}
                  hasUpdate={hasUpdate}
                  onOpenUpdateModal={() => setIsUpdateModalVisible(true)}
                />
              )}

              {activeTab === 'tracks' && (
                <TracksScreen
                  theme={theme}
                  onToggleTheme={handleToggleTheme}
                  currentTrackIndex={currentTrackIndex}
                  onSelectTrack={idx => {
                    setCurrentTrackIndex(idx);
                    setCurrentMissionIndex(0);
                  }}
                  onStartMission={handleStartMission}
                  onBackToHome={() => setActiveTab('home')}
                  tracks={tracksState}
                  xp={xp}
                  completedMissionIds={completedMissionIds}
                />
              )}

              {activeTab === 'practice' && (
                <PracticeScreen
                  theme={theme}
                  track={currentTrack}
                  missionIndex={currentMissionIndex}
                  onClose={() => setActiveTab('home')}
                  onGoToTracks={() => setActiveTab('tracks')}
                  onMissionComplete={handleMissionComplete}
                  onBreakStreak={handleBreakStreak}
                  onNextMission={handleNextMission}
                  streak={streak}
                  xp={xp}
                />
              )}

              {activeTab === 'profile' && (
                <ProfileScreen
                  theme={theme}
                  onSetTheme={setTheme}
                  xp={xp}
                  streak={streak}
                  userName={userName}
                  userEmail={userEmail}
                  userRole={userRole}
                  isLoggedIn={isLoggedIn}
                  onLogin={handleLogin}
                  onRegister={handleRegister}
                  onLogout={handleLogout}
                  onBackToHome={() => setActiveTab('home')}
                />
              )}
            </Animated.View>

            {/* Floating Dock Navigation (Glides smoothly off-screen when Practice screen is active) */}
            <Animated.View
              pointerEvents={activeTab === 'practice' ? 'none' : 'auto'}
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                bottom: 0,
                opacity: dockAnim,
                transform: [
                  {
                    translateY: dockAnim.interpolate({
                      inputRange: [0, 1],
                      outputRange: [90, 0],
                    }),
                  },
                ],
              }}
            >
              <FloatingDock
                activeTab={activeTab}
                onTabChange={setActiveTab}
                theme={theme}
              />
            </Animated.View>

            <AppUpdateModal
              visible={isUpdateModalVisible}
              onDismiss={() => setIsUpdateModalVisible(false)}
              currentVersion="v1.0.0"
              targetVersion={targetVersion}
            />
          </>
        )}
      </View>
    </View>
    </AmbientGlassBackground>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  container: {
    flex: 1,
    width: '100%',
  },
  desktopContainer: {
    maxWidth: 960,
    alignSelf: 'center',
  },
  content: {
    flex: 1,
  },
});
