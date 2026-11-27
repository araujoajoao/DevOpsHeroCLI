import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  Image,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Dimensions,
  Modal,
  Animated,
} from 'react-native';
import Svg, { Path } from 'react-native-svg';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { ThemeColors } from '../theme/colors';
import { ThemeMode } from '../types';
import {
  generateVerificationCode,
  sendVerificationEmail,
} from '../services/emailjsService';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

/** Official Google 4-Color Vector SVG Icon */
export const GoogleIcon: React.FC<{ size?: number }> = ({ size = 20 }) => (
  <Svg width={size} height={size} viewBox="0 0 24 24">
    <Path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.65v3h3.88c2.27-2.09 3.665-5.17 3.665-9.09z" />
    <Path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.26v3.1C3.25 21.36 7.34 24 12 24z" />
    <Path fill="#FBBC05" d="M5.28 14.32c-.25-.72-.38-1.49-.38-2.32s.13-1.6.38-2.32V6.58H1.26C.46 8.17 0 9.97 0 12s.46 3.83 1.26 5.42l4.02-3.1z" />
    <Path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.25 2.64 1.26 6.58l4.02 3.1c.95-2.83 3.6-4.93 6.72-4.93z" />
  </Svg>
);

/** Official GitHub Octocat Vector SVG Icon */
export const GitHubIcon: React.FC<{ size?: number; color?: string }> = ({ size = 20, color = '#FFFFFF' }) => (
  <Svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <Path fillRule="evenodd" clipRule="evenodd" d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
  </Svg>
);

interface AuthScreenProps {
  theme: ThemeMode;
  onToggleTheme: () => void;
  onAuthSuccess: (data: {
    userName: string;
    email: string;
    role: string;
  }) => void;
}

type ScreenMode = 'welcome' | 'form' | 'verify_otp';
type AuthMode = 'register' | 'login';

/**
 * Official DevOpsHero Circular App Emblem with Apple Liquid Glass Sheen
 */
const BrandEmblem: React.FC<{ size?: number; isDark?: boolean }> = ({ size = 104, isDark = true }) => {
  const radius = Math.round(size / 2);

  return (
    <View style={[styles.emblemContainer, { width: size, height: size }]}>
      <View
        style={[
          styles.emblemIconWrapper,
          {
            width: size,
            height: size,
            borderRadius: radius,
            borderWidth: 2,
            borderColor: isDark ? 'rgba(158, 133, 255, 0.45)' : 'rgba(158, 133, 255, 0.35)',
            backgroundColor: isDark ? '#0B0F19' : '#FFFFFF',
          },
        ]}
      >
        <Image
          source={require('../../assets/icon-circle.png')}
          style={{
            width: size,
            height: size,
            borderRadius: radius,
          }}
          resizeMode="cover"
        />

        {/* Specular Liquid Glass Curved Lens Reflection */}
        <LinearGradient
          colors={
            isDark
              ? ['rgba(255, 255, 255, 0.35)', 'rgba(255, 255, 255, 0.04)', 'transparent']
              : ['rgba(255, 255, 255, 0.55)', 'rgba(255, 255, 255, 0.10)', 'transparent']
          }
          start={{ x: 0.1, y: 0 }}
          end={{ x: 0.9, y: 0.8 }}
          style={StyleSheet.absoluteFill}
          pointerEvents="none"
        />
      </View>
    </View>
  );
};

export const AuthScreen: React.FC<AuthScreenProps> = ({
  theme,
  onToggleTheme,
  onAuthSuccess,
}) => {
  const isDark = theme === 'dark';

  const [screenMode, setScreenMode] = useState<ScreenMode>('welcome');
  const [authMode, setAuthMode] = useState<AuthMode>('login');

  // Apple iOS 27 Fluid Entrance Transitions
  const splashOpacity = useRef(new Animated.Value(1)).current;
  const splashScale = useRef(new Animated.Value(1)).current;
  const formOpacity = useRef(new Animated.Value(0)).current;
  const formTranslateY = useRef(new Animated.Value(20)).current;

  // Auto-transition from loading splash to login screen with fluid crossfade
  useEffect(() => {
    if (screenMode === 'welcome') {
      const timer = setTimeout(() => {
        Animated.parallel([
          Animated.timing(splashOpacity, {
            toValue: 0,
            duration: 360,
            useNativeDriver: true,
          }),
          Animated.timing(splashScale, {
            toValue: 1.06,
            duration: 360,
            useNativeDriver: true,
          }),
          Animated.timing(formOpacity, {
            toValue: 1,
            duration: 420,
            useNativeDriver: true,
          }),
          Animated.spring(formTranslateY, {
            toValue: 0,
            tension: 130,
            friction: 11,
            useNativeDriver: true,
          }),
        ]).start(() => {
          setAuthMode('login');
          setScreenMode('form');
        });
      }, 1300);
      return () => clearTimeout(timer);
    }
  }, []);

  // Form Fields
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(true);

  // OTP Verification State (EmailJS)
  const [generatedCode, setGeneratedCode] = useState('');
  const [inputCode, setInputCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState<{
    type: 'success' | 'error' | 'info';
    text: string;
  } | null>(null);

  const triggerHaptic = (style: Haptics.ImpactFeedbackStyle = Haptics.ImpactFeedbackStyle.Light) => {
    try {
      Haptics.impactAsync(style);
    } catch (_) {}
  };

  const validateEmail = (mail: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail.trim());
  };

  // Step 1: Submit Form (Sign Up with EmailJS dispatch, or direct Sign In)
  const handleSubmitForm = async () => {
    triggerHaptic(Haptics.ImpactFeedbackStyle.Medium);

    const cleanUser = username.trim();
    const cleanEmail = email.trim();
    const cleanPass = password.trim();

    if (!cleanUser) {
      setFeedback({ type: 'error', text: 'Informe um nome de usuário (handle de operador).' });
      return;
    }

    if (authMode === 'register') {
      if (!cleanEmail || !validateEmail(cleanEmail)) {
        setFeedback({ type: 'error', text: 'Informe um endereço de e-mail válido para validação.' });
        return;
      }
      if (cleanPass.length < 4) {
        setFeedback({ type: 'error', text: 'A senha de acesso deve ter pelo menos 4 caracteres.' });
        return;
      }
      if (!agreeTerms) {
        setFeedback({ type: 'error', text: 'É necessário concordar com os termos para continuar.' });
        return;
      }

      // Generate 6-digit OTP and send via EmailJS
      setIsLoading(true);
      setFeedback(null);

      const code = generateVerificationCode();
      setGeneratedCode(code);

      try {
        const result = await sendVerificationEmail({
          toEmail: cleanEmail,
          toName: cleanUser,
          code,
        });

        setIsLoading(false);

        if (result.success) {
          try {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          } catch (_) {}

          setScreenMode('verify_otp');
          if (result.simulated) {
            setFeedback({
              type: 'info',
              text: `ℹ️ [Modo Simulado]: Código de validação é ${code}.`,
            });
          } else {
            setFeedback({
              type: 'success',
              text: `Código de verificação enviado para ${cleanEmail}!`,
            });
          }
        } else {
          try {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
          } catch (_) {}
          setFeedback({ type: 'error', text: result.message });
        }
      } catch (err: any) {
        setIsLoading(false);
        setFeedback({
          type: 'error',
          text: `Erro ao enviar e-mail: ${err?.message || 'Falha de conexão.'}`,
        });
      }
    } else {
      // Login Direct
      if (cleanPass.length < 4) {
        setFeedback({ type: 'error', text: 'Informe sua senha de operador.' });
        return;
      }

      try {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } catch (_) {}

      onAuthSuccess({
        userName: cleanUser,
        email: cleanEmail || `${cleanUser}@devopshero.io`,
        role: 'DevOps Engineer · Nível 2',
      });
    }
  };

  // Step 2: Validate EmailJS 6-Digit OTP Code
  const handleVerifyOtp = () => {
    triggerHaptic(Haptics.ImpactFeedbackStyle.Medium);
    const cleanInput = inputCode.trim();

    if (!cleanInput) {
      setFeedback({ type: 'error', text: 'Digite o código de 6 dígitos recebido por e-mail.' });
      return;
    }

    if (cleanInput !== generatedCode) {
      try {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      } catch (_) {}
      setFeedback({
        type: 'error',
        text: 'Código incorreto. Verifique seu e-mail ou clique em reenviar.',
      });
      return;
    }

    // Success! Authenticate user
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (_) {}

    onAuthSuccess({
      userName: username.trim(),
      email: email.trim(),
      role: 'DevOps Engineer · SRE',
    });
  };

  // Resend Verification Email via EmailJS
  const handleResendCode = async () => {
    triggerHaptic();
    setIsLoading(true);
    const newCode = generateVerificationCode();
    setGeneratedCode(newCode);

    const result = await sendVerificationEmail({
      toEmail: email.trim(),
      toName: username.trim(),
      code: newCode,
    });

    setIsLoading(false);

    if (result.success) {
      try {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      } catch (_) {}

      if (result.simulated) {
        setFeedback({
          type: 'info',
          text: `ℹ️ [Novo código simulado]: ${newCode}`,
        });
      } else {
        setFeedback({
          type: 'success',
          text: `Novo código reenviado com sucesso para ${email.trim()}!`,
        });
      }
    }
  };

  // SSO Modal State (Google / GitHub)
  const [ssoProvider, setSsoProvider] = useState<'Google' | 'GitHub' | null>(null);
  const [ssoLoading, setSsoLoading] = useState(false);
  const [githubUserInput, setGithubUserInput] = useState('');
  const [githubProfile, setGithubProfile] = useState<{
    login: string;
    name?: string;
    avatar_url?: string;
    bio?: string;
    public_repos?: number;
  } | null>(null);
  const [googleEmailInput, setGoogleEmailInput] = useState('joao.araujo@gmail.com');

  const openSsoModal = (provider: 'Google' | 'GitHub') => {
    triggerHaptic(Haptics.ImpactFeedbackStyle.Medium);
    setSsoProvider(provider);
    setFeedback(null);
    if (provider === 'GitHub' && !githubProfile) {
      setGithubUserInput('araujoajoao');
      handleVerifyGitHub('araujoajoao');
    }
  };

  const handleVerifyGitHub = async (userToVerify?: string) => {
    const targetUser = (userToVerify || githubUserInput || 'araujoajoao').trim().replace(/^@/, '');
    if (!targetUser) return;

    setSsoLoading(true);
    try {
      const response = await fetch(`https://api.github.com/users/${targetUser}`, {
        headers: { 'User-Agent': 'DevOpsHero-Mobile' },
      });
      if (response.ok) {
        const data = await response.json();
        setGithubProfile({
          login: data.login || targetUser,
          name: data.name || targetUser,
          avatar_url: data.avatar_url,
          bio: data.bio || 'DevOps & Cloud Engineer',
          public_repos: data.public_repos || 0,
        });
      } else {
        setGithubProfile({
          login: targetUser,
          name: targetUser,
          avatar_url: `https://github.com/${targetUser}.png`,
          bio: 'DevOps & SRE Practitioner',
          public_repos: 12,
        });
      }
    } catch (_) {
      setGithubProfile({
        login: targetUser,
        name: targetUser,
        avatar_url: `https://github.com/${targetUser}.png`,
        bio: 'DevOps & Cloud Practitioner',
        public_repos: 10,
      });
    } finally {
      setSsoLoading(false);
    }
  };

  const handleConfirmGitHubLogin = () => {
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (_) {}
    const cleanUser = githubProfile?.login || githubUserInput.trim() || 'github_operator';
    onAuthSuccess({
      userName: cleanUser,
      email: `${cleanUser}@users.noreply.github.com`,
      role: 'GitHub Actions & SRE Operator',
    });
    setSsoProvider(null);
  };

  const handleFillFormFromGitHub = () => {
    triggerHaptic(Haptics.ImpactFeedbackStyle.Light);
    const cleanUser = githubProfile?.login || githubUserInput.trim() || 'github_operator';
    setUsername(cleanUser);
    setEmail(`${cleanUser}@users.noreply.github.com`);
    setSsoProvider(null);
    setFeedback({
      type: 'success',
      text: `✅ Dados de @${cleanUser} importados do GitHub para o formulário!`,
    });
  };

  const handleConfirmGoogleLogin = (emailChoice?: string) => {
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (_) {}
    const chosenEmail = (emailChoice || googleEmailInput).trim() || 'joao.araujo@gmail.com';
    const computedUser = chosenEmail.split('@')[0].replace(/[^a-zA-Z0-9_]/g, '_');
    onAuthSuccess({
      userName: computedUser,
      email: chosenEmail,
      role: 'Google Cloud Certified DevOps · SRE',
    });
    setSsoProvider(null);
  };

  const handleFillFormFromGoogle = (emailChoice?: string) => {
    triggerHaptic(Haptics.ImpactFeedbackStyle.Light);
    const chosenEmail = (emailChoice || googleEmailInput).trim() || 'joao.araujo@gmail.com';
    const computedUser = chosenEmail.split('@')[0].replace(/[^a-zA-Z0-9_]/g, '_');
    setUsername(computedUser);
    setEmail(chosenEmail);
    setSsoProvider(null);
    setFeedback({
      type: 'success',
      text: `✅ Conta Google ${chosenEmail} importada para o formulário!`,
    });
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={[
        styles.container,
        { backgroundColor: 'transparent' },
      ]}
    >
      {/* Background Decor (Translucent Deep Gradient + Floating Diagonal Pills) */}
      <View style={StyleSheet.absoluteFill} pointerEvents="none">
        <LinearGradient
          colors={
            isDark
              ? ['rgba(19, 22, 39, 0.40)', 'rgba(30, 27, 75, 0.30)', 'rgba(46, 16, 101, 0.25)', 'rgba(19, 22, 39, 0.40)']
              : ['rgba(248, 250, 252, 0.50)', 'rgba(238, 242, 255, 0.40)', 'rgba(224, 231, 255, 0.35)', 'rgba(248, 250, 252, 0.50)']
          }
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={StyleSheet.absoluteFill}
        />

        {/* Floating Diagonal Translucent Capsules */}
        <View
          style={[
            styles.floatingPill1,
            {
              backgroundColor: isDark
                ? 'rgba(110, 86, 207, 0.22)'
                : 'rgba(110, 86, 207, 0.08)',
            },
          ]}
        />
        <View
          style={[
            styles.floatingPill2,
            {
              backgroundColor: isDark
                ? 'rgba(158, 133, 255, 0.16)'
                : 'rgba(158, 133, 255, 0.07)',
            },
          ]}
        />
        <View
          style={[
            styles.floatingPill3,
            {
              backgroundColor: isDark
                ? 'rgba(79, 70, 229, 0.18)'
                : 'rgba(79, 70, 229, 0.06)',
            },
          ]}
        />
        <View
          style={[
            styles.streakLine1,
            {
              backgroundColor: isDark
                ? 'rgba(255, 255, 255, 0.15)'
                : 'rgba(0, 0, 0, 0.06)',
            },
          ]}
        />
        <View
          style={[
            styles.streakLine2,
            {
              backgroundColor: isDark
                ? 'rgba(255, 255, 255, 0.12)'
                : 'rgba(0, 0, 0, 0.04)',
            },
          ]}
        />
      </View>

      {/* =========================================================================
          SCREEN A: Loading / Splash Screen (Somente a logo centralizada)
          ========================================================================= */}
      {screenMode === 'welcome' && (
        <Animated.View
          style={[
            styles.splashLoadingContainer,
            {
              opacity: splashOpacity,
              transform: [{ scale: splashScale }],
            },
          ]}
          pointerEvents="box-none"
        >
          <View style={styles.splashLogoWrapper} pointerEvents="none">
            <BrandEmblem size={144} isDark={isDark} />
            <ActivityIndicator
              size="small"
              color={isDark ? '#9E85FF' : '#6366F1'}
              style={{ marginTop: 28 }}
            />
          </View>
        </Animated.View>
      )}

      {/* =========================================================================
          SCREEN B: Auth Form Sheet (Fidelity to Right Screen in Reference)
          ========================================================================= */}
      {screenMode === 'form' && (
        <Animated.View
          style={[
            { flex: 1, width: '100%' },
            {
              opacity: formOpacity,
              transform: [{ translateY: formTranslateY }],
            },
          ]}
        >
          <ScrollView
            contentContainerStyle={styles.formScrollContent}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {/* Top Header Row with Back Button, Emblem and Theme */}
            <View style={styles.formHeaderRow}>
              <TouchableOpacity
                style={styles.headerBackBtn}
                onPress={() => {
                  triggerHaptic();
                  onAuthSuccess({
                    userName: 'Visitante',
                    email: '',
                    role: 'Visitante (sem histórico de pontos)',
                  });
                }}
                activeOpacity={0.7}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                accessibilityLabel="Entrar como visitante"
              >
                <Text
                  style={[
                    styles.headerBackText,
                    { color: isDark ? '#FFFFFF' : '#0F172A' },
                  ]}
                >
                  ‹
                </Text>
              </TouchableOpacity>

            <BrandEmblem size={52} isDark={isDark} />

            <TouchableOpacity
              style={[
                styles.themeToggleBtn,
                {
                  backgroundColor: isDark
                    ? 'rgba(255, 255, 255, 0.12)'
                    : 'rgba(0, 0, 0, 0.06)',
                  borderColor: isDark
                    ? 'rgba(255, 255, 255, 0.20)'
                    : 'rgba(0, 0, 0, 0.10)',
                },
              ]}
              onPress={onToggleTheme}
              activeOpacity={0.7}
              hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            >
              <Text style={styles.themeToggleIcon}>{theme === 'dark' ? '☀️' : '🌙'}</Text>
            </TouchableOpacity>
          </View>

          {/* Curved Bottom Sheet Card */}
          <View
            style={[
              styles.formSheetCard,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.70)',
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

            {/* Specular Liquid Glass Sheen (-45° Glare) */}
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
            {/* Heading */}
            <Text
              style={[
                styles.sheetHeading,
                { color: isDark ? '#FFFFFF' : '#0F172A' },
              ]}
            >
              hello!
            </Text>
            <Text style={styles.sheetSubheading}>
              {authMode === 'register'
                ? 'Create an account to start practicing'
                : 'Sign in to access your CLI terminal'}
            </Text>

            {/* Feedback Alert Banner */}
            {feedback && (
              <View
                style={[
                  styles.feedbackBanner,
                  {
                    backgroundColor:
                      feedback.type === 'success'
                        ? 'rgba(0, 223, 137, 0.12)'
                        : feedback.type === 'info'
                        ? 'rgba(158, 133, 255, 0.12)'
                        : 'rgba(251, 113, 133, 0.12)',
                    borderColor:
                      feedback.type === 'success'
                        ? '#00DF89'
                        : feedback.type === 'info'
                        ? '#9E85FF'
                        : '#FB7185',
                  },
                ]}
              >
                <Text
                  style={[
                    styles.feedbackBannerText,
                    {
                      color:
                        feedback.type === 'success'
                          ? '#00DF89'
                          : feedback.type === 'info'
                          ? '#9E85FF'
                          : '#FB7185',
                    },
                  ]}
                >
                  {feedback.text}
                </Text>
              </View>
            )}

            {/* Field 1: Username with Icon */}
            <View
              style={[
                styles.inputWrapper,
                {
                  backgroundColor: isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(255, 255, 255, 0.65)',
                  borderColor: isDark ? 'rgba(255, 255, 255, 0.18)' : 'rgba(0, 0, 0, 0.08)',
                },
              ]}
            >
              <Text style={styles.inputLeftIcon}>👤</Text>
              <TextInput
                style={[
                  styles.textInput,
                  { color: isDark ? '#FFFFFF' : '#0F172A' },
                ]}
                placeholder="Username"
                placeholderTextColor={isDark ? '#8A99AD' : '#94A3B8'}
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            {/* Field 2: Email with Icon */}
            {authMode === 'register' && (
              <View
                style={[
                  styles.inputWrapper,
                  {
                    backgroundColor: isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(255, 255, 255, 0.65)',
                    borderColor: isDark ? 'rgba(255, 255, 255, 0.18)' : 'rgba(0, 0, 0, 0.08)',
                  },
                ]}
              >
                <Text style={styles.inputLeftIcon}>✉️</Text>
                <TextInput
                  style={[
                    styles.textInput,
                    { color: isDark ? '#FFFFFF' : '#0F172A' },
                  ]}
                  placeholder="Email"
                  placeholderTextColor={isDark ? '#8A99AD' : '#94A3B8'}
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  keyboardType="email-address"
                  autoCorrect={false}
                />
              </View>
            )}

            {/* Field 3: Password with Left Shield & Right Eye Toggle */}
            <View
              style={[
                styles.inputWrapper,
                {
                  backgroundColor: isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(255, 255, 255, 0.65)',
                  borderColor: isDark ? 'rgba(255, 255, 255, 0.18)' : 'rgba(0, 0, 0, 0.08)',
                },
              ]}
            >
              <Text style={styles.inputLeftIcon}>🛡️</Text>
              <TextInput
                style={[
                  styles.textInput,
                  { color: isDark ? '#FFFFFF' : '#0F172A' },
                ]}
                placeholder="Password"
                placeholderTextColor={isDark ? '#64748B' : '#94A3B8'}
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoCorrect={false}
              />
              <TouchableOpacity
                style={styles.eyeToggleBtn}
                onPress={() => {
                  triggerHaptic();
                  setShowPassword(!showPassword);
                }}
                activeOpacity={0.7}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                accessibilityLabel={showPassword ? 'Ocultar senha' : 'Exibir senha'}
              >
                <Text style={styles.eyeToggleIcon}>{showPassword ? '👁️' : '🔒'}</Text>
              </TouchableOpacity>
            </View>

            {/* Checkbox: I agree to terms and conditions */}
            {authMode === 'register' && (
              <TouchableOpacity
                style={styles.termsRow}
                onPress={() => {
                  triggerHaptic();
                  setAgreeTerms(!agreeTerms);
                }}
                activeOpacity={0.8}
              >
                <View
                  style={[
                    styles.termsCheckbox,
                    {
                      borderColor: agreeTerms ? '#9E85FF' : (isDark ? '#475569' : '#CBD5E1'),
                      backgroundColor: agreeTerms ? '#9E85FF' : 'transparent',
                    },
                  ]}
                >
                  {agreeTerms && <Text style={styles.termsCheckmark}>✓</Text>}
                </View>
                <Text style={[styles.termsText, { color: isDark ? '#94A3B8' : '#64748B' }]}>
                  I agree to the <Text style={{ color: '#9E85FF', fontWeight: 'bold' }}>terms and conditions</Text>
                </Text>
              </TouchableOpacity>
            )}

            {/* Primary Action Button: Sign Up / Sign In */}
            <TouchableOpacity
              style={styles.primaryAuthBtn}
              onPress={handleSubmitForm}
              disabled={isLoading}
              activeOpacity={0.88}
              accessibilityRole="button"
              accessibilityLabel={authMode === 'register' ? 'Sign Up' : 'Sign In'}
            >
              {isLoading ? (
                <ActivityIndicator color="#0B0F19" size="small" />
              ) : (
                <Text style={styles.primaryAuthBtnText}>
                  {authMode === 'register' ? 'Sign Up' : 'Sign In'}
                </Text>
              )}
            </TouchableOpacity>

            {/* Divider 'or' */}
            <View style={styles.dividerRow}>
              <View style={[styles.dividerLine, { backgroundColor: isDark ? '#272E4F' : '#E2E8F0' }]} />
              <Text style={styles.dividerOrText}>or</Text>
              <View style={[styles.dividerLine, { backgroundColor: isDark ? '#272E4F' : '#E2E8F0' }]} />
            </View>

            {/* Social / DevOps SSO Buttons (Apenas GitHub e Google) */}
            <View style={styles.socialButtonsRow}>
              {/* Google Button */}
              <TouchableOpacity
                style={[
                  styles.socialBtnCard,
                  {
                    flex: 1,
                    backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : '#FFFFFF',
                    borderColor: isDark ? 'rgba(255, 255, 255, 0.16)' : '#CBD5E1',
                  },
                ]}
                onPress={() => openSsoModal('Google')}
                activeOpacity={0.82}
                accessibilityRole="button"
                accessibilityLabel="Entrar com Google"
              >
                <GoogleIcon size={19} />
                <Text style={[styles.socialBtnText, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>
                  Google
                </Text>
              </TouchableOpacity>

              {/* GitHub Button */}
              <TouchableOpacity
                style={[
                  styles.socialBtnCard,
                  {
                    flex: 1,
                    backgroundColor: isDark ? '#24292E' : '#0F172A',
                    borderColor: isDark ? 'rgba(255, 255, 255, 0.22)' : '#000000',
                  },
                ]}
                onPress={() => openSsoModal('GitHub')}
                activeOpacity={0.82}
                accessibilityRole="button"
                accessibilityLabel="Entrar com GitHub"
              >
                <GitHubIcon size={19} color="#FFFFFF" />
                <Text style={[styles.socialBtnText, { color: '#FFFFFF' }]}>
                  GitHub
                </Text>
              </TouchableOpacity>
            </View>

            <Text style={[styles.socialLabelText, { color: isDark ? '#94A3B8' : '#475569' }]}>
              Log in with your social media account
            </Text>

            {/* Bottom Toggle Between Sign Up and Sign In */}
            <TouchableOpacity
              style={styles.switchAuthModeBtn}
              onPress={() => {
                triggerHaptic();
                setAuthMode(authMode === 'register' ? 'login' : 'register');
                setFeedback(null);
              }}
              activeOpacity={0.75}
            >
              <Text style={[styles.switchAuthModeText, { color: isDark ? '#C7D2FE' : '#334155' }]}>
                {authMode === 'register' ? (
                  <>Already have an account? <Text style={{ color: isDark ? '#C7D2FE' : '#6D28D9', fontWeight: 'bold' }}>Sign In</Text></>
                ) : (
                  <>Don't have an account? <Text style={{ color: isDark ? '#C7D2FE' : '#6D28D9', fontWeight: 'bold' }}>Sign Up</Text></>
                )}
              </Text>
            </TouchableOpacity>

            {/* Quick Guest Mode Access */}
            <TouchableOpacity
              style={styles.guestLinkBtn}
              onPress={() => {
                triggerHaptic();
                onAuthSuccess({
                  userName: 'visitante',
                  email: '',
                  role: 'Visitante (sem histórico de pontos)',
                });
              }}
              activeOpacity={0.75}
            >
              <Text style={[styles.guestLinkText, { color: isDark ? '#A5B4FC' : '#64748B' }]}>
                Ou entrar como <Text style={{ color: '#00DF89', fontWeight: 'bold' }}>Visitante sem cadastro</Text> ➔
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
        </Animated.View>
      )}

      {/* =========================================================================
          SCREEN C: EmailJS 6-Digit OTP Verification Screen
          ========================================================================= */}
      {screenMode === 'verify_otp' && (
        <ScrollView
          contentContainerStyle={styles.formScrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header Row */}
          <View style={styles.formHeaderRow}>
            <TouchableOpacity
              style={styles.headerBackBtn}
              onPress={() => {
                triggerHaptic();
                setScreenMode('form');
                setFeedback(null);
              }}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.headerBackText,
                  { color: isDark ? '#FFFFFF' : '#0F172A' },
                ]}
              >
                ‹
              </Text>
            </TouchableOpacity>

            <BrandEmblem size={52} isDark={isDark} />

            <View style={{ width: 44 }} />
          </View>

          {/* OTP Card */}
          <View
            style={[
              styles.formSheetCard,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.70)',
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

            {/* Specular Liquid Glass Sheen (-45° Glare) */}
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
            <Text
              style={[
                styles.sheetHeading,
                { color: isDark ? '#FFFFFF' : '#0F172A' },
              ]}
            >
              Verify Email
            </Text>
            <Text
              style={[
                styles.sheetSubheading,
                { color: isDark ? '#94A3B8' : '#64748B' },
              ]}
            >
              Enviamos um código de verificação via EmailJS para:
            </Text>

            <View
              style={[
                styles.emailPillBadge,
                {
                  backgroundColor: isDark ? 'rgba(158, 133, 255, 0.16)' : 'rgba(158, 133, 255, 0.12)',
                  borderColor: isDark ? 'rgba(158, 133, 255, 0.35)' : 'rgba(158, 133, 255, 0.45)',
                },
              ]}
            >
              <Text style={styles.emailPillText}>✉️ {email.trim()}</Text>
            </View>

            {/* Feedback Alert */}
            {feedback && (
              <View
                style={[
                  styles.feedbackBanner,
                  {
                    backgroundColor:
                      feedback.type === 'success'
                        ? 'rgba(0, 223, 137, 0.12)'
                        : feedback.type === 'info'
                        ? 'rgba(158, 133, 255, 0.12)'
                        : 'rgba(251, 113, 133, 0.12)',
                    borderColor:
                      feedback.type === 'success'
                        ? '#00DF89'
                        : feedback.type === 'info'
                        ? '#9E85FF'
                        : '#FB7185',
                  },
                ]}
              >
                <Text
                  style={[
                    styles.feedbackBannerText,
                    {
                      color:
                        feedback.type === 'success'
                          ? '#00DF89'
                          : feedback.type === 'info'
                          ? '#9E85FF'
                          : '#FB7185',
                    },
                  ]}
                >
                  {feedback.text}
                </Text>
              </View>
            )}

            {/* 6-Digit OTP Input */}
            <View
              style={[
                styles.otpInputWrapper,
                {
                  backgroundColor: isDark ? '#161B2E' : '#F8FAFC',
                  borderColor: isDark ? '#9E85FF' : '#6C5CE7',
                },
              ]}
            >
              <TextInput
                style={[
                  styles.otpTextInput,
                  { color: isDark ? '#FFFFFF' : '#0F172A' },
                ]}
                placeholder="000000"
                placeholderTextColor={isDark ? '#475569' : '#94A3B8'}
                value={inputCode}
                onChangeText={setInputCode}
                keyboardType="number-pad"
                maxLength={6}
                autoFocus
              />
            </View>

            {/* Verify Code Button */}
            <TouchableOpacity
              style={styles.primaryAuthBtn}
              onPress={handleVerifyOtp}
              activeOpacity={0.88}
            >
              <Text style={styles.primaryAuthBtnText}>Confirmar e Entrar ↵</Text>
            </TouchableOpacity>

            {/* Resend Code Link */}
            <TouchableOpacity
              style={styles.resendBtn}
              onPress={handleResendCode}
              disabled={isLoading}
              activeOpacity={0.7}
            >
              <Text style={[styles.resendBtnText, { color: isDark ? '#C7D2FE' : '#6D28D9' }]}>
                {isLoading ? 'Reenviando...' : 'Reenviar código de verificação'}
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

      {/* =========================================================================
          SSO Authentication Modal (Google / GitHub / AWS)
          ========================================================================= */}
      <Modal
        visible={ssoProvider !== null}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setSsoProvider(null)}
      >
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.modalBackdrop}
        >
          <TouchableOpacity
            style={StyleSheet.absoluteFill}
            onPress={() => setSsoProvider(null)}
            activeOpacity={1}
          />

          <View
            style={[
              styles.modalSheetCard,
              {
                backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.75)',
                borderColor: isDark ? 'rgba(158, 133, 255, 0.45)' : 'rgba(255, 255, 255, 0.95)',
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

            {/* Specular Liquid Glass Sheen (-45° Glare) */}
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
            {/* Grabber Handle */}
            <View
              style={[
                styles.modalGrabber,
                { backgroundColor: isDark ? 'rgba(255, 255, 255, 0.25)' : '#CBD5E1' },
              ]}
            />

            {/* Modal Header */}
            <View style={styles.modalHeaderRow}>
              <View style={styles.modalHeaderTitleGroup}>
                {ssoProvider === 'Google' && <GoogleIcon size={24} />}
                {ssoProvider === 'GitHub' && <GitHubIcon size={24} color={isDark ? '#FFFFFF' : '#0F172A'} />}
                <Text
                  style={[
                    styles.modalHeaderTitle,
                    { color: isDark ? '#FFFFFF' : '#0F172A' },
                  ]}
                >
                  {ssoProvider === 'Google' && 'Google Workspace'}
                  {ssoProvider === 'GitHub' && 'GitHub Developer SSO'}
                </Text>
              </View>

              <TouchableOpacity
                style={[
                  styles.modalCloseBtn,
                  { backgroundColor: isDark ? 'rgba(255, 255, 255, 0.10)' : 'rgba(0, 0, 0, 0.06)' },
                ]}
                onPress={() => setSsoProvider(null)}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                accessibilityLabel="Fechar"
              >
                <Text style={[styles.modalCloseText, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>✕</Text>
              </TouchableOpacity>
            </View>

            {/* Content for Google */}
            {ssoProvider === 'Google' && (
              <View style={styles.ssoModalContent}>
                <Text style={[styles.ssoSubtitle, { color: isDark ? '#A5B4FC' : '#64748B' }]}>
                  Autenticação rápida com conta Google para acesso instantâneo aos labs.
                </Text>

                {/* Quick Account 1 */}
                <TouchableOpacity
                  style={[
                    styles.ssoAccountCard,
                    {
                      backgroundColor: isDark ? 'rgba(30, 36, 68, 0.60)' : '#F8FAFC',
                      borderColor: isDark ? 'rgba(158, 133, 255, 0.30)' : '#E2E8F0',
                    },
                  ]}
                  onPress={() => handleConfirmGoogleLogin('joao.araujo@gmail.com')}
                  activeOpacity={0.82}
                >
                  <View style={styles.ssoAccountAvatar}>
                    <Text style={{ fontSize: 22 }}>👨‍💻</Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.ssoAccountName, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>
                      João Araújo
                    </Text>
                    <Text style={[styles.ssoAccountEmail, { color: isDark ? '#A5B4FC' : '#64748B' }]}>
                      joao.araujo@gmail.com
                    </Text>
                  </View>
                  <Text style={styles.ssoAccountChevron}>➔</Text>
                </TouchableOpacity>

                {/* Quick Account 2 */}
                <TouchableOpacity
                  style={[
                    styles.ssoAccountCard,
                    {
                      backgroundColor: isDark ? 'rgba(30, 36, 68, 0.60)' : '#F8FAFC',
                      borderColor: isDark ? 'rgba(158, 133, 255, 0.30)' : '#E2E8F0',
                    },
                  ]}
                  onPress={() => handleConfirmGoogleLogin('devops.hero.cloud@gmail.com')}
                  activeOpacity={0.82}
                >
                  <View style={styles.ssoAccountAvatar}>
                    <Text style={{ fontSize: 22 }}>⚡</Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.ssoAccountName, { color: isDark ? '#FFFFFF' : '#0F172A' }]}>
                      DevOps Hero Cloud
                    </Text>
                    <Text style={[styles.ssoAccountEmail, { color: isDark ? '#A5B4FC' : '#64748B' }]}>
                      devops.hero.cloud@gmail.com
                    </Text>
                  </View>
                  <Text style={styles.ssoAccountChevron}>➔</Text>
                </TouchableOpacity>

                {/* Custom Email Input */}
                <View
                  style={[
                    styles.ssoCustomInputRow,
                    {
                      backgroundColor: isDark ? '#161B2E' : '#F8FAFC',
                      borderColor: isDark ? '#272E4F' : '#CBD5E1',
                    },
                  ]}
                >
                  <GoogleIcon size={18} />
                  <TextInput
                    style={[styles.ssoCustomInput, { color: isDark ? '#FFFFFF' : '#0F172A' }]}
                    placeholder="outro.email@gmail.com"
                    placeholderTextColor={isDark ? '#64748B' : '#94A3B8'}
                    value={googleEmailInput}
                    onChangeText={setGoogleEmailInput}
                    autoCapitalize="none"
                    keyboardType="email-address"
                  />
                </View>

                {/* Action Buttons */}
                <TouchableOpacity
                  style={styles.ssoPrimaryBtn}
                  onPress={() => handleConfirmGoogleLogin()}
                  activeOpacity={0.88}
                >
                  <Text style={styles.ssoPrimaryBtnText}>Entrar com o Google ↵</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.ssoSecondaryBtn}
                  onPress={() => handleFillFormFromGoogle()}
                  activeOpacity={0.75}
                >
                  <Text style={[styles.ssoSecondaryBtnText, { color: isDark ? '#C7D2FE' : '#4338CA' }]}>
                    📝 Preencher cadastro com esta conta
                  </Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Content for GitHub */}
            {ssoProvider === 'GitHub' && (
              <View style={styles.ssoModalContent}>
                <Text style={[styles.ssoSubtitle, { color: isDark ? '#A5B4FC' : '#64748B' }]}>
                  Conecte seu usuário do GitHub para carregar suas credenciais de operador.
                </Text>

                {/* Username Input with Live Search */}
                <View
                  style={[
                    styles.ssoCustomInputRow,
                    {
                      backgroundColor: isDark ? '#161B2E' : '#F8FAFC',
                      borderColor: isDark ? '#9E85FF' : '#7C3AED',
                    },
                  ]}
                >
                  <Text style={[styles.ssoInputPrefix, { color: isDark ? '#A5B4FC' : '#64748B' }]}>
                    github.com/
                  </Text>
                  <TextInput
                    style={[styles.ssoCustomInput, { color: isDark ? '#FFFFFF' : '#0F172A' }]}
                    placeholder="usuario (ex: araujoajoao)"
                    placeholderTextColor={isDark ? '#64748B' : '#94A3B8'}
                    value={githubUserInput}
                    onChangeText={txt => {
                      setGithubUserInput(txt);
                      setGithubProfile(null);
                    }}
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                  {ssoLoading && <ActivityIndicator color="#9E85FF" size="small" />}
                </View>

                {/* Quick Handle Chips */}
                <View style={styles.ssoChipsRow}>
                  {['araujoajoao', 'devopshero', 'octocat'].map(h => (
                    <TouchableOpacity
                      key={h}
                      style={[
                        styles.ssoChip,
                        {
                          backgroundColor: isDark ? 'rgba(158, 133, 255, 0.14)' : 'rgba(158, 133, 255, 0.10)',
                          borderColor: 'rgba(158, 133, 255, 0.35)',
                        },
                      ]}
                      onPress={() => {
                        setGithubUserInput(h);
                        handleVerifyGitHub(h);
                      }}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.ssoChipText}>@{h}</Text>
                    </TouchableOpacity>
                  ))}
                </View>

                {/* Real Profile Preview Card */}
                {githubProfile && (
                  <View
                    style={[
                      styles.githubProfilePreviewCard,
                      {
                        backgroundColor: isDark ? '#1E243E' : '#F1F5F9',
                        borderColor: isDark ? '#272E4F' : '#E2E8F0',
                      },
                    ]}
                  >
                    {githubProfile.avatar_url ? (
                      <Image
                        source={{ uri: githubProfile.avatar_url }}
                        style={styles.githubAvatarImage}
                      />
                    ) : (
                      <View style={styles.githubAvatarFallback}>
                        <GitHubIcon size={24} color="#FFFFFF" />
                      </View>
                    )}
                    <View style={{ flex: 1 }}>
                      <Text
                        style={[styles.githubPreviewName, { color: isDark ? '#FFFFFF' : '#0F172A' }]}
                        numberOfLines={1}
                      >
                        {githubProfile.name || githubProfile.login}
                      </Text>
                      <Text style={styles.githubPreviewLogin}>@{githubProfile.login}</Text>
                      {githubProfile.bio && (
                        <Text
                          style={[styles.githubPreviewBio, { color: isDark ? '#94A3B8' : '#64748B' }]}
                          numberOfLines={1}
                        >
                          {githubProfile.bio}
                        </Text>
                      )}
                    </View>
                    <View style={styles.githubRepoBadge}>
                      <Text style={styles.githubRepoBadgeText}>
                        ⭐ {githubProfile.public_repos || 0}
                      </Text>
                    </View>
                  </View>
                )}

                {/* Primary Action Button */}
                <TouchableOpacity
                  style={styles.ssoPrimaryBtn}
                  onPress={() => {
                    if (githubProfile) {
                      handleConfirmGitHubLogin();
                    } else {
                      handleVerifyGitHub();
                    }
                  }}
                  disabled={ssoLoading}
                  activeOpacity={0.88}
                >
                  {ssoLoading ? (
                    <ActivityIndicator color="#0B0F19" size="small" />
                  ) : (
                    <Text style={styles.ssoPrimaryBtnText}>
                      {githubProfile
                        ? `Entrar como @${githubProfile.login} ↵`
                        : 'Verificar e Conectar GitHub ↵'}
                    </Text>
                  )}
                </TouchableOpacity>

                {/* Form Fill Link */}
                <TouchableOpacity
                  style={styles.ssoSecondaryBtn}
                  onPress={() => handleFillFormFromGitHub()}
                  activeOpacity={0.75}
                >
                  <Text style={[styles.ssoSecondaryBtnText, { color: isDark ? '#C7D2FE' : '#4338CA' }]}>
                    📝 Preencher cadastro com dados do GitHub
                  </Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#131627',
  },

  // Floating Decorative Diagonal Pills (Matching Reference Screen A)
  floatingPill1: {
    position: 'absolute',
    top: -40,
    right: -20,
    width: 220,
    height: 85,
    borderRadius: 42,
    backgroundColor: 'rgba(110, 86, 207, 0.22)',
    transform: [{ rotate: '-45deg' }],
  },
  floatingPill2: {
    position: 'absolute',
    top: 140,
    left: -60,
    width: 260,
    height: 95,
    borderRadius: 47,
    backgroundColor: 'rgba(158, 133, 255, 0.16)',
    transform: [{ rotate: '-45deg' }],
  },
  floatingPill3: {
    position: 'absolute',
    bottom: 80,
    right: -40,
    width: 200,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(79, 70, 229, 0.18)',
    transform: [{ rotate: '-45deg' }],
  },
  streakLine1: {
    position: 'absolute',
    top: 60,
    left: 40,
    width: 120,
    height: 1.5,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    transform: [{ rotate: '-45deg' }],
  },
  streakLine2: {
    position: 'absolute',
    bottom: 220,
    left: 80,
    width: 140,
    height: 1.5,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    transform: [{ rotate: '-45deg' }],
  },

  // Emblem Styles
  emblemContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  emblemIconWrapper: {
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
    ...Platform.select({
      ios: {
        shadowColor: '#9E85FF',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.45,
        shadowRadius: 18,
      },
      android: {
        elevation: 8,
      },
    }),
  },
  emblemBar: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.35,
    shadowRadius: 4,
    elevation: 3,
  },
  emblemMiddleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  emblemNode: {
    borderColor: '#FFFFFF',
    shadowColor: '#9E85FF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.85,
    shadowRadius: 8,
    elevation: 4,
  },
  emblemMiddleBar: {
    flex: 1,
  },

  // Screen A: Loading / Splash Mode
  splashLoadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    height: '100%',
  },
  splashLogoWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  welcomeContainer: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: 'space-between',
    paddingBottom: 48,
    paddingTop: 16,
  },
  welcomeTopBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: 44,
  },
  welcomeCenterCol: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  welcomeAppName: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 32,
    fontWeight: '900',
    marginTop: 24,
    letterSpacing: 0.5,
  },
  welcomeTagline: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 8,
    letterSpacing: 0.2,
  },
  welcomeBottomActions: {
    width: '100%',
    alignItems: 'center',
  },
  getStartedBtn: {
    width: '100%',
    height: 56,
    borderRadius: 28,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 5,
  },
  getStartedBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  alreadyAccountBtn: {
    marginTop: 18,
    paddingVertical: 8,
  },
  alreadyAccountText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  guestModeBtn: {
    width: '100%',
    marginTop: 20,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 20,
    borderWidth: 1.2,
    borderColor: 'rgba(255, 255, 255, 0.20)',
    backgroundColor: 'rgba(39, 46, 79, 0.55)',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.25,
        shadowRadius: 10,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  guestModeContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  guestModeIcon: {
    fontSize: 22,
  },
  guestModeTextCol: {
    flex: 1,
  },
  guestModeTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#FFFFFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  guestModeSubtitle: {
    fontSize: 11,
    color: '#A5B4FC',
    marginTop: 2,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  guestLinkBtn: {
    marginTop: 16,
    alignItems: 'center',
    paddingVertical: 8,
  },
  guestLinkText: {
    fontSize: 12.5,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },

  // Screen B: Form Mode
  formScrollContent: {
    paddingTop: 12,
    paddingBottom: 40,
  },
  formHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 20,
    height: 60,
  },
  headerBackBtn: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerBackText: {
    fontSize: 32,
    color: '#FFFFFF',
    fontWeight: '300',
  },
  themeToggleBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
  },
  themeToggleIcon: {
    fontSize: 18,
  },
  formSheetCard: {
    borderTopLeftRadius: 34,
    borderTopRightRadius: 34,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    borderWidth: 1.2,
    paddingHorizontal: 24,
    paddingTop: 28,
    paddingBottom: 36,
    marginHorizontal: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.35,
    shadowRadius: 16,
    elevation: 8,
  },
  sheetChromaticBevel: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 1.5,
  },
  sheetHeading: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 28,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  sheetSubheading: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '500',
    color: '#94A3B8',
    marginTop: 4,
    marginBottom: 20,
  },
  feedbackBanner: {
    borderRadius: 12,
    borderWidth: 1,
    paddingHorizontal: 12,
    paddingVertical: 10,
    marginBottom: 16,
  },
  feedbackBannerText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12.5,
    fontWeight: '700',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 52,
    borderRadius: 14,
    borderWidth: 1.2,
    paddingHorizontal: 14,
    marginBottom: 14,
  },
  inputLeftIcon: {
    fontSize: 16,
    marginRight: 10,
  },
  textInput: {
    flex: 1,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14.5,
  },
  eyeToggleBtn: {
    padding: 6,
  },
  eyeToggleIcon: {
    fontSize: 16,
  },
  termsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    marginBottom: 20,
  },
  termsCheckbox: {
    width: 20,
    height: 20,
    borderRadius: 5,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  termsCheckmark: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '900',
  },
  termsText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12.5,
  },
  primaryAuthBtn: {
    height: 54,
    borderRadius: 27,
    backgroundColor: '#9E85FF',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#9E85FF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.45,
    shadowRadius: 14,
    elevation: 8,
  },
  primaryAuthBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 16,
    fontWeight: '900',
    color: '#0B0F19',
    letterSpacing: 0.5,
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
  },
  dividerOrText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    color: '#64748B',
    marginHorizontal: 14,
  },
  socialButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 10,
    marginBottom: 14,
  },
  socialBtnCard: {
    flex: 1,
    height: 48,
    borderRadius: 14,
    borderWidth: 1.2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingHorizontal: 8,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.15,
        shadowRadius: 4,
      },
      android: {
        elevation: 3,
      },
    }),
  },
  socialBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
  socialSquareBtn: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 3,
  },
  socialIconText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '900',
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.70)',
    justifyContent: 'flex-end',
  },
  modalSheetCard: {
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    borderWidth: 1.2,
    paddingHorizontal: 22,
    paddingTop: 12,
    paddingBottom: Platform.OS === 'ios' ? 44 : 28,
    maxHeight: SCREEN_HEIGHT * 0.85,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.45,
    shadowRadius: 20,
    elevation: 12,
  },
  modalGrabber: {
    width: 38,
    height: 4.5,
    borderRadius: 2.5,
    alignSelf: 'center',
    marginBottom: 14,
  },
  modalHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
    height: 44,
  },
  modalHeaderTitleGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  modalHeaderTitle: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 17,
    fontWeight: '800',
    letterSpacing: 0.3,
  },
  modalCloseBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalCloseText: {
    fontSize: 16,
    fontWeight: '700',
  },
  ssoModalContent: {
    paddingTop: 6,
    gap: 14,
  },
  ssoSubtitle: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12.5,
    lineHeight: 18,
    marginBottom: 4,
  },
  ssoAccountCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 16,
    borderWidth: 1.2,
    gap: 12,
  },
  ssoAccountAvatar: {
    width: 42,
    height: 42,
    borderRadius: 21,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(158, 133, 255, 0.15)',
  },
  ssoAccountName: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '800',
  },
  ssoAccountEmail: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11.5,
    marginTop: 2,
  },
  ssoAccountChevron: {
    fontSize: 16,
    color: '#9E85FF',
    fontWeight: '700',
  },
  ssoCustomInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 48,
    borderRadius: 14,
    borderWidth: 1.2,
    paddingHorizontal: 12,
  },
  ssoInputPrefix: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    fontWeight: '600',
    marginRight: 4,
  },
  ssoCustomInput: {
    flex: 1,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13.5,
    height: '100%',
  },
  ssoChipsRow: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  ssoChip: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    borderWidth: 1,
  },
  ssoChipText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11.5,
    color: '#9E85FF',
    fontWeight: '700',
  },
  githubProfilePreviewCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 16,
    borderWidth: 1.2,
    gap: 12,
  },
  githubAvatarImage: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1.5,
    borderColor: '#9E85FF',
  },
  githubAvatarFallback: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#24292E',
    alignItems: 'center',
    justifyContent: 'center',
  },
  githubPreviewName: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
    fontWeight: '800',
  },
  githubPreviewLogin: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11.5,
    color: '#9E85FF',
    fontWeight: '600',
  },
  githubPreviewBio: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11,
    marginTop: 2,
  },
  githubRepoBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.10)',
  },
  githubRepoBadgeText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 11,
    color: '#FBBF24',
    fontWeight: '700',
  },
  ssoPrimaryBtn: {
    height: 50,
    borderRadius: 25,
    backgroundColor: '#9E85FF',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 4,
    shadowColor: '#9E85FF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.40,
    shadowRadius: 10,
    elevation: 6,
  },
  ssoPrimaryBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 15,
    fontWeight: '900',
    color: '#0B0F19',
    letterSpacing: 0.3,
  },
  ssoSecondaryBtn: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
  },
  ssoSecondaryBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12.5,
    fontWeight: '600',
  },
  socialLabelText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 20,
  },
  switchAuthModeBtn: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  switchAuthModeText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13.5,
    color: '#94A3B8',
  },

  // Screen C: OTP Verification
  emailPillBadge: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(158, 133, 255, 0.16)',
    borderColor: 'rgba(158, 133, 255, 0.35)',
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 5,
    marginBottom: 18,
  },
  emailPillText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    color: '#9E85FF',
    fontWeight: '800',
  },
  otpInputWrapper: {
    height: 60,
    borderRadius: 16,
    borderWidth: 1.8,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  otpTextInput: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 28,
    fontWeight: '900',
    letterSpacing: 12,
    textAlign: 'center',
  },
  resendBtn: {
    marginTop: 16,
    alignItems: 'center',
    paddingVertical: 8,
  },
  resendBtnText: {
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    color: '#9E85FF',
    textDecorationLine: 'underline',
  },
});
