import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Platform,
} from 'react-native';
import * as Haptics from 'expo-haptics';

interface AppUpdateModalProps {
  visible: boolean;
  onDismiss: () => void;
  currentVersion?: string;
  targetVersion?: string;
}

export const AppUpdateModal: React.FC<AppUpdateModalProps> = ({
  visible,
  onDismiss,
  currentVersion = 'v1.0.0',
  targetVersion = '0.21.0',
}) => {
  const [progress, setProgress] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [showWhatsNew, setShowWhatsNew] = useState(false);

  useEffect(() => {
    if (!visible) {
      setProgress(0);
      setIsCompleted(false);
      setShowWhatsNew(false);
      return;
    }

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsCompleted(true);
          try {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          } catch (_) {}
          return 100;
        }
        return prev + 6;
      });
    }, 120);

    return () => clearInterval(interval);
  }, [visible]);

  const handleDismiss = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
    onDismiss();
  };

  const handleToggleWhatsNew = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (_) {}
    setShowWhatsNew(prev => !prev);
  };

  return (
    <Modal
      transparent
      visible={visible}
      animationType="fade"
      onRequestClose={handleDismiss}
    >
      <View style={styles.backdrop}>
        <View style={styles.card}>
          {/* Top Row: App Icon + Titles + Apple Standard 44pt Close Button */}
          <View style={styles.topRow}>
            <View style={styles.iconContainer}>
              <Text style={styles.iconText}>⚡</Text>
            </View>

            <View style={styles.titleColumn}>
              <View style={styles.titleInlineRow}>
                <Text style={styles.appName}>DevOpsHero</Text>
                <Text style={styles.byAuthor}>by @araujoajoao</Text>
                <View style={styles.updateBadge}>
                  <Text style={styles.updateBadgeText}>UPDATE</Text>
                </View>
              </View>

              <Text style={styles.versionText}>
                {currentVersion} to {targetVersion}
              </Text>
            </View>

            <TouchableOpacity
              onPress={handleDismiss}
              style={styles.closeButton}
              hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
              accessibilityLabel="Fechar janela de atualização"
              accessibilityRole="button"
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          {/* Middle Row: Spinner + Status Text + Apple Continuous Progress Bar */}
          <View style={styles.progressSection}>
            <View style={styles.statusRow}>
              {isCompleted ? (
                <Text style={styles.completedCheck}>✓</Text>
              ) : (
                <ActivityIndicator size="small" color="#64748B" style={styles.spinner} />
              )}
              <Text style={styles.statusText}>
                {isCompleted
                  ? 'DevOpsHero atualizado com sucesso!'
                  : 'Downloading and installing update...'}
              </Text>
            </View>

            <View style={styles.progressBarTrack}>
              <View
                style={[
                  styles.progressBarFill,
                  { width: `${progress}%`, backgroundColor: isCompleted ? '#16A34A' : '#E05236' },
                ]}
              />
            </View>
          </View>

          {/* Expandable What's New Box (Apple Inset Grouped style) */}
          {showWhatsNew && (
            <ScrollView style={styles.whatsNewBox} contentContainerStyle={styles.whatsNewContent}>
              <Text style={styles.whatsNewHeading}>O que há de novo na versão {targetVersion}:</Text>
              <Text style={styles.whatsNewBullet}>• 8 Trilhas alinhadas às documentações oficiais (Linux, Docker, K8s, AWS, Terraform, Datadog)</Text>
              <Text style={styles.whatsNewBullet}>• Bloqueio estrito de trilhas por Senioridade e XP</Text>
              <Text style={styles.whatsNewBullet}>• Modo aleatório de tarefas (Shuffled tasks) a cada sessão</Text>
              <Text style={styles.whatsNewBullet}>• Novo comando nativo 'dh update' no terminal</Text>
            </ScrollView>
          )}

          {/* Apple Hairline Divider */}
          <View style={styles.divider} />

          {/* Footer: "What's new" on left, "DISMISS" on right with Apple 44pt Touch Target */}
          <View style={styles.footerRow}>
            <TouchableOpacity
              onPress={handleToggleWhatsNew}
              activeOpacity={0.7}
              style={styles.whatsNewBtn}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Text style={styles.whatsNewText}>What's new</Text>
              <View style={styles.whatsNewUnderline} />
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleDismiss}
              activeOpacity={0.8}
              style={styles.dismissButton}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Text style={styles.dismissButtonText}>
                {isCompleted ? 'CONCLUIR' : 'DISMISS'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.48)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  card: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingTop: 20,
    paddingHorizontal: 20,
    paddingBottom: 18,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.22,
    shadowRadius: 22,
    elevation: 12,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  iconContainer: {
    width: 44,
    height: 44,
    borderRadius: 10,
    backgroundColor: '#E05236',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  iconText: {
    fontSize: 22,
    color: '#FFFFFF',
    fontWeight: '700',
  },
  titleColumn: {
    flex: 1,
    justifyContent: 'center',
  },
  titleInlineRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  appName: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
    marginRight: 6,
  },
  byAuthor: {
    fontSize: 12,
    color: '#6B7280',
    marginRight: 8,
  },
  updateBadge: {
    backgroundColor: '#E05236',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  updateBadgeText: {
    fontSize: 9,
    fontWeight: '800',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  versionText: {
    fontSize: 12,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    color: '#6B7280',
    marginTop: 3,
  },
  closeButton: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'flex-end',
  },
  closeButtonText: {
    fontSize: 15,
    color: '#9CA3AF',
    fontWeight: '600',
  },
  progressSection: {
    marginTop: 16,
    marginBottom: 6,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  spinner: {
    marginRight: 8,
  },
  completedCheck: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#16A34A',
    marginRight: 8,
  },
  statusText: {
    fontSize: 13,
    color: '#1F2937',
    fontWeight: '600',
  },
  progressBarTrack: {
    height: 3.5,
    backgroundColor: '#E5E7EB',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 2,
  },
  whatsNewBox: {
    maxHeight: 125,
    backgroundColor: '#F9FAFB',
    borderColor: '#E5E7EB',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginTop: 10,
    marginBottom: 6,
  },
  whatsNewContent: {
    paddingBottom: 4,
  },
  whatsNewHeading: {
    fontSize: 12,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 6,
  },
  whatsNewBullet: {
    fontSize: 11,
    color: '#4B5563',
    lineHeight: 16,
    marginBottom: 3,
  },
  divider: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: '#E5E7EB',
    marginTop: 14,
    marginBottom: 14,
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  whatsNewBtn: {
    minHeight: 44,
    justifyContent: 'center',
  },
  whatsNewText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#111827',
  },
  whatsNewUnderline: {
    height: 1.5,
    backgroundColor: '#E05236',
    marginTop: 2,
  },
  dismissButton: {
    minHeight: 36,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 6,
    paddingVertical: 8,
    paddingHorizontal: 22,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  dismissButtonText: {
    fontSize: 11,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontWeight: '700',
    color: '#4B5563',
    letterSpacing: 0.8,
  },
});
