import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

/// EvaluationSheetView - Question Evaluation Drawer with Retro CRT Mascot
/// 100% Parity with devopshero-mobile and Mimo Code Flow (media_1793714309288_cf334ed3.png)
/// Features:
/// - Pinned Status Pill: 'Almost there..' / 'Excelente!' / 'Gabarito Oficial'
/// - Retro CRT Terminal Mascot with interactive screen expressions
/// - Guidance Speech Bubble with '✨ GET HELP' action
/// - Syntax-highlighted verification box & XP Score Audit
/// - Lilac Bottom Full-Width Action Button ('↺ TRY AGAIN' / 'CONTINUAR ➔')
public struct EvaluationSheetView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    private var isCorrect: Bool {
        viewModel.isCorrect
    }

    private var solutionUsed: Bool {
        viewModel.solutionUsed
    }

    public var body: some View {
        let isDark = viewModel.themeMode == .dark
        let lilacColor = Color(red: 0.62, green: 0.52, blue: 1.0) // #9E85FF

        VStack(spacing: 0) {
            // Drag Handle Indicator
            Capsule()
                .fill(isDark ? Color.white.opacity(0.25) : Color.black.opacity(0.20))
                .frame(width: 42, height: 5)
                .padding(.top, 12)
                .padding(.bottom, 16)

            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 18) {
                    // Header Pill Tag
                    HStack {
                        headerPillTag
                        Spacer()
                    }

                    // Main Row: Retro CRT Terminal Mascot + Speech Bubble with Feedback
                    HStack(alignment: .top, spacing: 14) {
                        TerminalMascotView(
                            isCorrect: isCorrect,
                            solutionUsed: solutionUsed,
                            isDark: isDark
                        )
                        .frame(width: 68, height: 72)

                        feedbackBubbleView(isDark: isDark)
                    }

                    // Answer / Solution Verification Box
                    if let mission = viewModel.currentMission {
                        solutionCodeBox(mission: mission, isDark: isDark)
                    }

                    // XP Score & Streak Audit
                    if isCorrect && !solutionUsed, let award = viewModel.lastAward {
                        scoreAuditCard(award: award, isDark: isDark)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 24)
            }

            // Bottom Full-Width Action Button
            actionButtonView(lilacColor: lilacColor)
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
        }
        .background(
            ZStack {
                RoundedRectangle(cornerRadius: 32, style: .continuous)
                    .fill(isDark ? Color(red: 0.10, green: 0.12, blue: 0.22).opacity(0.92) : Color.white.opacity(0.94))
            }
            .background(Material.ultraThinMaterial)
            .ignoresSafeArea()
        )
    }

    // MARK: - 1. Header Pill Tag
    private var headerPillTag: some View {
        let tagText: String
        let tagColor: Color
        let tagBg: Color

        if solutionUsed {
            tagText = "Gabarito Oficial"
            tagColor = Color(red: 0.98, green: 0.75, blue: 0.14) // Amber
            tagBg = Color(red: 0.98, green: 0.75, blue: 0.14).opacity(0.16)
        } else if isCorrect {
            tagText = "Excelente!"
            tagColor = Color(red: 0.0, green: 0.88, blue: 0.55) // Neon Green
            tagBg = Color(red: 0.0, green: 0.88, blue: 0.55).opacity(0.16)
        } else {
            tagText = "Almost there.."
            tagColor = Color(red: 0.98, green: 0.42, blue: 0.52) // Coral / Salmon Pink
            tagBg = Color(red: 0.98, green: 0.42, blue: 0.52).opacity(0.16)
        }

        return Text(tagText)
            .font(.system(size: 13, weight: .black, design: .monospaced))
            .foregroundColor(tagColor)
            .padding(.horizontal, 12)
            .padding(.vertical, 5)
            .background(tagBg)
            .clipShape(Capsule(style: .continuous))
            .overlay(
                Capsule(style: .continuous)
                    .stroke(tagColor.opacity(0.40), lineWidth: 1.2)
            )
    }

    // MARK: - 2. Interactive Speech / Guidance Bubble in Liquid Glass
    private func feedbackBubbleView(isDark: Bool) -> some View {
        let textColor = isDark ? Color.white : Color(red: 0.08, green: 0.10, blue: 0.22)

        return VStack(alignment: .leading, spacing: 10) {
            if isCorrect {
                Text(solutionUsed ? "Você consultou a solução oficial desta missão. Revise a sintaxe abaixo para fixar o aprendizado." : "Comando validado e executado com sucesso no container!")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(textColor)
                    .lineSpacing(3)
            } else {
                if let mission = viewModel.currentMission {
                    Text(mission.tip.isEmpty ? "A ordem dos parâmetros ou argumentos precisa de ajuste no terminal." : mission.tip)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(textColor)
                        .lineSpacing(3)
                }
            }

            if !isCorrect {
                Button(action: {
                    triggerHaptic()
                    viewModel.openTip()
                }) {
                    HStack(spacing: 5) {
                        Image(systemName: "sparkles")
                            .font(.system(size: 12, weight: .bold))
                        Text(viewModel.tipsUsed >= viewModel.maxTips ? "Dicas Esgotadas" : "GET HELP")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(
                        RoundedRectangle(cornerRadius: 8, style: .continuous)
                            .fill(Color(red: 0.22, green: 0.26, blue: 0.42))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 8, style: .continuous)
                            .stroke(Color.white.opacity(0.15), lineWidth: 1)
                    )
                }
                .buttonStyle(.plain)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .liquidGlass(
            cornerRadius: 16,
            isDark: isDark,
            isSelected: false,
            displacementScale: 24
        )
    }

    // MARK: - 3. Command Syntax Code Box in Liquid Glass
    private func solutionCodeBox(mission: Mission, isDark: Bool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(isCorrect ? "✓ LINHA DE COMANDO EXECUTADA" : "📖 COMANDO ESPERADO")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(isCorrect ? Color(red: 0.0, green: 0.88, blue: 0.55) : Color(red: 0.62, green: 0.52, blue: 1.0))

                Spacer()

                Text("bash")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.55, green: 0.60, blue: 0.78))
            }

            HStack(spacing: 6) {
                Text("$")
                    .font(.system(size: 15, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.0, green: 0.94, blue: 0.99))

                Text(mission.solution)
                    .font(.system(size: 15, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.0, green: 0.88, blue: 0.55))
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(isDark ? Color.black.opacity(0.35) : Color.black.opacity(0.06))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
        }
        .padding(14)
        .liquidGlass(
            cornerRadius: 14,
            isDark: isDark,
            isSelected: false,
            displacementScale: 20
        )
    }

    // MARK: - 4. Score Audit Card in Liquid Glass
    private func scoreAuditCard(award: AwardResult, isDark: Bool) -> some View {
        VStack(spacing: 8) {
            HStack {
                Text("+\(award.xp) XP")
                    .font(.system(size: 26, weight: .black, design: .monospaced))
                    .foregroundColor(Color(red: 0.0, green: 0.88, blue: 0.55))

                Spacer()

                Text(award.tierName)
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.98, green: 0.75, blue: 0.14))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color(red: 0.98, green: 0.75, blue: 0.14).opacity(0.16))
                    .cornerRadius(6)
            }

            Divider().background(Color.white.opacity(0.08))

            HStack {
                Text("⏱️ TEMPO TOTAL:")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.55, green: 0.60, blue: 0.78))
                Spacer()
                Text("\(Int(award.elapsedSeconds))s")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? .white : Color(red: 0.04, green: 0.06, blue: 0.10))
            }

            HStack {
                Text("🔥 BÔNUS STREAK:")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.55, green: 0.60, blue: 0.78))
                Spacer()
                Text("+\(award.streakBonusPct)%")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.0, green: 0.94, blue: 0.99))
            }
        }
        .padding(14)
        .liquidGlass(
            cornerRadius: 14,
            isDark: isDark,
            isSelected: false,
            displacementScale: 20
        )
    }

    // MARK: - 5. Bottom Full-Width Action Button (Lilac #9E85FF)
    private func actionButtonView(lilacColor: Color) -> some View {
        Button(action: {
            triggerHaptic()
            viewModel.continueAfterEvaluation()
        }) {
            HStack(spacing: 8) {
                if !isCorrect {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 16, weight: .bold))
                    Text("TRY AGAIN")
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                } else {
                    Text(solutionUsed ? "AVANÇAR ETAPA" : "CONTINUAR")
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                    Image(systemName: "arrow.right")
                        .font(.system(size: 16, weight: .bold))
                }
            }
            .foregroundColor(Color(red: 0.04, green: 0.06, blue: 0.10))
            .frame(maxWidth: .infinity)
            .frame(height: 54)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(lilacColor)
            )
            .shadow(color: lilacColor.opacity(0.40), radius: 10, x: 0, y: 4)
        }
        .buttonStyle(.plain)
    }

    private func triggerHaptic() {
        #if canImport(UIKit)
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
        #endif
    }
}

// MARK: - Retro CRT Terminal Mascot View
public struct TerminalMascotView: View {
    let isCorrect: Bool
    let solutionUsed: Bool
    let isDark: Bool

    public init(isCorrect: Bool, solutionUsed: Bool, isDark: Bool) {
        self.isCorrect = isCorrect
        self.solutionUsed = solutionUsed
        self.isDark = isDark
    }

    public var body: some View {
        VStack(spacing: 2) {
            // Monitor Body
            ZStack {
                // Outer CRT Bezel
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: isDark
                                ? [Color(red: 0.90, green: 0.92, blue: 0.96), Color(red: 0.78, green: 0.82, blue: 0.88)]
                                : [Color(red: 0.35, green: 0.40, blue: 0.55), Color(red: 0.25, green: 0.30, blue: 0.42)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .frame(width: 60, height: 50)
                    .shadow(color: Color.black.opacity(0.20), radius: 4, x: 0, y: 2)

                // Screen Display
                ZStack {
                    RoundedRectangle(cornerRadius: 8, style: .continuous)
                        .fill(Color(red: 0.08, green: 0.09, blue: 0.16)) // Dark CRT Screen
                        .frame(width: 46, height: 36)

                    // CRT Screen Face Expression
                    if !isCorrect {
                        Image(systemName: "xmark")
                            .font(.system(size: 18, weight: .black, design: .monospaced))
                            .foregroundColor(Color(red: 0.98, green: 0.42, blue: 0.52))
                    } else if solutionUsed {
                        HStack(spacing: 6) {
                            Circle().fill(Color(red: 0.98, green: 0.75, blue: 0.14)).frame(width: 5, height: 5)
                            Circle().fill(Color(red: 0.98, green: 0.75, blue: 0.14)).frame(width: 5, height: 5)
                        }
                    } else {
                        Image(systemName: "checkmark")
                            .font(.system(size: 18, weight: .black, design: .monospaced))
                            .foregroundColor(Color(red: 0.0, green: 0.88, blue: 0.55))
                    }
                }

                // CRT Stand LED dot
                Circle()
                    .fill(isCorrect ? Color(red: 0.0, green: 0.88, blue: 0.55) : Color(red: 0.98, green: 0.42, blue: 0.52))
                    .frame(width: 4, height: 4)
                    .offset(x: 18, y: 19)
            }

            // Monitor Feet
            HStack(spacing: 8) {
                Capsule()
                    .fill(Color(red: 0.65, green: 0.70, blue: 0.80))
                    .frame(width: 14, height: 6)
                Capsule()
                    .fill(Color(red: 0.65, green: 0.70, blue: 0.80))
                    .frame(width: 14, height: 6)
            }
        }
    }
}
