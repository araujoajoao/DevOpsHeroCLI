import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Animated, Platform } from 'react-native';
import Svg, {
  Rect,
  Circle,
  Ellipse,
  Path,
  G,
  Defs,
  LinearGradient,
  Stop,
  Line,
} from 'react-native-svg';
import * as Haptics from 'expo-haptics';

interface CyberLockHUDProps {
  status: 'standby' | 'success' | 'error';
}

export const CyberLockHUD: React.FC<CyberLockHUDProps> = ({ status }) => {
  // 0 = locked shut, 1 = fully open
  const [openProgress, setOpenProgress] = useState(status === 'success' ? 1 : 0);

  // Outer container animations (haptic pop & error shake)
  const shakeX = useRef(new Animated.Value(0)).current;
  const scale = useRef(new Animated.Value(1)).current;

  // Shackle opening driver (0 -> 1)
  const animVal = useRef(new Animated.Value(status === 'success' ? 1 : 0)).current;

  useEffect(() => {
    const listenerId = animVal.addListener(({ value }) => {
      setOpenProgress(value);
    });

    if (status === 'success') {
      try {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } catch (_) {}

      // Reset to closed first so opening spring triggers authentically
      animVal.setValue(0);

      Animated.sequence([
        Animated.timing(scale, { toValue: 1.05, duration: 160, useNativeDriver: true }),
        Animated.timing(scale, { toValue: 1.0, duration: 180, useNativeDriver: true }),
      ]).start();

      Animated.spring(animVal, {
        toValue: 1,
        friction: 6.0,
        tension: 40,
        useNativeDriver: false,
      }).start();
    } else if (status === 'error') {
      try {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      } catch (_) {}

      Animated.sequence([
        Animated.timing(animVal, {
          toValue: 0,
          duration: 120,
          useNativeDriver: false,
        }),
        Animated.sequence([
          Animated.timing(shakeX, { toValue: -6, duration: 40, useNativeDriver: true }),
          Animated.timing(shakeX, { toValue: 6, duration: 50, useNativeDriver: true }),
          Animated.timing(shakeX, { toValue: -4, duration: 40, useNativeDriver: true }),
          Animated.timing(shakeX, { toValue: 4, duration: 40, useNativeDriver: true }),
          Animated.timing(shakeX, { toValue: 0, duration: 40, useNativeDriver: true }),
        ]),
      ]).start();
    } else {
      animVal.setValue(0);
      shakeX.setValue(0);
      scale.setValue(1);
    }

    return () => {
      animVal.removeListener(listenerId);
    };
  }, [status]);

  const isSuccess = status === 'success';
  const isError = status === 'error';

  // HUD & Padlock Theme Colors
  const strokeColor = isSuccess ? '#22c55e' : isError ? '#ef4444' : '#64748b';
  const statusLabel = isSuccess ? '● UNLOCKED' : isError ? '● LOCKED' : '● STANDBY';
  const labelColor = isSuccess ? '#4ade80' : isError ? '#f87171' : '#94a3b8';
  const borderColor = isSuccess
    ? 'rgba(34, 197, 94, 0.45)'
    : isError
    ? 'rgba(239, 68, 68, 0.45)'
    : 'rgba(255, 255, 255, 0.16)';
  const boxBg = isSuccess ? '#09130e' : isError ? '#140909' : '#0b1118';

  // Physical Shackle Trajectory:
  // Hinge point at right socket: (103, 80)
  // At openProgress = 0 (Locked): yLift = 0, rotAngle = 0deg (both legs plunge 4px deep inside sockets)
  // At openProgress = 1 (Open): yLift = -7px, rotAngle = +28deg (smooth upward clockwise swing)
  // Left tip opens a clean 15.7px gap above left socket, while the arch top clears 8.7px below top divider.
  const yLift = openProgress * -7.0;
  const rotAngle = openProgress * 28.0;
  const shackleTransform = `translate(0, ${yLift}) translate(103, 80) rotate(${rotAngle}) translate(-103, -80)`;

  return (
    <Animated.View
      style={[
        styles.container,
        {
          backgroundColor: boxBg,
          borderColor: borderColor,
          transform: [{ translateX: shakeX }, { scale: scale }],
        },
      ]}
    >
      {/* 
        Single Unified SVG Canvas (180 x 160 viewBox):
        Both locked and unlocked states are optically and geometrically centered:
        - 18px top margin to divider (locked)
        - 18px bottom margin to divider (locked)
        - 57px left margin / 57px right margin to canvas edges
        - Shackle in open state lifts upward without clipping text or borders.
      */}
      <Svg width={148} height={136} viewBox="0 0 180 160">
        <Defs>
          {/* Chrome Metallic Steel Shackle Gradient */}
          <LinearGradient id="chromeShackle" x1="0%" y1="0%" x2="100%" y2="100%">
            <Stop offset="0%" stopColor="#ffffff" />
            <Stop offset="30%" stopColor="#f1f5f9" />
            <Stop offset="70%" stopColor="#cbd5e1" />
            <Stop offset="100%" stopColor="#94a3b8" />
          </LinearGradient>

          {/* Cyber Body Gradients */}
          <LinearGradient id="bodyGradSuccess" x1="0%" y1="0%" x2="0%" y2="100%">
            <Stop offset="0%" stopColor="#1e5336" />
            <Stop offset="100%" stopColor="#113220" />
          </LinearGradient>

          <LinearGradient id="bodyGradError" x1="0%" y1="0%" x2="0%" y2="100%">
            <Stop offset="0%" stopColor="#881919" />
            <Stop offset="100%" stopColor="#4c1010" />
          </LinearGradient>

          <LinearGradient id="bodyGradStandby" x1="0%" y1="0%" x2="0%" y2="100%">
            <Stop offset="0%" stopColor="#1e293b" />
            <Stop offset="100%" stopColor="#0f172a" />
          </LinearGradient>
        </Defs>

        {/* 1. HUD Crosshairs at 4 Corners */}
        <Circle cx={8} cy={8} r={1.5} fill={strokeColor} />
        <Circle cx={172} cy={8} r={1.5} fill={strokeColor} />
        <Circle cx={8} cy={152} r={1.5} fill={strokeColor} />
        <Circle cx={172} cy={152} r={1.5} fill={strokeColor} />

        {/* 2. HUD Meta Divider Lines */}
        <Line x1={10} y1={26} x2={170} y2={26} stroke={borderColor} strokeWidth={1} />
        <Line x1={10} y1={144} x2={170} y2={144} stroke={borderColor} strokeWidth={1} />

        {/* 3. Sockets on the top surface of the padlock body (Depth Insets) */}
        <Ellipse cx={77} cy={80} rx={6.5} ry={2.5} fill="#060c09" stroke={strokeColor} strokeWidth={1} />
        <Ellipse cx={103} cy={80} rx={6.5} ry={2.5} fill="#060c09" stroke={strokeColor} strokeWidth={1} />

        {/* 
          4. Animated Padlock Shackle:
          - Heavy 8px Chrome Steel Arch
          - Left leg at x=77, Right leg at x=103
          - In locked state: plunges cleanly 4px inside sockets
          - In open state: springs up 7px and rotates +28deg upwards, clearing left socket by ~16px
        */}
        <G transform={shackleTransform}>
          <Path
            d="M 77 84 L 77 61 A 13 13 0 0 1 103 61 L 103 84"
            fill="none"
            stroke="url(#chromeShackle)"
            strokeWidth={8}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </G>

        {/* 5. Padlock Body (Heavy Armored Cyber Shell, centered at X=90, Y=103) */}
        <Rect
          x={57}
          y={80}
          width={66}
          height={46}
          rx={14}
          fill={
            isSuccess
              ? 'url(#bodyGradSuccess)'
              : isError
              ? 'url(#bodyGradError)'
              : 'url(#bodyGradStandby)'
          }
          stroke={strokeColor}
          strokeWidth={3.2}
        />

        {/* 6. Center Rivet & Keyhole Core */}
        <Circle cx={90} cy={101} r={5.5} fill="#f8fafc" stroke="#cbd5e1" strokeWidth={0.8} />
        <Circle cx={90} cy={99.5} r={2.2} fill="#0f172a" />
        <Path d="M 88.8 100.5 L 91.2 100.5 L 92 105.5 L 88 105.5 Z" fill="#0f172a" />
      </Svg>

      {/* Top Header Overlay with Apple HIG Typography (Legible 11.5pt font) */}
      <View style={styles.hudHeaderOverlay}>
        <Text style={[styles.hudBrand, { color: strokeColor }]}>DEVOPS HERO</Text>
        <Text style={[styles.hudStatus, { color: labelColor }]}>{statusLabel}</Text>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: 156,
    height: 142,
    borderRadius: 16,
    borderWidth: 1.2,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.35,
    shadowRadius: 16,
    elevation: 8,
    flexShrink: 0,
    position: 'relative',
    overflow: 'hidden',
  },
  hudHeaderOverlay: {
    position: 'absolute',
    top: 7,
    left: 12,
    right: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    pointerEvents: 'none',
  },
  hudBrand: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.6,
  },
  hudStatus: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
});
