import { DEFAULT_EMAILJS_CONFIG, EmailJSConfig } from './emailjsConfig';
import { detectDevice } from '../utils/deviceInfo';

export interface SendEmailParams {
  toEmail: string;
  toName: string;
  code: string;
}

export interface SendEmailResult {
  success: boolean;
  message: string;
  simulated?: boolean;
}

/**
 * Generates a secure 6-digit numeric OTP verification code
 */
export function generateVerificationCode(): string {
  return String(Math.floor(100000 + Math.random() * 900000));
}

/**
 * Sends a verification email using EmailJS REST API
 * (Compatible with Expo, React Native and Web without native dependencies)
 */
export async function sendVerificationEmail(
  params: SendEmailParams,
  customConfig?: Partial<EmailJSConfig>
): Promise<SendEmailResult> {
  const config: EmailJSConfig = {
    ...DEFAULT_EMAILJS_CONFIG,
    ...(customConfig || {}),
  };

  const isRealConfig =
    config.isConfigured &&
    config.serviceId &&
    !config.serviceId.includes('devopshero') &&
    config.publicKey &&
    !config.publicKey.includes('devopshero');

  // If using placeholder credentials, operate in safe Development Simulation Mode
  if (!isRealConfig) {
    console.log(
      `[EmailJS Simulation] Código para ${params.toEmail} (@${params.toName}): ${params.code}`
    );
    return {
      success: true,
      simulated: true,
      message: `Código gerado em modo de teste: ${params.code} (Insira suas chaves do EmailJS para envio real).`,
    };
  }

  try {
    const device = detectDevice();

    const payload: Record<string, any> = {
      service_id: config.serviceId,
      template_id: config.templateId,
      user_id: config.publicKey,
      template_params: {
        to_email: params.toEmail,
        to_name: params.toName,
        verification_code: params.code,
        app_name: 'DevOpsHero CLI',
        expires_in: '15 minutos',
        time_sent: new Date().toLocaleString('pt-BR'),
        admin_email: config.adminEmail || 'araujoaojoao@gmail.com',
        from_name: 'DevOpsHero Admin',
        reply_to: config.adminEmail || 'araujoaojoao@gmail.com',
        // Auto-detected Device Info
        device_type: device.deviceType.toUpperCase(),
        device_badge: device.badgeLabel,
        device_model: device.modelName,
        client_platform: `${device.osName} (${device.isDesktop ? 'Desktop Workstation' : device.isTablet ? 'Tablet' : 'Mobile Smartphone'})`,
        client_resolution: `${Math.round(device.screenWidth)}x${Math.round(device.screenHeight)} pt`,
        input_type: device.isTouchDevice ? 'Touchscreen' : 'Teclado & Mouse',
      },
    };

    // If Private Key is provided (for accounts with Strict Mode enabled), attach as accessToken
    if (config.privateKey && config.privateKey.trim().length > 0) {
      payload.accessToken = config.privateKey.trim();
    }

    const response = await fetch('https://api.emailjs.com/api/v1.0/email/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      return {
        success: true,
        simulated: false,
        message: `E-mail de verificação enviado com sucesso para ${params.toEmail}!`,
      };
    } else {
      const errorText = await response.text();
      console.warn('[EmailJS Error]', errorText);

      let userFriendlyMsg = `Falha no EmailJS (${response.status}): ${errorText || 'Verifique Service ID e Template ID'}.`;
      if (errorText.includes('strict mode') || errorText.includes('Private Key')) {
        userFriendlyMsg = 'Acesso em Strict Mode no EmailJS: Desative a opção "API access in strict mode" em Account > Security, ou informe a Private Key.';
      }

      return {
        success: false,
        simulated: false,
        message: userFriendlyMsg,
      };
    }
  } catch (error: any) {
    console.warn('[EmailJS Network Error]', error);
    return {
      success: false,
      simulated: false,
      message: `Erro de conexão ao enviar e-mail: ${error?.message || 'Verifique sua conexão'}.`,
    };
  }
}

