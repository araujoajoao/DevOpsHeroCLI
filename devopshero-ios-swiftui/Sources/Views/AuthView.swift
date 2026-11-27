import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

public struct BrandEmblemView: View {
    public let size: CGFloat

    public init(size: CGFloat = 80) {
        self.size = size
    }

    private var scale: CGFloat { size / 80.0 }

    public var body: some View {
        ZStack {
            // Soft Radial Glow
            Circle()
                .fill(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.35))
                .frame(width: size * 0.9, height: size * 0.9)
                .scaleEffect(1.2)

            VStack(spacing: 7 * scale) {
                // Top Bar
                RoundedRectangle(cornerRadius: 7 * scale, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [Color.white, Color(red: 0.85, green: 0.88, blue: 0.98), Color(red: 0.65, green: 0.71, blue: 0.92)],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: 58 * scale, height: 14 * scale)
                    .shadow(color: Color.black.opacity(0.35), radius: 4, x: 0, y: 2)

                // Middle Bar with Luminous Glowing Node
                HStack(spacing: 4 * scale) {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.white, Color(red: 0.78, green: 0.82, blue: 0.98), Color(red: 0.62, green: 0.52, blue: 1.0)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .overlay(Circle().stroke(Color.white, lineWidth: 2 * scale))
                        .frame(width: 18 * scale, height: 18 * scale)
                        .shadow(color: Color(red: 0.62, green: 0.52, blue: 1.0), radius: 8, x: 0, y: 0)

                    RoundedRectangle(cornerRadius: 7 * scale, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [Color.white, Color(red: 0.85, green: 0.88, blue: 0.98), Color(red: 0.65, green: 0.71, blue: 0.92)],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: 40 * scale, height: 14 * scale)
                }
                .frame(width: 62 * scale, height: 16 * scale)

                // Bottom Bar
                RoundedRectangle(cornerRadius: 7 * scale, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [Color.white, Color(red: 0.85, green: 0.88, blue: 0.98), Color(red: 0.65, green: 0.71, blue: 0.92)],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: 58 * scale, height: 14 * scale)
                    .shadow(color: Color.black.opacity(0.35), radius: 4, x: 0, y: 2)
            }
        }
        .frame(width: size, height: size)
    }
}

public struct AuthView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel

    public enum ScreenMode {
        case welcome
        case form
        case verifyOtp
    }

    public enum AuthMode {
        case register
        case login
    }

    @State private var screenMode: ScreenMode = .welcome
    @State private var authMode: AuthMode = .login

    // Form inputs
    @State private var username: String = ""
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var showPassword: Bool = false
    @State private var agreeTerms: Bool = true

    // EmailJS OTP State
    @State private var generatedOtp: String = ""
    @State private var inputOtp: String = ""
    @State private var isLoading: Bool = false
    @State private var feedbackText: String? = nil
    @State private var feedbackIsError: Bool = false

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    private func triggerHaptic() {
        #if canImport(UIKit)
        let impact = UIImpactFeedbackGenerator(style: .light)
        impact.impactOccurred()
        #endif
    }

    public var body: some View {
        ZStack {
            // Background Decor: Apple Liquid Glass Atmospheric Backing
            AmbientGlassBackgroundView(themeMode: viewModel.themeMode)

            switch screenMode {
            case .welcome:
                welcomeScreenView
            case .form:
                formScreenView
            case .verifyOtp:
                verifyOtpScreenView
            }
        }
    }

    // MARK: - Screen A: Loading / Splash Mode
    private var welcomeScreenView: some View {
        Button(action: {
            triggerHaptic()
            authMode = .login
            screenMode = .form
        }) {
            VStack(spacing: 28) {
                Spacer()

                BrandEmblemView(size: 136)

                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: Color(red: 0.62, green: 0.52, blue: 1.0)))
                    .scaleEffect(1.2)

                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .buttonStyle(.plain)
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                withAnimation(.easeInOut(duration: 0.4)) {
                    authMode = .login
                    screenMode = .form
                }
            }
        }
    }

    // MARK: - Screen B: Form Mode
    private var formScreenView: some View {
        let isDark = viewModel.themeMode == .dark

        return ScrollView(showsIndicators: false) {
            VStack(spacing: 0) {
                // Curved Sheet Card
                VStack(alignment: .leading, spacing: 16) {
                    Text("hello!")
                        .font(.system(size: 28, weight: .black, design: .monospaced))
                        .foregroundColor(isDark ? .white : Color(red: 0.06, green: 0.09, blue: 0.16))

                    Text(authMode == .register ? "Create an account to start practicing" : "Sign in to access your CLI terminal")
                        .font(.system(size: 13, weight: .medium, design: .monospaced))
                        .foregroundColor(Color(red: 0.58, green: 0.64, blue: 0.72))
                        .padding(.bottom, 4)

                    // Feedback Alert Banner
                    if let feedback = feedbackText {
                        HStack {
                            Text(feedback)
                                .font(.system(size: 12.5, weight: .bold, design: .monospaced))
                                .foregroundColor(feedbackIsError ? ThemeColors.rose : ThemeColors.mintGreen)
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(feedbackIsError ? ThemeColors.rose.opacity(0.12) : ThemeColors.mintGreen.opacity(0.12))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .stroke(feedbackIsError ? ThemeColors.rose : ThemeColors.mintGreen, lineWidth: 1)
                        )
                    }

                    // Field 1: Username
                    HStack(spacing: 12) {
                        Text("👤")
                            .font(.system(size: 16))
                        TextField("Username", text: $username)
                            .font(.system(size: 14.5, design: .monospaced))
                            .foregroundColor(isDark ? .white : .black)
                            .plainTextFieldStyle()
                    }
                    .padding(.horizontal, 14)
                    .frame(height: 52)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(isDark ? Color.black.opacity(0.35) : Color.black.opacity(0.04))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08), lineWidth: 1.2)
                    )

                    // Field 2: Email (Registration mode)
                    if authMode == .register {
                        HStack(spacing: 12) {
                            Text("✉️")
                                .font(.system(size: 16))
                            TextField("Email", text: $email)
                                .font(.system(size: 14.5, design: .monospaced))
                                .foregroundColor(isDark ? .white : .black)
                                .emailFieldStyle()
                        }
                        .padding(.horizontal, 14)
                        .frame(height: 52)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .fill(isDark ? Color.black.opacity(0.35) : Color.black.opacity(0.04))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08), lineWidth: 1.2)
                        )
                    }

                    // Field 3: Password with Eye Toggle
                    HStack(spacing: 12) {
                        Text("🛡️")
                            .font(.system(size: 16))

                        if showPassword {
                            TextField("Password", text: $password)
                                .font(.system(size: 14.5, design: .monospaced))
                                .foregroundColor(isDark ? .white : .black)
                                .plainTextFieldStyle()
                        } else {
                            SecureField("Password", text: $password)
                                .font(.system(size: 14.5, design: .monospaced))
                                .foregroundColor(isDark ? .white : .black)
                                .plainTextFieldStyle()
                        }

                        Button(action: {
                            triggerHaptic()
                            showPassword.toggle()
                        }) {
                            Text(showPassword ? "👁️" : "🔒")
                                .font(.system(size: 16))
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.horizontal, 14)
                    .frame(height: 52)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(isDark ? Color.black.opacity(0.35) : Color.black.opacity(0.04))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08), lineWidth: 1.2)
                    )

                    // Terms Checkbox
                    if authMode == .register {
                        Button(action: {
                            triggerHaptic()
                            agreeTerms.toggle()
                        }) {
                            HStack(spacing: 10) {
                                ZStack {
                                    RoundedRectangle(cornerRadius: 5, style: .continuous)
                                        .stroke(agreeTerms ? Color(red: 0.62, green: 0.52, blue: 1.0) : Color.gray, lineWidth: 1.5)
                                        .background(
                                            RoundedRectangle(cornerRadius: 5, style: .continuous)
                                                .fill(agreeTerms ? Color(red: 0.62, green: 0.52, blue: 1.0) : Color.clear)
                                        )
                                        .frame(width: 20, height: 20)

                                    if agreeTerms {
                                        Text("✓")
                                            .font(.system(size: 12, weight: .black))
                                            .foregroundColor(.white)
                                    }
                                }

                                Text("I agree to the ")
                                    .foregroundColor(Color(red: 0.58, green: 0.64, blue: 0.72))
                                    .font(.system(size: 12.5, design: .monospaced)) +
                                Text("terms and conditions")
                                    .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                                    .fontWeight(.bold)
                                    .font(.system(size: 12.5, design: .monospaced))
                            }
                        }
                        .buttonStyle(.plain)
                        .padding(.top, 4)
                    }

                    // Primary Action Button: Sign Up / Sign In
                    Button(action: {
                        triggerHaptic()
                        handleSubmit()
                    }) {
                        ZStack {
                            Capsule(style: .continuous)
                                .fill(Color(red: 0.62, green: 0.52, blue: 1.0))
                                .frame(height: 54)
                                .shadow(color: Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.45), radius: 14, x: 0, y: 4)

                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: Color(red: 0.04, green: 0.06, blue: 0.10)))
                            } else {
                                Text(authMode == .register ? "Sign Up" : "Sign In")
                                    .font(.system(size: 16, weight: .black, design: .monospaced))
                                    .foregroundColor(Color(red: 0.04, green: 0.06, blue: 0.10))
                            }
                        }
                    }
                    .buttonStyle(.plain)
                    .disabled(isLoading)
                    .padding(.top, 8)

                    // Divider 'or'
                    HStack(spacing: 14) {
                        Rectangle()
                            .fill(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08))
                            .frame(height: 1)

                        Text("or")
                            .font(.system(size: 13, design: .monospaced))
                            .foregroundColor(Color(red: 0.39, green: 0.45, blue: 0.55))

                        Rectangle()
                            .fill(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08))
                            .frame(height: 1)
                    }
                    .padding(.vertical, 14)

                    // Social SSO Buttons (Google e GitHub)
                    HStack(spacing: 16) {
                        // Google
                        Button(action: {
                            handleSocialLogin(provider: "Google")
                        }) {
                            HStack(spacing: 8) {
                                Text("G")
                                    .font(.system(size: 18, weight: .black, design: .monospaced))
                                    .foregroundColor(.white)
                                Text("Google")
                                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                                    .foregroundColor(.white)
                            }
                            .frame(maxWidth: .infinity)
                            .frame(height: 46)
                            .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(Color.red.opacity(0.85)))
                        }
                        .buttonStyle(.plain)

                        // GitHub
                        Button(action: {
                            handleSocialLogin(provider: "GitHub")
                        }) {
                            HStack(spacing: 8) {
                                Text("⌥")
                                    .font(.system(size: 18, weight: .black))
                                    .foregroundColor(.white)
                                Text("GitHub")
                                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                                    .foregroundColor(.white)
                            }
                            .frame(maxWidth: .infinity)
                            .frame(height: 46)
                            .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(Color(red: 0.14, green: 0.16, blue: 0.18)))
                        }
                        .buttonStyle(.plain)
                    }

                    // Guest Mode
                    Button(action: {
                        triggerHaptic()
                        viewModel.userName = "visitante"
                        viewModel.userRole = "Visitante (sem histórico de pontos)"
                        viewModel.xp = 0
                        viewModel.streak = 0
                        viewModel.isLoggedIn = true
                    }) {
                        HStack(spacing: 8) {
                            Text("👤")
                            Text("Continuar como Visitante (sem cadastro)")
                                .font(.system(size: 12, weight: .bold, design: .monospaced))
                                .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.12))
                        )
                    }
                    .buttonStyle(.plain)
                    .padding(.top, 4)

                    // Switch Mode Button
                    Button(action: {
                        triggerHaptic()
                        authMode = (authMode == .register ? .login : .register)
                        feedbackText = nil
                    }) {
                        HStack(spacing: 4) {
                            Text(authMode == .register ? "Already have an account?" : "Don't have an account?")
                                .foregroundColor(Color(red: 0.58, green: 0.64, blue: 0.72))
                            Text(authMode == .register ? "Sign In" : "Sign Up")
                                .fontWeight(.bold)
                                .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                        }
                        .font(.system(size: 13.5, design: .monospaced))
                        .frame(maxWidth: .infinity, alignment: .center)
                    }
                    .buttonStyle(.plain)
                    .padding(.top, 14)
                }
                .padding(24)
                .liquidGlass(
                    cornerRadius: 32,
                    isDark: isDark,
                    isSelected: false,
                    displacementScale: 36
                )
                .padding(.horizontal, 16)
                .padding(.top, 10)
            }
            .padding(.bottom, 40)
        }
        .safeAreaInset(edge: .top) {
            formTopHeader
        }
    }

    private var formTopHeader: some View {
        HStack {
            Button(action: {
                triggerHaptic()
                screenMode = .welcome
                feedbackText = nil
            }) {
                Text("‹")
                    .font(.system(size: 34, weight: .light))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
            }
            .buttonStyle(.plain)

            Spacer()

            BrandEmblemView(size: 52)

            Spacer()

            Button(action: {
                triggerHaptic()
                viewModel.themeMode = (viewModel.themeMode == .dark ? .light : .dark)
            }) {
                Text(viewModel.themeMode == .dark ? "☀️" : "🌙")
                    .font(.system(size: 18))
                    .frame(width: 44, height: 44)
                    .background(Color.white.opacity(0.12))
                    .clipShape(Circle())
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 8)
        .background(
            Rectangle()
                .fill(Material.ultraThinMaterial)
                .overlay(
                    LinearGradient(
                        colors: [Color.white.opacity(0.06), Color.clear],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .ignoresSafeArea(edges: .top)
        )
    }

    // MARK: - Screen C: EmailJS OTP Verification Mode
    private var verifyOtpScreenView: some View {
        let isDark = viewModel.themeMode == .dark

        return ScrollView(showsIndicators: false) {
            VStack(spacing: 0) {
                // OTP Card
                VStack(alignment: .leading, spacing: 16) {
                    Text("Verify Email")
                        .font(.system(size: 28, weight: .black, design: .monospaced))
                        .foregroundColor(isDark ? .white : Color(red: 0.06, green: 0.09, blue: 0.16))

                    Text("Enviamos um código de verificação via EmailJS para:")
                        .font(.system(size: 13, design: .monospaced))
                        .foregroundColor(Color(red: 0.58, green: 0.64, blue: 0.72))

                    HStack(spacing: 6) {
                        Text("✉️")
                        Text(email)
                            .font(.system(size: 13, weight: .bold, design: .monospaced))
                            .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(
                        Capsule(style: .continuous)
                            .fill(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.15))
                    )

                    if let feedback = feedbackText {
                        HStack {
                            Text(feedback)
                                .font(.system(size: 12.5, weight: .bold, design: .monospaced))
                                .foregroundColor(feedbackIsError ? ThemeColors.rose : ThemeColors.mintGreen)
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(feedbackIsError ? ThemeColors.rose.opacity(0.12) : ThemeColors.mintGreen.opacity(0.12))
                        )
                    }

                    // 6-digit OTP Box
                    TextField("000000", text: $inputOtp)
                        .font(.system(size: 28, weight: .black, design: .monospaced))
                        .multilineTextAlignment(.center)
                        .numericFieldStyle()
                        .frame(height: 60)
                        .background(
                            RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .fill(isDark ? Color.black.opacity(0.35) : Color.black.opacity(0.04))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .stroke(Color(red: 0.62, green: 0.52, blue: 1.0), lineWidth: 1.8)
                        )
                        .padding(.vertical, 8)

                    // Confirm Button
                    Button(action: {
                        triggerHaptic()
                        handleVerifyOtp()
                    }) {
                        Text("Confirmar e Entrar ↵")
                            .font(.system(size: 16, weight: .black, design: .monospaced))
                            .foregroundColor(Color(red: 0.04, green: 0.06, blue: 0.10))
                            .frame(maxWidth: .infinity)
                            .frame(height: 54)
                            .background(
                                Capsule(style: .continuous)
                                    .fill(Color(red: 0.62, green: 0.52, blue: 1.0))
                            )
                            .shadow(color: Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.45), radius: 14, x: 0, y: 4)
                    }
                    .buttonStyle(.plain)

                    // Resend Link
                    Button(action: {
                        triggerHaptic()
                        handleResendOtp()
                    }) {
                        Text(isLoading ? "Reenviando..." : "Reenviar código de verificação (EmailJS)")
                            .font(.system(size: 13, weight: .medium, design: .monospaced))
                            .underline()
                            .foregroundColor(isDark ? Color(red: 0.78, green: 0.71, blue: 1.0) : Color(red: 0.43, green: 0.16, blue: 0.85))
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                    .buttonStyle(.plain)
                    .disabled(isLoading)
                    .padding(.top, 6)
                }
                .padding(24)
                .liquidGlass(
                    cornerRadius: 32,
                    isDark: isDark,
                    isSelected: false,
                    displacementScale: 36
                )
                .padding(.horizontal, 16)
                .padding(.top, 10)
            }
            .padding(.bottom, 40)
        }
        .safeAreaInset(edge: .top) {
            verifyOtpTopHeader
        }
    }

    private var verifyOtpTopHeader: some View {
        HStack {
            Button(action: {
                triggerHaptic()
                screenMode = .form
                feedbackText = nil
            }) {
                Text("‹")
                    .font(.system(size: 34, weight: .light))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
            }
            .buttonStyle(.plain)

            Spacer()

            BrandEmblemView(size: 52)

            Spacer()

            Color.clear.frame(width: 44, height: 44)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 8)
        .background(
            Rectangle()
                .fill(Material.ultraThinMaterial)
                .overlay(
                    LinearGradient(
                        colors: [Color.white.opacity(0.06), Color.clear],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .ignoresSafeArea(edges: .top)
        )
    }

    // MARK: - Actions & EmailJS Calls
    private func handleSubmit() {
        let cleanUser = username.trimmingCharacters(in: .whitespaces)
        let cleanEmail = email.trimmingCharacters(in: .whitespaces)
        let cleanPass = password.trimmingCharacters(in: .whitespaces)

        if cleanUser.isEmpty {
            feedbackText = "Informe um nome de usuário."
            feedbackIsError = true
            return
        }

        if authMode == .register {
            if cleanEmail.isEmpty || !cleanEmail.contains("@") {
                feedbackText = "Informe um endereço de e-mail válido."
                feedbackIsError = true
                return
            }
            if cleanPass.count < 4 {
                feedbackText = "A senha deve conter no mínimo 4 caracteres."
                feedbackIsError = true
                return
            }
            if !agreeTerms {
                feedbackText = "É necessário aceitar os termos de serviço."
                feedbackIsError = true
                return
            }

            isLoading = true
            feedbackText = nil

            let code = EmailJSService.shared.generateVerificationCode()
            generatedOtp = code

            Task {
                let result = await EmailJSService.shared.sendVerificationEmail(toEmail: cleanEmail, toName: cleanUser, code: code)
                await MainActor.run {
                    isLoading = false
                    if result.success {
                        screenMode = .verifyOtp
                        feedbackIsError = false
                        feedbackText = result.simulated ? "ℹ️ [Simulado]: Código de teste é \(code)" : "Código enviado com sucesso!"
                    } else {
                        feedbackIsError = true
                        feedbackText = result.message
                    }
                }
            }
        } else {
            // Direct Login
            viewModel.login(username: cleanUser, email: cleanEmail.isEmpty ? "\(cleanUser)@devopshero.io" : cleanEmail, role: "DevOps Engineer · SRE")
        }
    }

    private func handleVerifyOtp() {
        let cleanInput = inputOtp.trimmingCharacters(in: .whitespaces)
        if cleanInput.isEmpty {
            feedbackText = "Digite o código de 6 dígitos."
            feedbackIsError = true
            return
        }
        if cleanInput != generatedOtp {
            feedbackText = "Código incorreto. Verifique seu e-mail."
            feedbackIsError = true
            return
        }

        viewModel.login(username: username.trimmingCharacters(in: .whitespaces), email: email.trimmingCharacters(in: .whitespaces), role: "DevOps Engineer · SRE")
    }

    private func handleResendOtp() {
        isLoading = true
        let newCode = EmailJSService.shared.generateVerificationCode()
        generatedOtp = newCode

        Task {
            let result = await EmailJSService.shared.sendVerificationEmail(toEmail: email.trimmingCharacters(in: .whitespaces), toName: username.trimmingCharacters(in: .whitespaces), code: newCode)
            await MainActor.run {
                isLoading = false
                feedbackIsError = !result.success
                feedbackText = result.simulated ? "ℹ️ [Novo código simulado]: \(newCode)" : "Novo código reenviado com sucesso!"
            }
        }
    }

    private func handleSocialLogin(provider: String) {
        let handle = "\(provider.lowercased())_operator"
        viewModel.login(username: handle, email: "\(handle)@devopshero.io", role: "\(provider) Certified DevOps")
    }
}

private extension View {
    @ViewBuilder
    func plainTextFieldStyle() -> some View {
        #if os(iOS)
        self
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled(true)
        #else
        self.autocorrectionDisabled(true)
        #endif
    }

    @ViewBuilder
    func emailFieldStyle() -> some View {
        #if os(iOS)
        self
            .keyboardType(.emailAddress)
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled(true)
        #else
        self.autocorrectionDisabled(true)
        #endif
    }

    @ViewBuilder
    func numericFieldStyle() -> some View {
        #if os(iOS)
        self
            .keyboardType(.numberPad)
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled(true)
        #else
        self.autocorrectionDisabled(true)
        #endif
    }
}
