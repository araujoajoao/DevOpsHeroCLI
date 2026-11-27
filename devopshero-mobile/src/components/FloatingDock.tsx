import React, { useRef, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform, Animated, Pressable } from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { TabType } from '../types';
import { ThemeColors } from '../theme/colors';
import { CURRENT_DEVICE } from '../utils/deviceInfo';

interface FloatingDockProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  theme: 'light' | 'dark';
}

const TABS: {
  id: TabType;
  label: string;
  icon: string;
  color: string;
  bgActive: string;
  glowColor: string;
}[] = [
  {
    id: 'home',
    label: 'Início',
    icon: '🏠',
    color: '#9E85FF',
    bgActive: 'rgba(158, 133, 255, 0.28)',
    glowColor: 'rgba(158, 133, 255, 0.60)',
  },
  {
    id: 'tracks',
    label: 'Trilhas',
    icon: '📚',
    color: '#00DF89',
    bgActive: 'rgba(0, 223, 137, 0.25)',
    glowColor: 'rgba(0, 223, 137, 0.55)',
  },
  {
    id: 'profile',
    label: 'Perfil',
    icon: '👤',
    color: '#00F2FE',
    bgActive: 'rgba(0, 242, 254, 0.25)',
    glowColor: 'rgba(0, 242, 254, 0.55)',
  },
];

/**
 * FloatingDock - Liquid Glass Floating Tab Bar (LiquidLensView Architecture)
 * Based on Apple Liquid Glass design principles and LiquidGlassKit:
 * - Real Apple systemUltraThinMaterial frosted glass capsule
 * - Translucent crystal body allowing ambient orbs to shine through
 * - Directional -45° specular glare reflection
 * - Chromatic refraction bevel on top rim
 * - Morphing Liquid Lens active pill with neon rim, specular highlight, and drop shadow
 * - Taptic Engine haptic responses
 */
export const FloatingDock: React.FC<FloatingDockProps> = ({
  activeTab,
  onTabChange,
  theme,
}) => {
  const isDark = theme === 'dark';

  // Float comfortably above physical iPhone home indicator
  const bottomLift = Math.max(CURRENT_DEVICE.insets.bottom, 16);

  // iOS 27 Liquid Lens Spring Transition Physics
  const pillScaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    pillScaleAnim.setValue(0.92);
    Animated.spring(pillScaleAnim, {
      toValue: 1,
      tension: 160,
      friction: 10,
      useNativeDriver: true,
    }).start();
  }, [activeTab]);

  const handleTabPress = (tabId: TabType) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
    onTabChange(tabId);
  };

  return (
    <View style={[styles.dockWrapper, { bottom: bottomLift }]}>
      <View
        style={[
          styles.dockShadowContainer,
          {
            shadowColor: isDark ? '#000000' : '#475569',
            shadowOpacity: isDark ? 0.45 : 0.15,
          },
        ]}
      >
        <View
          style={[
            styles.dockContainer,
            {
              backgroundColor: isDark
                ? 'rgba(255, 255, 255, 0.045)' // Ultra-pure crystal glass!
                : 'rgba(255, 255, 255, 0.50)',
              borderColor: isDark
                ? 'rgba(255, 255, 255, 0.30)'
                : 'rgba(255, 255, 255, 0.90)',
            },
          ]}
        >
          {/* Apple Native Backdrop Blur Filter */}
          <BlurView
            intensity={Platform.OS === 'ios' ? 42 : 55}
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

          {/* 1. Specular Liquid Glass Top Sheen (-45° Glare Angle) */}
          <LinearGradient
            colors={
              isDark
                ? [
                    'rgba(255, 255, 255, 0.40)',
                    'rgba(255, 255, 255, 0.12)',
                    'rgba(255, 255, 255, 0.02)',
                    'transparent',
                  ]
                : [
                    'rgba(255, 255, 255, 0.95)',
                    'rgba(255, 255, 255, 0.45)',
                    'rgba(255, 255, 255, 0.10)',
                    'transparent',
                  ]
            }
            start={{ x: 0.0, y: 0.0 }}
            end={{ x: 0.85, y: 0.85 }}
            style={StyleSheet.absoluteFill}
            pointerEvents="none"
          />

          {/* 2. Chromatic Dispersion Bevel on Top Edge */}
          <LinearGradient
            colors={
              isDark
                ? [
                    'rgba(168, 85, 247, 0.50)',
                    'rgba(56, 189, 248, 0.40)',
                    'rgba(255, 255, 255, 0.70)',
                    'rgba(16, 185, 129, 0.40)',
                    'transparent',
                  ]
                : [
                    'rgba(168, 85, 247, 0.35)',
                    'rgba(56, 189, 248, 0.25)',
                    'rgba(255, 255, 255, 0.85)',
                    'rgba(16, 185, 129, 0.25)',
                    'transparent',
                  ]
            }
            start={{ x: 0.05, y: 0.0 }}
            end={{ x: 0.95, y: 0.0 }}
            style={styles.chromaticBevel}
            pointerEvents="none"
          />

          {/* 3. 3D Inner Bevel Highlight Stroke */}
          <View
            style={[
              styles.innerBevel,
              {
                borderColor: isDark
                  ? 'rgba(255, 255, 255, 0.18)'
                  : 'rgba(255, 255, 255, 0.75)',
              },
            ]}
            pointerEvents="none"
          />

          {/* 4. Tab Items */}
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;

            if (isActive) {
              return (
                <Animated.View
                  key={tab.id}
                  style={{
                    transform: [{ scale: pillScaleAnim }],
                  }}
                >
                  <TouchableOpacity
                    style={[
                      styles.activePill,
                      {
                        backgroundColor: tab.bgActive,
                        borderColor: tab.color,
                        shadowColor: tab.glowColor,
                      },
                    ]}
                    onPress={() => handleTabPress(tab.id)}
                    activeOpacity={0.85}
                    accessibilityRole="tab"
                    accessibilityState={{ selected: true }}
                  >
                  {/* Active Liquid Lens Specular Highlight */}
                  <LinearGradient
                    colors={[
                      'rgba(255, 255, 255, 0.50)',
                      'rgba(255, 255, 255, 0.12)',
                      'transparent',
                    ]}
                    start={{ x: 0.1, y: 0.0 }}
                    end={{ x: 0.9, y: 1.0 }}
                    style={StyleSheet.absoluteFill}
                    pointerEvents="none"
                  />
                  <Text style={styles.activeIcon}>{tab.icon}</Text>
                  <Text style={[styles.activeLabel, { color: tab.color }]}>
                    {tab.label}
                  </Text>
                </TouchableOpacity>
              </Animated.View>
            );
            }

            return (
              <TouchableOpacity
                key={tab.id}
                style={styles.inactiveTab}
                onPress={() => handleTabPress(tab.id)}
                activeOpacity={0.7}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                accessibilityRole="tab"
                accessibilityState={{ selected: false }}
              >
                <Text style={styles.inactiveIcon}>{tab.icon}</Text>
                <Text
                  style={[
                    styles.inactiveLabel,
                    { color: isDark ? '#C7D2FE' : '#475569' },
                  ]}
                >
                  {tab.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  dockWrapper: {
    position: 'absolute',
    left: 16,
    right: 16,
    alignItems: 'center',
    zIndex: 999,
  },
  dockShadowContainer: {
    width: '100%',
    maxWidth: 380,
    borderRadius: 26,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 24,
    elevation: 14,
  },
  dockContainer: {
    width: '100%',
    height: 64,
    borderRadius: 26,
    borderWidth: 1.5,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 10,
    overflow: 'hidden',
    position: 'relative',
  },
  chromaticBevel: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 1.5,
  },
  innerBevel: {
    position: 'absolute',
    top: 1,
    left: 1,
    right: 1,
    bottom: 1,
    borderRadius: 25,
    borderWidth: 0.75,
  },
  activePill: {
    borderRadius: 20,
    borderWidth: 1.5,
    paddingHorizontal: 18,
    height: 44,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    position: 'relative',
    overflow: 'hidden',
    ...Platform.select({
      ios: {
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.60,
        shadowRadius: 12,
      },
      android: {
        elevation: 6,
      },
    }),
  },
  activeIcon: {
    fontSize: 18,
  },
  activeLabel: {
    fontSize: 13,
    fontWeight: '800',
    letterSpacing: 0.3,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  inactiveTab: {
    paddingHorizontal: 14,
    height: 44,
    minWidth: 44,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  inactiveIcon: {
    fontSize: 17,
    opacity: 0.85,
  },
  inactiveLabel: {
    fontSize: 12.5,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
});
