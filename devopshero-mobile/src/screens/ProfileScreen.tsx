import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { LiquidGlassView } from '../components/LiquidGlassView';
import { LinearGradient } from 'expo-linear-gradient';

interface ProfileScreenProps {
  theme: 'light' | 'dark';
  onSetTheme: (theme: 'light' | 'dark') => void;
  xp: number;
  streak: number;
  userName: string;
  userEmail?: string;
  userRole: string;
  isLoggedIn: boolean;
  onLogin: (username: string) => void;
  onRegister: (username: string, role?: string) => void;
  onLogout: () => void;
  onBackToHome?: () => void;
}

export const ProfileScreen: React.FC<ProfileScreenProps> = ({
  theme,
  onSetTheme,
  xp,
  streak,
  userName,
  userEmail,
  userRole,
  isLoggedIn,
  onLogin,
  onRegister,
  onLogout,
  onBackToHome,
}) => {
  const isDark = theme === 'dark';

  const [authMode, setAuthMode] = useState<'session' | 'login' | 'register'>('session');
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [roleInput, setRoleInput] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);

  const triggerHaptic = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
  };

  const handleDoLogin = () => {
    triggerHaptic();
    const targetUser = usernameInput.trim() || 'novo_operador';
    onLogin(targetUser);
    setFeedback(`● Autenticado com sucesso como @${targetUser}`);
    setAuthMode('session');
    setUsernameInput('');
    setPasswordInput('');
  };

  const handleDoRegister = () => {
    triggerHaptic();
    const targetUser = usernameInput.trim() || 'novo_devops';
    const targetRole = roleInput.trim() || 'DevOps Engineer · Nível 1';
    onRegister(targetUser, targetRole);
    setFeedback(`● Usuário @${targetUser} cadastrado e ativo!`);
    setAuthMode('session');
    setUsernameInput('');
    setPasswordInput('');
    setRoleInput('');
  };

  const progressRatio = Math.min(xp / 500, 1.0);
  const progressPercent = Math.min(Math.max(progressRatio * 100, 8), 100);

  const cardBg = isDark ? '#272E4F' : '#EDF0F7';
  const borderCol = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.07)';
  const textColor = isDark ? '#FFFFFF' : '#0F172A';
  const textMutedColor = isDark ? '#A5B4FC' : '#475569';

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={{ flex: 1 }}
    >
      <View
        style={[
          styles.root,
          {
            backgroundColor: 'transparent',
          },
        ]}
      >
        {/* 1. Header Row ('✕' Dismiss, 'DevOps Profile' Centered, Theme Toggle) */}
        <View style={styles.topBar}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => {
              triggerHaptic();
              if (onBackToHome) {
                onBackToHome();
              }
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
            DevOps Profile
          </Text>

          <TouchableOpacity
            style={styles.themeToggleBtn}
            onPress={() => {
              triggerHaptic();
              onSetTheme(isDark ? 'light' : 'dark');
            }}
            activeOpacity={0.7}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            accessibilityLabel="Alternar tema"
          >
            <Text style={styles.themeToggleIcon}>
              {isDark ? '☀️' : '🌙'}
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* 2. Section Title */}
          <Text style={[styles.sectionHeading, { color: textColor }]}>
            DevOps Operator
          </Text>

          {/* 3. Seniority Level & Lilac Progress Bar (Parity with Home & Tracks) */}
          <View style={styles.seniorityProgressContainer}>
            <View style={styles.seniorityLabelsRow}>
              <Text style={[styles.seniorityTitleLabel, { color: isDark ? '#A5B4FC' : '#6366F1' }]}>
                SENIORITY LEVEL
              </Text>
              <Text style={[styles.seniorityValueLabel, { color: isDark ? '#A5B4FC' : '#475569' }]}>
                PLENO · {xp}/500 XP
              </Text>
            </View>

            <View style={[styles.progressBarTrack, { backgroundColor: isDark ? '#181C33' : '#CBD5E1' }]}>
              <View
                style={[
                  styles.progressBarFill,
                  { width: `${progressPercent}%`, backgroundColor: '#9E85FF' },
                ]}
              />
            </View>
          </View>

          {/* Feedback Alert Box */}
          {feedback && (
            <View
              style={[
                styles.feedbackBox,
                {
                  backgroundColor: isDark ? 'rgba(0, 223, 137, 0.12)' : 'rgba(22, 163, 74, 0.10)',
                  borderColor: isDark ? '#00DF89' : '#16a34a',
                },
              ]}
            >
              <Text
                style={[
                  styles.feedbackText,
                  { color: isDark ? '#00DF89' : '#16a34a' },
                ]}
              >
                {feedback}
              </Text>
            </View>
          )}

          {/* 4. Operator Identity Card with Apple Liquid Glass */}
          <LiquidGlassView
            borderRadius={22}
            borderWidth={1.2}
            borderColor={isDark ? 'rgba(255, 255, 255, 0.22)' : 'rgba(0, 0, 0, 0.08)'}
            theme={theme}
            showSheen={true}
            intensity={40}
            style={styles.cardWrapper}
            contentStyle={styles.cardInterior}
          >
            {authMode === 'session' ? (
              <View>
                {/* Header Row: Badge Avatar + Names + Status Pill */}
                <View style={styles.operatorHeaderRow}>
                  {/* Official Single Badge Container (34x34pt squircle) */}
                  <View
                    style={[
                      styles.avatarBadge,
                      {
                        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.35)' : '#FFFFFF',
                      },
                    ]}
                  >
                    <Text style={styles.avatarEmoji}>👨‍💻</Text>
                  </View>

                  <View style={styles.operatorTitleCol}>
                    <Text
                      style={[
                        styles.operatorHandle,
                        { color: isDark ? '#00DF89' : '#16a34a' },
                      ]}
                      numberOfLines={1}
                    >
                      @{userName}
                    </Text>
                    <Text
                      style={[
                        styles.operatorRole,
                        { color: isDark ? '#D8E2FD' : '#334155' },
                      ]}
                      numberOfLines={1}
                    >
                      {userRole}
                    </Text>
                  </View>

                  {/* Status Pill Badge */}
                  <View
                    style={[
                      styles.statusPill,
                      {
                        backgroundColor: isDark ? 'rgba(0, 223, 137, 0.14)' : 'rgba(22, 163, 74, 0.12)',
                        borderColor: isDark ? 'rgba(0, 223, 137, 0.40)' : 'rgba(22, 163, 74, 0.30)',
                      },
                    ]}
                  >
                    <View
                      style={[
                        styles.statusDot,
                        { backgroundColor: isDark ? '#00DF89' : '#16a34a' },
                      ]}
                    />
                    <Text
                      style={[
                        styles.statusText,
                        { color: isDark ? '#00DF89' : '#16a34a' },
                      ]}
                    >
                      ONLINE
                    </Text>
                  </View>
                </View>

                <View style={[styles.cardDivider, { backgroundColor: borderCol }]} />

                {/* Session Metadata Rows */}
                <View style={styles.metaRowsContainer}>
                  <View style={styles.metaRow}>
                    <Text style={[styles.metaKey, { color: textMutedColor }]}>
                      Sessão CLI:
                    </Text>
                    <Text style={[styles.metaVal, { color: isDark ? '#00DF89' : '#16a34a' }]}>
                      devops@ops-lab (● ATIVO)
                    </Text>
                  </View>

                  <View style={styles.metaRow}>
                    <Text style={[styles.metaKey, { color: textMutedColor }]}>
                      Ambiente SRE:
                    </Text>
                    <Text style={[styles.metaVal, { color: isDark ? '#38BDF8' : '#0284c7' }]}>
                      Local Core Engine v1.1.0
                    </Text>
                  </View>

                  <View style={styles.metaRow}>
                    <Text style={[styles.metaKey, { color: textMutedColor }]}>
                      Chave SSH:
                    </Text>
                    <Text style={[styles.metaVal, { color: textColor }]}>
                      ed25519 · [rw-r--r--]
                    </Text>
                  </View>
                </View>

                {/* Action Buttons: Trocar Usuário & Encerrar Sessão */}
                <View style={styles.actionButtonsRow}>
                  <TouchableOpacity
                    style={[
                      styles.actionButton,
                      {
                        backgroundColor: isDark ? 'rgba(56, 189, 248, 0.12)' : 'rgba(2, 132, 199, 0.10)',
                        borderColor: isDark ? 'rgba(56, 189, 248, 0.50)' : 'rgba(2, 132, 199, 0.40)',
                      },
                    ]}
                    onPress={() => {
                      triggerHaptic();
                      setFeedback(null);
                      setAuthMode('login');
                    }}
                    activeOpacity={0.75}
                  >
                    <Text
                      style={[
                        styles.actionButtonText,
                        { color: isDark ? '#38BDF8' : '#0369A1' },
                      ]}
                    >
                      Trocar Usuário
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[
                      styles.actionButton,
                      {
                        backgroundColor: isDark ? 'rgba(251, 113, 133, 0.12)' : 'rgba(225, 29, 72, 0.10)',
                        borderColor: isDark ? 'rgba(251, 113, 133, 0.50)' : 'rgba(225, 29, 72, 0.40)',
                      },
                    ]}
                    onPress={() => {
                      triggerHaptic();
                      onLogout();
                    }}
                    activeOpacity={0.75}
                  >
                    <Text
                      style={[
                        styles.actionButtonText,
                        { color: isDark ? '#FB7185' : '#BE123C' },
                      ]}
                    >
                      Encerrar Sessão
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              <View>
                {/* Segmented Mode Switch */}
                <View style={styles.authSegmentRow}>
                  <TouchableOpacity
                    style={[
                      styles.authSegmentBtn,
                      authMode === 'login' && [
                        styles.authSegmentBtnActive,
                        {
                          borderColor: isDark ? '#38BDF8' : '#0369A1',
                          backgroundColor: isDark ? 'rgba(56, 189, 248, 0.16)' : 'rgba(3, 105, 161, 0.12)',
                        },
                      ],
                    ]}
                    onPress={() => {
                      triggerHaptic();
                      setAuthMode('login');
                    }}
                  >
                    <Text
                      style={[
                        styles.authSegmentText,
                        { color: authMode === 'login' ? (isDark ? '#38BDF8' : '#0369A1') : (isDark ? '#94A3B8' : '#475569') },
                      ]}
                    >
                      Fazer Login
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[
                      styles.authSegmentBtn,
                      authMode === 'register' && [
                        styles.authSegmentBtnActive,
                        {
                          borderColor: isDark ? '#00DF89' : '#15803D',
                          backgroundColor: isDark ? 'rgba(0, 223, 137, 0.16)' : 'rgba(21, 128, 61, 0.12)',
                        },
                      ],
                    ]}
                    onPress={() => {
                      triggerHaptic();
                      setAuthMode('register');
                    }}
                  >
                    <Text
                      style={[
                        styles.authSegmentText,
                        { color: authMode === 'register' ? (isDark ? '#00DF89' : '#15803D') : (isDark ? '#94A3B8' : '#475569') },
                      ]}
                    >
                      Cadastrar Novo
                    </Text>
                  </TouchableOpacity>
                </View>

                {/* Username Input */}
                <View style={styles.inputGroup}>
                  <Text style={[styles.inputLabel, { color: textColor }]}>
                    Nome de usuário:
                  </Text>
                  <TextInput
                    style={[
                      styles.textInput,
                      {
                        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.25)' : '#FFFFFF',
                        borderColor: borderCol,
                        color: textColor,
                      },
                    ]}
                    value={usernameInput}
                    onChangeText={setUsernameInput}
                    placeholder="ex: joao_araujo"
                    placeholderTextColor={textMutedColor}
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                </View>

                {/* Password Input */}
                <View style={styles.inputGroup}>
                  <Text style={[styles.inputLabel, { color: textColor }]}>
                    Senha de acesso:
                  </Text>
                  <TextInput
                    style={[
                      styles.textInput,
                      {
                        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.25)' : '#FFFFFF',
                        borderColor: borderCol,
                        color: textColor,
                      },
                    ]}
                    value={passwordInput}
                    onChangeText={setPasswordInput}
                    placeholder="••••••••"
                    placeholderTextColor={textMutedColor}
                    secureTextEntry
                  />
                </View>

                {/* Role Input if register */}
                {authMode === 'register' && (
                  <View style={styles.inputGroup}>
                    <Text style={[styles.inputLabel, { color: textColor }]}>
                      Cargo / Nível:
                    </Text>
                    <TextInput
                      style={[
                        styles.textInput,
                        {
                          backgroundColor: isDark ? 'rgba(0, 0, 0, 0.25)' : '#FFFFFF',
                          borderColor: borderCol,
                          color: textColor,
                        },
                      ]}
                      value={roleInput}
                      onChangeText={setRoleInput}
                      placeholder="ex: SRE Pleno / Cloud Engineer"
                      placeholderTextColor={textMutedColor}
                    />
                  </View>
                )}

                {/* Primary Submit Button */}
                <TouchableOpacity
                  style={[
                    styles.submitBtn,
                    {
                      backgroundColor:
                        authMode === 'login'
                          ? (isDark ? '#38BDF8' : '#0284c7')
                          : (isDark ? '#00DF89' : '#16a34a'),
                    },
                  ]}
                  onPress={authMode === 'login' ? handleDoLogin : handleDoRegister}
                  activeOpacity={0.85}
                >
                  <Text style={[styles.submitBtnText, { color: isDark ? '#0B0F19' : '#FFFFFF' }]}>
                    {authMode === 'login'
                      ? 'Autenticar e Entrar ➔'
                      : 'Cadastrar e Iniciar ➔'}
                  </Text>
                </TouchableOpacity>

                {/* Cancel Button */}
                <TouchableOpacity
                  style={styles.cancelBtn}
                  onPress={() => {
                    triggerHaptic();
                    setAuthMode('session');
                  }}
                  activeOpacity={0.7}
                >
                  <Text style={[styles.cancelBtnText, { color: isDark ? '#94A3B8' : '#475569' }]}>
                    Cancelar e voltar à sessão
                  </Text>
                </TouchableOpacity>
              </View>
            )}
          </LiquidGlassView>

          {/* 5. Performance Metrics Section (2x2 Cards in #272E4F) */}
          <View style={styles.sectionHeaderRow}>
            <Text style={[styles.commandHeader, { color: isDark ? '#00DF89' : '#16a34a' }]}>
              $ cat /var/log/learning_metrics.tsv
            </Text>
          </View>

          <View style={styles.metricsGrid}>
            <LiquidGlassView
              borderRadius={18}
              borderWidth={1.2}
              borderColor={isDark ? 'rgba(56, 189, 248, 0.40)' : 'rgba(2, 132, 199, 0.25)'}
              theme={theme}
              showSheen={true}
              intensity={40}
              style={styles.metricCardTouchable}
              contentStyle={styles.metricCardInterior}
            >
              <Text style={[styles.metricCardKey, { color: isDark ? '#38BDF8' : '#0284c7' }]}>
                [TOTAL MISSIONS]
              </Text>
              <Text style={[styles.metricCardVal, { color: textColor }]}>
                80
              </Text>
              <Text style={[styles.metricCardDesc, { color: textMutedColor }]}>
                Missões Oficiais
              </Text>
            </LiquidGlassView>

            <LiquidGlassView
              borderRadius={18}
              borderWidth={1.2}
              borderColor={isDark ? 'rgba(251, 191, 36, 0.40)' : 'rgba(217, 119, 6, 0.25)'}
              theme={theme}
              showSheen={true}
              intensity={40}
              style={styles.metricCardTouchable}
              contentStyle={styles.metricCardInterior}
            >
              <Text style={[styles.metricCardKey, { color: isDark ? '#FBBF24' : '#D97706' }]}>
                [DAILY STREAK]
              </Text>
              <Text style={[styles.metricCardVal, { color: textColor }]}>
                {streak}d
              </Text>
              <Text style={[styles.metricCardDesc, { color: textMutedColor }]}>
                Dias Consecutivos
              </Text>
            </LiquidGlassView>

            <LiquidGlassView
              borderRadius={18}
              borderWidth={1.2}
              borderColor={isDark ? 'rgba(0, 223, 137, 0.40)' : 'rgba(22, 163, 74, 0.25)'}
              theme={theme}
              showSheen={true}
              intensity={40}
              style={styles.metricCardTouchable}
              contentStyle={styles.metricCardInterior}
            >
              <Text style={[styles.metricCardKey, { color: isDark ? '#00DF89' : '#16a34a' }]}>
                [TOTAL XP]
              </Text>
              <Text style={[styles.metricCardVal, { color: textColor }]}>
                {xp} XP
              </Text>
              <Text style={[styles.metricCardDesc, { color: textMutedColor }]}>
                Pontos Acumulados
              </Text>
            </LiquidGlassView>

            <LiquidGlassView
              borderRadius={18}
              borderWidth={1.2}
              borderColor={isDark ? 'rgba(158, 133, 255, 0.40)' : 'rgba(124, 92, 252, 0.25)'}
              theme={theme}
              showSheen={true}
              intensity={40}
              style={styles.metricCardTouchable}
              contentStyle={styles.metricCardInterior}
            >
              <Text style={[styles.metricCardKey, { color: '#9E85FF' }]}>
                [ACTIVE TRACKS]
              </Text>
              <Text style={[styles.metricCardVal, { color: textColor }]}>
                08
              </Text>
              <Text style={[styles.metricCardDesc, { color: textMutedColor }]}>
                Disciplinas CLI
              </Text>
            </LiquidGlassView>
          </View>

          {/* 6. System & Security Profile Card with Liquid Glass */}
          <LiquidGlassView
            borderRadius={22}
            borderWidth={1.2}
            borderColor={isDark ? 'rgba(255, 255, 255, 0.22)' : 'rgba(0, 0, 0, 0.08)'}
            theme={theme}
            showSheen={true}
            intensity={40}
            style={[styles.cardWrapper, styles.systemCardWrapper]}
            contentStyle={styles.cardInterior}
          >
            <Text style={[styles.commandHeader, { color: isDark ? '#00DF89' : '#16a34a', marginBottom: 10 }]}>
              2  ➜  ~ whoami --security
            </Text>

            <View style={styles.metaRowsContainer}>
              <View style={styles.metaRow}>
                <Text style={[styles.metaKey, { color: textMutedColor }]}>
                  Cluster Auth:
                </Text>
                <Text style={[styles.metaVal, { color: textColor }]}>
                  Bearer OTP (EmailJS Validated)
                </Text>
              </View>

              <View style={styles.metaRow}>
                <Text style={[styles.metaKey, { color: textMutedColor }]}>
                  SAIF Security:
                </Text>
                <Text style={[styles.metaVal, { color: isDark ? '#38BDF8' : '#0284c7' }]}>
                  Level-3 Compliant
                </Text>
              </View>

              <View style={styles.metaRow}>
                <Text style={[styles.metaKey, { color: textMutedColor }]}>
                  Storage Volume:
                </Text>
                <Text style={[styles.metaVal, { color: isDark ? '#FBBF24' : '#D97706' }]}>
                  Persistent Local SQLite
                </Text>
              </View>
            </View>
          </LiquidGlassView>
        </ScrollView>
      </View>
    </KeyboardAvoidingView>
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
    height: 48,
    marginTop: 8,
  },
  backButton: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backIcon: {
    fontSize: 20,
    fontWeight: '700',
  },
  topBarTitle: {
    fontSize: 17,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: -0.2,
  },
  themeToggleBtn: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  themeToggleIcon: {
    fontSize: 18,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 110,
  },
  sectionHeading: {
    fontSize: 20,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 14,
  },
  seniorityProgressContainer: {
    marginBottom: 20,
  },
  seniorityLabelsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  seniorityTitleLabel: {
    fontSize: 11,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 0.8,
  },
  seniorityValueLabel: {
    fontSize: 12,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  progressBarTrack: {
    height: 7,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  feedbackBox: {
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
  },
  feedbackText: {
    fontSize: 13,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  card: {
    borderRadius: 20,
    borderWidth: 1.2,
    padding: 18,
    marginBottom: 18,
  },
  operatorHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarBadge: {
    width: 34,
    height: 34,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarEmoji: {
    fontSize: 19,
  },
  operatorTitleCol: {
    flex: 1,
    marginLeft: 12,
  },
  operatorHandle: {
    fontSize: 19,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  operatorRole: {
    fontSize: 13,
    fontWeight: '600',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginTop: 2,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 9,
    paddingVertical: 4,
    borderRadius: 16,
    borderWidth: 1,
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 3.5,
    marginRight: 5,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 0.5,
  },
  cardDivider: {
    height: 1,
    marginVertical: 14,
  },
  metaRowsContainer: {
    gap: 8,
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  metaKey: {
    fontSize: 12,
    fontWeight: '500',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  metaVal: {
    fontSize: 12,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  actionButtonsRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  actionButton: {
    flex: 1,
    height: 44,
    borderRadius: 14,
    borderWidth: 1.2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  authSegmentRow: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0, 0, 0, 0.15)',
    borderRadius: 12,
    padding: 3,
    marginBottom: 14,
  },
  authSegmentBtn: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1.2,
    borderColor: 'transparent',
  },
  authSegmentBtnActive: {
    // defined dynamically
  },
  authSegmentText: {
    fontSize: 13,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  inputGroup: {
    marginBottom: 12,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 6,
  },
  textInput: {
    height: 46,
    borderRadius: 12,
    borderWidth: 1.2,
    paddingHorizontal: 14,
    fontSize: 14,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  submitBtn: {
    height: 48,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 6,
    marginBottom: 10,
  },
  submitBtnText: {
    color: '#0B0F19',
    fontSize: 14,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  cancelBtn: {
    height: 38,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelBtnText: {
    fontSize: 12,
    fontWeight: '600',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  sectionHeaderRow: {
    marginBottom: 10,
    marginTop: 4,
  },
  commandHeader: {
    fontSize: 12,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 18,
  },
  cardWrapper: {
    width: '100%',
    marginBottom: 18,
  },
  cardInterior: {
    padding: 18,
  },
  metricCardTouchable: {
    width: '48%',
    flexGrow: 1,
  },
  metricCardInterior: {
    padding: 16,
  },
  systemCardWrapper: {
    marginTop: 4,
  },
  metricCard: {
    width: '48%',
    flexGrow: 1,
    borderRadius: 18,
    borderWidth: 1.2,
    padding: 14,
  },
  metricCardKey: {
    fontSize: 11,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 6,
  },
  metricCardVal: {
    fontSize: 22,
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginBottom: 4,
  },
  metricCardDesc: {
    fontSize: 12,
    fontWeight: '500',
  },
  systemCard: {
    marginTop: 2,
  },
});
