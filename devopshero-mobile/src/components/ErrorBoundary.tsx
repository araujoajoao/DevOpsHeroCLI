import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[DevOpsHero ErrorBoundary Caught]', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleRestart = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <SafeAreaView style={styles.container}>
          <ScrollView contentContainerStyle={styles.content}>
            <Text style={styles.badge}>⚠️ DEVOPSHERO RECOVERY</Text>
            <Text style={styles.title}>Falha na Execução</Text>
            <Text style={styles.subtitle}>
              Um erro inesperado ocorreu durante a renderização do aplicativo:
            </Text>

            <View style={styles.errorBox}>
              <Text style={styles.errorText}>
                {this.state.error?.toString() || 'Erro desconhecido'}
              </Text>
              {this.state.errorInfo?.componentStack && (
                <Text style={styles.stackText}>
                  {this.state.errorInfo.componentStack.slice(0, 400)}
                </Text>
              )}
            </View>

            <TouchableOpacity style={styles.retryButton} onPress={this.handleRestart}>
              <Text style={styles.retryButtonText}>↺ TENTAR NOVAMENTE</Text>
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#131627',
  },
  content: {
    padding: 24,
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100%',
  },
  badge: {
    color: '#FBBF24',
    fontFamily: 'Menlo',
    fontSize: 12,
    fontWeight: 'bold',
    letterSpacing: 1,
    marginBottom: 8,
  },
  title: {
    color: '#FFFFFF',
    fontFamily: 'Menlo',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    color: '#9E85FF',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 20,
  },
  errorBox: {
    backgroundColor: '#1E243E',
    borderColor: '#FB7185',
    borderWidth: 1,
    borderRadius: 14,
    padding: 16,
    width: '100%',
    marginBottom: 24,
  },
  errorText: {
    color: '#FB7185',
    fontFamily: 'Menlo',
    fontSize: 13,
    marginBottom: 8,
  },
  stackText: {
    color: '#8A99AD',
    fontFamily: 'Menlo',
    fontSize: 11,
    lineHeight: 16,
  },
  retryButton: {
    backgroundColor: '#9E85FF',
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 16,
    width: '100%',
    alignItems: 'center',
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontFamily: 'Menlo',
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
});

