import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

/// ProfileView - DevOps Operator Profile Screen
/// 100% Parity with devopshero-mobile/src/screens/ProfileScreen.tsx
/// Apple HIG & iPhone 17 Pro Max Framing:
/// - Pinned Liquid Glass Header via .safeAreaInset(edge: .top)
/// - Continuous Squircle Curvature (.continuous)
/// - Liquid Glass Identity & Performance Cards
public struct ProfileView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    public var body: some View {
        let isDark = viewModel.themeMode == .dark

        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 18) {
                // Section Title
                Text("DevOps Operator")
                    .font(.system(size: 20, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? .white : Color(red: 0.1, green: 0.12, blue: 0.22))
                    .padding(.top, 16)

                // Seniority Level & Lilac Progress Bar
                seniorityProgressRow

                // Operator Identity Card
                operatorIdentityCard(isDark: isDark)

                // Performance Metrics Grid
                metricsGrid(isDark: isDark)

                // System & Security Profile Card
                systemProfileCard(isDark: isDark)
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 24)
        }
        .safeAreaInset(edge: .top) {
            topBarView
                .padding(.horizontal, 20)
                .padding(.vertical, 8)
                .background(
                    Rectangle()
                        .fill(Material.ultraThinMaterial)
                        .overlay(
                            LinearGradient(
                                colors: [
                                    isDark ? Color.white.opacity(0.06) : Color.white.opacity(0.50),
                                    Color.clear
                                ],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        .overlay(
                            Divider().background(Color.white.opacity(0.08)),
                            alignment: .bottom
                        )
                        .ignoresSafeArea(edges: .top)
                )
        }
        .alert("Alterar Operador", isPresented: $viewModel.showingEditUser) {
            TextField("Nome de usuário", text: $viewModel.newUsername)
            Button("Salvar") {
                let trimmed = viewModel.newUsername.trimmingCharacters(in: .whitespaces)
                if !trimmed.isEmpty {
                    viewModel.userName = trimmed
                }
            }
            Button("Cancelar", role: .cancel) { }
        }
    }

    // MARK: - 1. Pinned Top Navigation Bar
    private var topBarView: some View {
        let isDark = viewModel.themeMode == .dark
        let titleColor = isDark ? Color(red: 0.85, green: 0.88, blue: 0.98) : Color(red: 0.12, green: 0.16, blue: 0.25)

        return HStack {
            // Left: '✕' Button to return to Home
            Button(action: {
                triggerHaptic()
                viewModel.activeTab = .home
            }) {
                ZStack {
                    Circle()
                        .fill(isDark ? Color.white.opacity(0.08) : Color.black.opacity(0.05))
                        .frame(width: 44, height: 44)
                        .overlay(
                            Circle().stroke(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08), lineWidth: 1)
                        )

                    Text("✕")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.28, green: 0.33, blue: 0.41))
                }
                .frame(width: 44, height: 44)
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Voltar para Início")

            Spacer()

            // Center: Title 'DevOps Profile'
            Text("DevOps Profile")
                .font(.system(size: 17, weight: .bold, design: .monospaced))
                .foregroundColor(titleColor)

            Spacer()

            // Right: Theme Toggle (44x44 area)
            Button(action: {
                triggerHaptic()
                viewModel.toggleTheme()
            }) {
                ZStack {
                    Circle()
                        .fill(isDark ? Color.white.opacity(0.08) : Color.black.opacity(0.05))
                        .frame(width: 44, height: 44)
                        .overlay(
                            Circle().stroke(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08), lineWidth: 1)
                        )

                    Text(isDark ? "☀️" : "🌙")
                        .font(.system(size: 18))
                }
                .frame(width: 44, height: 44)
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Alternar tema")
        }
        .frame(height: 48)
    }

    // MARK: - 2. Seniority & XP Progress Row
    private var seniorityProgressRow: some View {
        let isDark = viewModel.themeMode == .dark
        let progressRatio = min(Double(viewModel.xp) / 500.0, 1.0)

        return VStack(spacing: 8) {
            HStack {
                Text("SENIORITY LEVEL")
                    .font(.system(size: 11, weight: .heavy, design: .monospaced))
                    .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.39, green: 0.40, blue: 0.95))

                Spacer()

                Text("PLENO · \(viewModel.xp)/500 XP")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? Color(red: 0.78, green: 0.82, blue: 0.99) : Color(red: 0.28, green: 0.33, blue: 0.41))
            }

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule(style: .continuous)
                        .fill(isDark ? Color.white.opacity(0.10) : Color.black.opacity(0.08))
                        .frame(height: 7)

                    Capsule(style: .continuous)
                        .fill(ThemeColors.lilac)
                        .frame(width: max(geo.size.width * CGFloat(progressRatio), 14), height: 7)
                        .overlay(
                            LinearGradient(
                                colors: [Color.white.opacity(0.40), Color.clear],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                            .clipShape(Capsule(style: .continuous))
                        )
                }
            }
            .frame(height: 7)
        }
    }

    // MARK: - 3. Operator Identity Card in Liquid Glass
    private func operatorIdentityCard(isDark: Bool) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            // Top Row: Avatar Badge + Active Online Pill
            HStack(alignment: .center) {
                ZStack {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .fill(isDark ? Color.black.opacity(0.35) : Color.white)
                        .frame(width: 34, height: 34)

                    Text("👨‍💻")
                        .font(.system(size: 19))
                }

                VStack(alignment: .leading, spacing: 2) {
                    Text("@\(viewModel.userName)")
                        .font(.system(size: 19, weight: .bold, design: .monospaced))
                        .foregroundColor(ThemeColors.neonGreen)
                        .lineLimit(1)

                    Text(viewModel.userRole)
                        .font(.system(size: 13, weight: .semibold, design: .monospaced))
                        .foregroundColor(isDark ? Color(red: 0.85, green: 0.88, blue: 0.99) : Color(red: 0.20, green: 0.24, blue: 0.36))
                        .lineLimit(1)
                }
                .padding(.leading, 6)

                Spacer()

                // Status Pill Badge
                HStack(spacing: 4) {
                    Circle()
                        .fill(ThemeColors.neonGreen)
                        .frame(width: 7, height: 7)
                    Text("ONLINE")
                        .font(.system(size: 11, weight: .heavy, design: .monospaced))
                        .foregroundColor(ThemeColors.neonGreen)
                }
                .padding(.horizontal, 9)
                .padding(.vertical, 4)
                .background(ThemeColors.neonGreen.opacity(0.14))
                .clipShape(Capsule(style: .continuous))
            }

            Divider().background(isDark ? Color.white.opacity(0.08) : Color.black.opacity(0.06))

            // Session Metadata Rows
            VStack(spacing: 8) {
                metaLine(key: "Sessão CLI:", val: "devops@ops-lab (● ATIVO)", valColor: ThemeColors.neonGreen)
                metaLine(key: "Ambiente SRE:", val: "Local Core Engine v1.1.0", valColor: ThemeColors.azureCyan)
                metaLine(key: "Chave SSH:", val: "ed25519 · [rw-r--r--]", valColor: isDark ? Color(red: 0.85, green: 0.88, blue: 0.98) : Color(red: 0.15, green: 0.18, blue: 0.32))
            }

            // Action Buttons Row (Trocar Usuário & Encerrar Sessão)
            HStack(spacing: 12) {
                Button(action: {
                    triggerHaptic()
                    viewModel.showingEditUser = true
                }) {
                    Text("Trocar Usuário")
                        .font(.system(size: 13.5, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? ThemeColors.azureCyan : Color(red: 0.01, green: 0.41, blue: 0.63))
                        .frame(maxWidth: .infinity)
                        .frame(height: 44)
                        .background(ThemeColors.azureCyan.opacity(0.14))
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .stroke(ThemeColors.azureCyan.opacity(0.50), lineWidth: 1.2)
                        )
                }
                .buttonStyle(.plain)

                Button(action: {
                    triggerHaptic()
                    viewModel.logout()
                }) {
                    Text("Encerrar Sessão")
                        .font(.system(size: 13.5, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? ThemeColors.rose : Color(red: 0.75, green: 0.07, blue: 0.24))
                        .frame(maxWidth: .infinity)
                        .frame(height: 44)
                        .background(ThemeColors.rose.opacity(0.14))
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .stroke(ThemeColors.rose.opacity(0.50), lineWidth: 1.2)
                        )
                }
                .buttonStyle(.plain)
            }
            .padding(.top, 4)
        }
        .padding(18)
        .liquidGlass(
            cornerRadius: 22,
            isDark: isDark,
            isSelected: false,
            displacementScale: 32
        )
    }

    private func metaLine(key: String, val: String, valColor: Color) -> some View {
        HStack {
            Text(key)
                .font(.system(size: 12, weight: .medium, design: .monospaced))
                .foregroundColor(viewModel.themeMode == .dark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.40, green: 0.45, blue: 0.60))

            Spacer()

            Text(val)
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundColor(valColor)
        }
    }

    // MARK: - 4. Performance Metrics Grid in Liquid Glass
    private func metricsGrid(isDark: Bool) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("$ cat /var/log/learning_metrics.tsv")
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundColor(ThemeColors.neonGreen)

            LazyVGrid(columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)], spacing: 12) {
                metricCard(key: "[TOTAL MISSIONS]", val: "80", desc: "Missões Oficiais", color: ThemeColors.azureCyan, isDark: isDark)
                metricCard(key: "[DAILY STREAK]", val: "\(viewModel.streak)d", desc: "Dias Consecutivos", color: ThemeColors.amber, isDark: isDark)
                metricCard(key: "[TOTAL XP]", val: "\(viewModel.xp) XP", desc: "Pontos Acumulados", color: ThemeColors.neonGreen, isDark: isDark)
                metricCard(key: "[ACTIVE TRACKS]", val: "08", desc: "Disciplinas CLI", color: ThemeColors.lilac, isDark: isDark)
            }
        }
    }

    private func metricCard(key: String, val: String, desc: String, color: Color, isDark: Bool) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(key)
                .font(.system(size: 11, weight: .heavy, design: .monospaced))
                .foregroundColor(color)

            Text(val)
                .font(.system(size: 22, weight: .bold, design: .monospaced))
                .foregroundColor(isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22))

            Text(desc)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.40, green: 0.45, blue: 0.60))
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .liquidGlass(
            cornerRadius: 18,
            isDark: isDark,
            isSelected: false,
            displacementScale: 24
        )
    }

    // MARK: - 5. System Profile Card in Liquid Glass
    private func systemProfileCard(isDark: Bool) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("2  ➜  ~ whoami --security")
                .font(.system(size: 13, weight: .bold, design: .monospaced))
                .foregroundColor(ThemeColors.neonGreen)

            VStack(spacing: 6) {
                metaLine(key: "Cluster Auth:", val: "Bearer OTP (EmailJS Validated)", valColor: isDark ? Color(red: 0.85, green: 0.88, blue: 0.98) : Color(red: 0.15, green: 0.18, blue: 0.32))
                metaLine(key: "SAIF Security:", val: "Level-3 Compliant", valColor: ThemeColors.azureCyan)
                metaLine(key: "Storage Volume:", val: "Persistent Local SQLite", valColor: ThemeColors.amber)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .liquidGlass(
            cornerRadius: 20,
            isDark: isDark,
            isSelected: false,
            displacementScale: 28
        )
    }

    private func triggerHaptic() {
        #if canImport(UIKit)
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
        #endif
    }
}
