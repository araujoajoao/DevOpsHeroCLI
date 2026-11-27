/**
 * EmailJS Configuration for DevOpsHero CLI
 * 
 * Painel: https://dashboard.emailjs.com/
 * - Email Admin Remetente: araujoaojoao@gmail.com
 * - Service ID (ex: "service_xxxxxxx")
 * - Template ID (ex: "template_xxxxxxx")
 * - Public Key (ex: "user_xxxxxxx" ou chave pública da conta)
 */

export interface EmailJSConfig {
  serviceId: string;
  templateId: string;
  publicKey: string;
  privateKey?: string;
  adminEmail: string;
  isConfigured: boolean;
}

export const DEFAULT_EMAILJS_CONFIG: EmailJSConfig = {
  // Configurações ativas do EmailJS:
  serviceId: 'service_gxm4z5e',
  templateId: 'template_1hondid',
  publicKey: 'ZUXg-zLHTMAg-LqnX',
  privateKey: '', // Opcional: preencha se mantiver o Strict Mode ativo no EmailJS
  adminEmail: 'araujoaojoao@gmail.com',
  isConfigured: true,
};

