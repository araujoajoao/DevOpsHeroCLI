import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Dimensions, Animated, Easing } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface AmbientGlassBackgroundProps {
  theme?: 'light' | 'dark';
  children?: React.ReactNode;
}

/**
 * AmbientGlassBackground - Apple Liquid Glass Atmospheric Backing Engine (iOS 27 Physics)
 * Provides vibrant, luminous aurora light orbs and optical streaks that shine through
 * the systemUltraThinMaterial frosted glass layers (LiquidGlassView, FloatingDock, Cards).
 * Includes smooth atmospheric float drift simulating fluid light physics.
 */
export const AmbientGlassBackground: React.FC<AmbientGlassBackgroundProps> = ({
  theme = 'dark',
  children,
}) => {
  const isDark = theme === 'dark';

  // Fluid breathing drift animation (iOS 27 ambient light physics)
  const driftAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(driftAnim, {
          toValue: 1,
          duration: 9000,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
        Animated.timing(driftAnim, {
          toValue: 0,
          duration: 9000,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, [driftAnim]);

  const orb1TranslateX = driftAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 18],
  });
  const orb1TranslateY = driftAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -14],
  });

  const orb2TranslateX = driftAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -16],
  });
  const orb2TranslateY = driftAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 18],
  });

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: isDark ? '#080A16' : '#F6F8FA',
        },
      ]}
    >
      {/* 1. Base Atmospheric Space Gradient */}
      <LinearGradient
        colors={
          isDark
            ? ['#070914', '#0B0E20', '#121630', '#070914']
            : ['#F8FAFC', '#EEF2FF', '#E0E7FF', '#F1F5F9']
        }
        start={{ x: 0.1, y: 0.0 }}
        end={{ x: 0.9, y: 1.0 }}
        style={StyleSheet.absoluteFill}
        pointerEvents="none"
      />

      {/* 2. Top-Right Luminous Violet / Purple Aurora Orb */}
      <Animated.View
        style={[
          styles.ambientOrb,
          styles.topRightOrb,
          {
            transform: [
              { translateX: orb1TranslateX },
              { translateY: orb1TranslateY },
            ],
          },
        ]}
        pointerEvents="none"
      >
        <LinearGradient
          colors={
            isDark
              ? ['rgba(168, 85, 247, 0.60)', 'rgba(99, 102, 241, 0.35)', 'rgba(139, 92, 246, 0.10)', 'transparent']
              : ['rgba(168, 85, 247, 0.28)', 'rgba(99, 102, 241, 0.15)', 'transparent']
          }
          start={{ x: 0.5, y: 0.5 }}
          end={{ x: 1.0, y: 1.0 }}
          style={StyleSheet.absoluteFill}
        />
      </Animated.View>

      {/* 3. Center Atmospheric Magenta / Lilac Bloom */}
      <Animated.View
        style={[
          styles.ambientOrb,
          styles.centerBloomOrb,
          {
            transform: [
              { translateX: orb2TranslateX },
              { translateY: orb2TranslateY },
            ],
          },
        ]}
        pointerEvents="none"
      >
        <LinearGradient
          colors={
            isDark
              ? ['rgba(217, 70, 239, 0.35)', 'rgba(168, 85, 247, 0.18)', 'transparent']
              : ['rgba(217, 70, 239, 0.18)', 'rgba(168, 85, 247, 0.08)', 'transparent']
          }
          start={{ x: 0.5, y: 0.5 }}
          end={{ x: 1.0, y: 1.0 }}
          style={StyleSheet.absoluteFill}
        />
      </Animated.View>

      {/* 4. Bottom-Left Luminous Electric Cyan / Azure Aurora Orb */}
      <Animated.View
        style={[
          styles.ambientOrb,
          styles.bottomLeftOrb,
          {
            transform: [
              { translateX: orb1TranslateX },
              { translateY: orb2TranslateY },
            ],
          },
        ]}
        pointerEvents="none"
      >
        <LinearGradient
          colors={
            isDark
              ? ['rgba(6, 182, 212, 0.50)', 'rgba(14, 165, 233, 0.28)', 'rgba(0, 242, 254, 0.08)', 'transparent']
              : ['rgba(6, 182, 212, 0.25)', 'rgba(14, 165, 233, 0.12)', 'transparent']
          }
          start={{ x: 0.5, y: 0.5 }}
          end={{ x: 0.0, y: 0.0 }}
          style={StyleSheet.absoluteFill}
        />
      </Animated.View>

      {/* 5. Bottom-Center Neon Emerald / Mint Glow (behind Dock) */}
      <Animated.View
        style={[
          styles.ambientOrb,
          styles.dockGlowOrb,
          {
            transform: [{ translateY: orb1TranslateY }],
          },
        ]}
        pointerEvents="none"
      >
        <LinearGradient
          colors={
            isDark
              ? ['rgba(16, 185, 129, 0.40)', 'rgba(5, 150, 105, 0.16)', 'transparent']
              : ['rgba(16, 185, 129, 0.20)', 'rgba(5, 150, 105, 0.08)', 'transparent']
          }
          start={{ x: 0.5, y: 0.5 }}
          end={{ x: 0.5, y: 1.0 }}
          style={StyleSheet.absoluteFill}
        />
      </Animated.View>

      {/* 6. Optical Diagonal Refraction Streak Lines (-45° Angle) */}
      <View style={[styles.streakLine1, { backgroundColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.05)' }]} pointerEvents="none" />
      <View style={[styles.streakLine2, { backgroundColor: isDark ? 'rgba(168, 85, 247, 0.20)' : 'rgba(158, 133, 255, 0.10)' }]} pointerEvents="none" />

      {/* Children content mounted on top */}
      <View style={styles.contentLayer}>{children}</View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    position: 'relative',
    overflow: 'hidden',
  },
  contentLayer: {
    flex: 1,
    zIndex: 1,
  },
  ambientOrb: {
    position: 'absolute',
    borderRadius: 9999,
  },
  topRightOrb: {
    top: -SCREEN_WIDTH * 0.25,
    right: -SCREEN_WIDTH * 0.25,
    width: SCREEN_WIDTH * 1.15,
    height: SCREEN_WIDTH * 1.15,
  },
  centerBloomOrb: {
    top: SCREEN_HEIGHT * 0.28,
    left: -SCREEN_WIDTH * 0.20,
    width: SCREEN_WIDTH * 0.90,
    height: SCREEN_WIDTH * 0.90,
  },
  bottomLeftOrb: {
    bottom: -SCREEN_WIDTH * 0.20,
    left: -SCREEN_WIDTH * 0.25,
    width: SCREEN_WIDTH * 1.10,
    height: SCREEN_WIDTH * 1.10,
  },
  dockGlowOrb: {
    bottom: 20,
    alignSelf: 'center',
    width: SCREEN_WIDTH * 0.95,
    height: 140,
    borderRadius: 70,
  },
  streakLine1: {
    position: 'absolute',
    top: 80,
    left: -40,
    width: SCREEN_WIDTH * 1.2,
    height: 1.5,
    transform: [{ rotate: '-35deg' }],
  },
  streakLine2: {
    position: 'absolute',
    bottom: 220,
    right: -40,
    width: SCREEN_WIDTH * 1.1,
    height: 1.5,
    transform: [{ rotate: '-35deg' }],
  },
});
