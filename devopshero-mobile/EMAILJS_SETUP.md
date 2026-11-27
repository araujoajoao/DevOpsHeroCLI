# 📧 Guia de Configuração do EmailJS no DevOpsHero

Este guia orienta como configurar o serviço **EmailJS** para validar e-mails de novos operadores cadastrados no aplicativo.

---

## 1. Variáveis do Template no EmailJS

Ao criar ou editar o seu template no [Dashboard do EmailJS](https://dashboard.emailjs.com/admin/templates), utilize os seguintes parâmetros:

| Variável | Descrição | Exemplo de Valor |
| :--- | :--- | :--- |
| `{{to_email}}` | E-mail do usuário destinatário | `operador@empresa.com` |
| `{{to_name}}` | Nome de usuário CLI | `joao_araujo` |
| `{{verification_code}}` | Código OTP de 6 dígitos | `849201` |
| `{{app_name}}` | Nome do sistema | `DevOpsHero CLI` |
| `{{expires_in}}` | Tempo de validade | `15 minutos` |
| `{{time_sent}}` | Data e hora do envio | `02/11/2026, 21:30:00` |

---

## 2. Conteúdo do Template

1. Abra o painel do EmailJS em **Email Templates** ➔ **Create New Template**.
2. No campo **Subject (Assunto)**, defina:
   ```text
   🔐 [DevOpsHero] Código de Verificação: {{verification_code}}
   ```
3. No campo **To Email (Destinatário)**, preencha:
   ```text
   {{to_email}}
   ```
4. No editor de conteúdo (aba **Content**), alterne para modo **HTML** e cole o código disponível no arquivo:
   📂 `src/services/emailjsTemplate.html`

---

## 3. Configurar as Chaves no Aplicativo

Abra o arquivo [`src/services/emailjsConfig.ts`](./src/services/emailjsConfig.ts) e informe seus identificadores:

```typescript
export const DEFAULT_EMAILJS_CONFIG: EmailJSConfig = {
  serviceId: 'service_SEU_ID',    // Ex: "service_gmail" ou "service_resend"
  templateId: 'template_SEU_ID',  // Ex: "template_devopshero"
  publicKey: 'pub_SUA_CHAVE',     // Sua Public Key do EmailJS (Account ➔ API Keys)
  isConfigured: true,
};
```

---

## 4. Modo de Simulação (Fallback)
Se as chaves ainda não estiverem cadastradas ou se a chamada à API falhar durante testes locais/offline, o aplicativo opera em **Modo de Desenvolvimento Seguro**:
- Um alerta exibe o código de 6 dígitos diretamente na tela do dispositivo para permitir que os testes continuem sem bloqueio.
- Assim que você inserir suas chaves reais, o disparo de e-mails reais entra em operação imediatamente através da API do EmailJS!

