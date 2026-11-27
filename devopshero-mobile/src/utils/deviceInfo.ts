import { useState, useEffect } from 'react';
import { Platform, Dimensions, PixelRatio, StatusBar, ScaledSize } from 'react-native';

export type DeviceType = 'desktop' | 'tablet' | 'mobile';

export interface DeviceInfo {
  deviceType: DeviceType;
  isDesktop: boolean;
  isTablet: boolean;
  isMobile: boolean;
  isWeb: boolean;
  isTouchDevice: boolean;
  osName: string;
  osVersion: string;
  modelName: string;
  isIPhone: boolean;
  hasDynamicIsland: boolean;
  hasNotch: boolean;
  hasHomeIndicator: boolean;
  screenWidth: number;
  screenHeight: number;
  scale: number;
  insets: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  summary: string;
  badgeLabel: string;
}

/**
 * Automatically detects whether the runtime environment is Desktop, Tablet, or Mobile.
 * Evaluates Platform OS, Navigator User-Agent (Web/Browser), pointer precision,
 * viewport dimensions, and Apple viewport metrics.
 */
export function detectDevice(overrideWindow?: { width: number; height: number }): DeviceInfo {
  const windowDims = overrideWindow || Dimensions.get('window');
  const width = windowDims.width;
  const height = windowDims.height;
  const scale = PixelRatio.get();

  const isIOS = Platform.OS === 'ios';
  const isAndroid = Platform.OS === 'android';
  const isWeb = Platform.OS === 'web';
  const isNativeDesktop = Platform.OS === 'macos' || Platform.OS === 'windows';

  // Check for web browser navigator if available
  const hasNavigator = typeof navigator !== 'undefined';
  const ua = hasNavigator ? navigator.userAgent || '' : '';

  let osName = isIOS ? 'iOS' : isAndroid ? 'Android' : Platform.OS;
  let osVersion = String(Platform.Version || '');

  // Detect pointer capability (mouse/trackpad vs touch)
  let isTouchDevice = isIOS || isAndroid;
  if (typeof window !== 'undefined' && window.matchMedia) {
    if (window.matchMedia('(pointer: coarse)').matches) {
      isTouchDevice = true;
    } else if (window.matchMedia('(pointer: fine)').matches) {
      isTouchDevice = false;
    }
  }

  // Refine OS Name in Web/Desktop environments
  if (isWeb) {
    if (/Macintosh|Mac OS X/i.test(ua)) {
      osName = 'macOS';
    } else if (/Windows NT/i.test(ua)) {
      osName = 'Windows';
    } else if (/CrOS/i.test(ua)) {
      osName = 'ChromeOS';
    } else if (/Linux/i.test(ua) && !/Android/i.test(ua)) {
      osName = 'Linux';
    } else if (/Android/i.test(ua)) {
      osName = 'Android (Web)';
    } else if (/iPhone|iPad|iPod/i.test(ua)) {
      osName = 'iOS (Web)';
    } else {
      osName = 'Navegador Web';
    }
  }

  // Determine Device Type: Desktop vs Tablet vs Mobile
  let deviceType: DeviceType = 'mobile';
  let isDesktop = false;
  let isTablet = false;
  let isMobile = false;

  const isPad = isIOS && Boolean((Platform as { isPad?: boolean }).isPad);
  const minDim = Math.min(width, height);

  if (isNativeDesktop) {
    deviceType = 'desktop';
    isDesktop = true;
  } else if (isWeb) {
    // In web environment, check user agent and viewport width
    const isMobileUA = /iPhone|iPod|Android.*Mobile|Windows Phone|BlackBerry/i.test(ua);
    const isTabletUA = /iPad|Android(?!.*Mobile)|Tablet/i.test(ua);

    if (isMobileUA || width < 768) {
      deviceType = 'mobile';
      isMobile = true;
    } else if (isTabletUA || (width >= 768 && width < 1024)) {
      deviceType = 'tablet';
      isTablet = true;
    } else {
      // 1024px or higher on web is desktop
      deviceType = 'desktop';
      isDesktop = true;
    }
  } else if (isIOS) {
    if (isPad || minDim >= 768) {
      deviceType = 'tablet';
      isTablet = true;
    } else {
      deviceType = 'mobile';
      isMobile = true;
    }
  } else if (isAndroid) {
    if (minDim >= 600) {
      deviceType = 'tablet';
      isTablet = true;
    } else {
      deviceType = 'mobile';
      isMobile = true;
    }
  }

  let modelName = 'Dispositivo Móvel';
  let hasDynamicIsland = false;
  let hasNotch = false;
  let hasHomeIndicator = false;
  let topInset = 20;
  let bottomInset = 0;

  if (isDesktop) {
    modelName = `Desktop (${osName})`;
    topInset = 16;
    bottomInset = 16;
    hasHomeIndicator = false;
  } else if (isTablet) {
    modelName = isIOS ? 'Apple iPad' : `Tablet (${osName})`;
    topInset = isIOS ? 24 : 16;
    bottomInset = 20;
    hasHomeIndicator = isIOS;
  } else if (isIOS) {
    // iPhone detection based on viewport points
    const portraitHeight = Math.max(width, height);
    hasHomeIndicator = portraitHeight >= 780;

    if (portraitHeight >= 956) {
      modelName = 'iPhone 17 Pro Max / 16 Pro Max';
      hasDynamicIsland = true;
      topInset = 62;
      bottomInset = 38;
    } else if (portraitHeight >= 932) {
      modelName = 'iPhone 15 Pro Max / 14 Pro Max';
      hasDynamicIsland = true;
      topInset = 59;
      bottomInset = 34;
    } else if (portraitHeight >= 926) {
      modelName = 'iPhone 13 Pro Max / 12 Pro Max';
      hasNotch = true;
      topInset = 47;
      bottomInset = 34;
    } else if (portraitHeight >= 896) {
      modelName = scale === 3 ? 'iPhone 11 Pro Max / XS Max' : 'iPhone 11 / XR';
      hasNotch = true;
      topInset = 48;
      bottomInset = 34;
    } else if (portraitHeight >= 874) {
      modelName = 'iPhone 17 Pro / 16 Pro';
      hasDynamicIsland = true;
      topInset = 60;
      bottomInset = 36;
    } else if (portraitHeight >= 852) {
      modelName = 'iPhone 15 Pro / 14 Pro';
      hasDynamicIsland = true;
      topInset = 59;
      bottomInset = 34;
    } else if (portraitHeight >= 844) {
      modelName = 'iPhone 14 / 13 / 12 Pro';
      hasNotch = true;
      topInset = 47;
      bottomInset = 34;
    } else if (portraitHeight >= 812) {
      modelName = 'iPhone 13 mini / 11 Pro / X';
      hasNotch = true;
      topInset = 44;
      bottomInset = 34;
    } else if (portraitHeight >= 667) {
      modelName = 'iPhone SE (Touch ID)';
      topInset = 20;
      bottomInset = 0;
    } else {
      modelName = 'iPhone (Compacto)';
      topInset = 20;
      bottomInset = 0;
    }
  } else if (isAndroid) {
    modelName = 'Smartphone Android';
    topInset = StatusBar.currentHeight ? StatusBar.currentHeight : 24;
    bottomInset = 16;
  }

  const badgeLabel = isDesktop ? '🖥️ DESKTOP' : isTablet ? '📟 TABLET' : '📱 MOBILE';
  const summary = `${badgeLabel} · ${modelName} · ${Math.round(width)}x${Math.round(height)} @${scale}x`;

  return {
    deviceType,
    isDesktop,
    isTablet,
    isMobile,
    isWeb,
    isTouchDevice,
    osName,
    osVersion,
    modelName,
    isIPhone: isIOS && !isPad,
    hasDynamicIsland,
    hasNotch,
    hasHomeIndicator,
    screenWidth: width,
    screenHeight: height,
    scale,
    insets: {
      top: topInset,
      bottom: bottomInset,
      left: 0,
      right: 0,
    },
    summary,
    badgeLabel,
  };
}

export const CURRENT_DEVICE = detectDevice();

/**
 * React hook that dynamically detects and updates device type when screen dimensions change
 * (e.g. browser resizing, device orientation change, iPad split view).
 */
export function useDeviceInfo(): DeviceInfo {
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo>(CURRENT_DEVICE);

  useEffect(() => {
    const handler = ({ window }: { window: ScaledSize }) => {
      setDeviceInfo(detectDevice({ width: window.width, height: window.height }));
    };

    const subscription = Dimensions.addEventListener('change', handler);
    return () => {
      subscription?.remove();
    };
  }, []);

  return deviceInfo;
}
