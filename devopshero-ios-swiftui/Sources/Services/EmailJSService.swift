import Foundation

public struct EmailJSConfig {
    public var serviceId: String = "service_gxm4z5e"
    public var templateId: String = "template_1hondid"
    public var publicKey: String = "ZUXg-zLHTMAg-LqnX"
    public var privateKey: String = ""
    public var adminEmail: String = "araujoaojoao@gmail.com"

    public static let `default` = EmailJSConfig()
}

public class EmailJSService {
    public static let shared = EmailJSService()

    public init() {}

    public func generateVerificationCode() -> String {
        let code = Int.random(in: 100000...999999)
        return String(code)
    }

    public func sendVerificationEmail(
        toEmail: String,
        toName: String,
        code: String,
        config: EmailJSConfig = .default
    ) async -> (success: Bool, message: String, simulated: Bool) {
        let isRealConfig = !config.serviceId.isEmpty &&
            !config.serviceId.contains("devopshero") &&
            !config.publicKey.isEmpty &&
            !config.publicKey.contains("devopshero")

        if !isRealConfig {
            print("[EmailJS Simulation] Código para \(toEmail) (@\(toName)): \(code)")
            return (true, "Código gerado em modo de teste: \(code)", true)
        }

        guard let url = URL(string: "https://api.emailjs.com/api/v1.0/email/send") else {
            return (false, "URL da API EmailJS inválida.", false)
        }

        let templateParams: [String: Any] = [
            "to_email": toEmail,
            "to_name": toName,
            "verification_code": code,
            "app_name": "DevOpsHero iOS",
            "expires_in": "15 minutos",
            "time_sent": DateFormatter.localizedString(from: Date(), dateStyle: .short, timeStyle: .short),
            "admin_email": config.adminEmail,
            "from_name": "DevOpsHero Admin",
            "reply_to": config.adminEmail,
            "client_platform": "Apple iOS (SwiftUI Native)",
            "device_type": "APPLE_IOS"
        ]

        var payload: [String: Any] = [
            "service_id": config.serviceId,
            "template_id": config.templateId,
            "user_id": config.publicKey,
            "template_params": templateParams
        ]

        if !config.privateKey.trimmingCharacters(in: .whitespaces).isEmpty {
            payload["accessToken"] = config.privateKey.trimmingCharacters(in: .whitespaces)
        }

        do {
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: payload, options: [])

            let (data, response) = try await URLSession.shared.data(for: request)

            if let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) {
                return (true, "E-mail de verificação enviado com sucesso para \(toEmail)!", false)
            } else {
                let errorText = String(data: data, encoding: .utf8) ?? "Erro desconhecido"
                let userFriendly = "Falha no envio via EmailJS: \(errorText)"
                return (false, userFriendly, false)
            }
        } catch {
            return (false, "Erro de conexão ao enviar e-mail: \(error.localizedDescription)", false)
        }
    }
}
