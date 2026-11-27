import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

/// PracticeView - Interactive Code Assembly & Terminal Lab
/// 100% Parity with devopshero-mobile/src/screens/PracticeScreen.tsx
/// Apple HIG & iPhone 17 Pro Max Framing:
/// - Pinned Liquid Glass Header via .safeAreaInset(edge: .top)
/// - Pinned Liquid Glass Sticky Action Bar via .safeAreaInset(edge: .bottom)
/// - Full Liquid Glass on Code Editor Window & Word Bank Tray
public struct PracticeView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    public var body: some View {
        let isDark = viewModel.themeMode == .dark

        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 16) {
                // Apple Live Activities & Dynamic Island In-App Banner Preview
                DevOpsDynamicIslandPreviewBanner()
                    .padding(.top, 4)

                // 1. Code Editor Terminal Window with Syntax Highlighted Command Assembly
                codeEditorWindow(isDark: isDark)

                // 2. Word Bank Tray (Available Tokens)
                wordBankTray(isDark: isDark)
            }
            .padding(.horizontal, 16)
            .padding(.top, 10)
            .padding(.bottom, 20)
        }
        .safeAreaInset(edge: .top) {
            pinnedTopBar(isDark: isDark)
        }
        .safeAreaInset(edge: .bottom) {
            pinnedBottomBar(isDark: isDark)
        }
        .sheet(isPresented: $viewModel.showEvaluationSheet) {
            EvaluationSheetView(viewModel: viewModel)
                .presentationDetents([.fraction(0.65)])
        }
        .alert(viewModel.hasMoreTips ? "💡 Dica \(viewModel.currentTipNumber) de \(viewModel.maxTips)" : "🛑 Limite de Dicas", isPresented: $viewModel.showTipModal) {
            Button("Entendido", role: .cancel) { }
        } message: {
            Text(viewModel.currentTipText)
        }
    }

    // MARK: - 1. Pinned Navigation Header
    private func pinnedTopBar(isDark: Bool) -> some View {
        VStack(spacing: 6) {
            HStack(spacing: 8) {
                // Back Button (‹ Início)
                Button(action: {
                    triggerHaptic()
                    viewModel.exitToHome()
                }) {
                    HStack(spacing: 4) {
                        Text("‹")
                            .font(.system(size: 26, weight: .bold))
                        Text("Início")
                            .font(.system(size: 16, weight: .bold))
                    }
                    .foregroundColor(ThemeColors.azureCyan)
                    .frame(minWidth: 44, minHeight: 44)
                }
                .buttonStyle(.plain)

                // Track and Mission Status
                VStack(alignment: .leading, spacing: 2) {
                    if let track = viewModel.currentTrack {
                        Text(track.name)
                            .font(.system(size: 15, weight: .heavy))
                            .foregroundColor(isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22))
                            .lineLimit(1)

                        Text("Missão \(viewModel.selectedMissionIndex + 1) de \(track.missions.count)")
                            .font(.system(size: 12, weight: .semibold, design: .monospaced))
                            .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.39, green: 0.40, blue: 0.95))
                            .lineLimit(1)
                    }
                }

                Spacer()

                // Pause Button
                Button(action: {
                    triggerHaptic()
                    viewModel.pauseTrack()
                }) {
                    Text("⏸ Pausar")
                        .font(.system(size: 12.5, weight: .heavy, design: .monospaced))
                        .foregroundColor(ThemeColors.amber)
                        .padding(.horizontal, 9)
                        .padding(.vertical, 6)
                        .background(ThemeColors.amber.opacity(0.14))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                .stroke(ThemeColors.amber.opacity(0.50), lineWidth: 1.2)
                        )
                }
                .buttonStyle(.plain)

                // Live Timer
                Text("⏱️ \(viewModel.secondsElapsed)s")
                    .font(.system(size: 12.5, weight: .heavy, design: .monospaced))
                    .foregroundColor(viewModel.secondsElapsed <= 5 ? ThemeColors.neonGreen : (isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22)))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 6)
                    .background(isDark ? Color.white.opacity(0.08) : Color.black.opacity(0.05))
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8, style: .continuous)
                            .stroke(viewModel.secondsElapsed <= 5 ? ThemeColors.neonGreen : (isDark ? Color.white.opacity(0.14) : Color.black.opacity(0.08)), lineWidth: 1.2)
                    )
            }
            .padding(.horizontal, 16)
            .padding(.top, 4)

            // Progress Track
            if let track = viewModel.currentTrack {
                let pct = Double(viewModel.selectedMissionIndex + 1) / Double(max(1, track.missions.count))
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule(style: .continuous)
                            .fill(isDark ? Color.white.opacity(0.10) : Color.black.opacity(0.08))
                            .frame(height: 4)

                        Capsule(style: .continuous)
                            .fill(ThemeColors.azureCyan)
                            .frame(width: max(geo.size.width * pct, 8), height: 4)
                    }
                }
                .frame(height: 4)
                .padding(.horizontal, 16)
                .padding(.bottom, 6)
            }
        }
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

    // MARK: - 2. Code Editor Terminal Window
    private func codeEditorWindow(isDark: Bool) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            // Editor Header Tab Bar
            HStack {
                HStack(spacing: 6) {
                    Circle().fill(Color(red: 1.0, green: 0.37, blue: 0.34)).frame(width: 8, height: 8)
                    Circle().fill(Color(red: 1.0, green: 0.74, blue: 0.18)).frame(width: 8, height: 8)
                    Circle().fill(Color(red: 0.15, green: 0.79, blue: 0.25)).frame(width: 8, height: 8)
                }
                .padding(.trailing, 6)

                Text("\(viewModel.currentMission?.title ?? "terminal").sh")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.28, green: 0.33, blue: 0.41))
                    .lineLimit(1)

                Spacer()

                if let xp = viewModel.currentMission?.xp {
                    Text("⭐ \(xp) XP")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(ThemeColors.azureCyan)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(ThemeColors.azureCyan.opacity(0.14))
                        .cornerRadius(6)
                }
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 9)
            .background(isDark ? Color.black.opacity(0.20) : Color.black.opacity(0.04))

            Divider().background(isDark ? Color.white.opacity(0.08) : Color.black.opacity(0.06))

            // Editor Code Lines Area
            VStack(alignment: .leading, spacing: 10) {
                // Line 1: Comment with Mission Objective
                HStack(alignment: .top, spacing: 10) {
                    Text("1")
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? Color(red: 0.40, green: 0.45, blue: 0.55) : Color(red: 0.58, green: 0.64, blue: 0.72))
                        .frame(width: 16, alignment: .trailing)

                    Text("# \(viewModel.currentMission?.objective ?? "Monte o comando solicitado")")
                        .font(.system(size: 13, weight: .semibold, design: .monospaced))
                        .foregroundColor(isDark ? Color(red: 0.58, green: 0.64, blue: 0.75) : Color(red: 0.39, green: 0.45, blue: 0.54))
                        .lineLimit(nil)
                }

                // Line 2: Terminal Prompt & Dynamic Receptacle
                HStack(alignment: .top, spacing: 10) {
                    Text("2")
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? Color(red: 0.40, green: 0.45, blue: 0.55) : Color(red: 0.58, green: 0.64, blue: 0.72))
                        .frame(width: 16, alignment: .trailing)
                        .padding(.top, 7)

                    HStack(spacing: 8) {
                        Text("$")
                            .font(.system(size: 14, weight: .bold, design: .monospaced))
                            .foregroundColor(ThemeColors.neonGreen)
                            .padding(.top, 7)

                        // Slot Receptacle
                        Group {
                            if viewModel.placedChips.isEmpty {
                                Text("toque nos blocos abaixo para montar...")
                                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                                    .italic()
                                    .foregroundColor(isDark ? Color(red: 0.45, green: 0.50, blue: 0.62) : Color(red: 0.58, green: 0.64, blue: 0.72))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 8)
                            } else {
                                FlowLayout(spacing: 6) {
                                    ForEach(Array(viewModel.placedChips.enumerated()), id: \.offset) { idx, chipText in
                                        let tokenColor = syntaxColorForToken(chipText)
                                        Button(action: {
                                            triggerHaptic()
                                            viewModel.removeChip(at: idx)
                                        }) {
                                            Text(chipText)
                                                .font(.system(size: 13, weight: .bold, design: .monospaced))
                                                .foregroundColor(tokenColor)
                                                .padding(.horizontal, 9)
                                                .padding(.vertical, 4.5)
                                                .background(tokenColor.opacity(0.18))
                                                .cornerRadius(6)
                                                .overlay(
                                                    RoundedRectangle(cornerRadius: 6, style: .continuous)
                                                        .stroke(tokenColor.opacity(0.65), lineWidth: 1.2)
                                                )
                                        }
                                        .buttonStyle(.plain)
                                    }
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 5)
                            }
                        }
                        .frame(maxWidth: .infinity, minHeight: 38, alignment: .leading)
                        .background(
                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                .fill(viewModel.placedChips.isEmpty ? Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.06) : Color.black.opacity(0.25))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 8, style: .continuous)
                                .stroke(
                                    viewModel.placedChips.isEmpty
                                        ? Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.40)
                                        : Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.30),
                                    style: StrokeStyle(lineWidth: 1.2, dash: viewModel.placedChips.isEmpty ? [4, 4] : [])
                                )
                        )
                    }
                }
            }
            .padding(14)
        }
        .liquidGlass(
            cornerRadius: 20,
            isDark: isDark,
            isSelected: false,
            displacementScale: 32
        )
    }

    // MARK: - 3. Word Bank Tray (Tokens)
    private func wordBankTray(isDark: Bool) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            // Tray Header
            HStack {
                HStack(spacing: 5) {
                    Text("⌨️")
                        .font(.system(size: 11))
                    Text("TOKENS")
                        .font(.system(size: 11, weight: .black, design: .monospaced))
                        .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 3)
                .background(
                    RoundedRectangle(cornerRadius: 6, style: .continuous)
                        .fill(isDark ? Color.black.opacity(0.30) : Color.black.opacity(0.06))
                )

                Spacer()

                Text("toque para selecionar")
                    .font(.system(size: 11.5, weight: .medium, design: .monospaced))
                    .italic()
                    .foregroundColor(isDark ? Color(red: 0.55, green: 0.60, blue: 0.72) : Color(red: 0.39, green: 0.45, blue: 0.54))
            }

            Divider().background(isDark ? Color.white.opacity(0.06) : Color.black.opacity(0.06))

            FlowLayout(spacing: 8) {
                ForEach(viewModel.availableChips) { chip in
                    let tokenColor = syntaxColorForToken(chip.text)
                    Button(action: {
                        if !chip.isPlaced {
                            triggerHaptic()
                            viewModel.addChip(chipId: chip.id, text: chip.text)
                        }
                    }) {
                        Text(chip.text)
                            .font(.system(size: 13.5, weight: .bold, design: .monospaced))
                            .foregroundColor(chip.isPlaced ? Color.white.opacity(0.22) : tokenColor)
                            .padding(.horizontal, 14)
                            .padding(.vertical, 8)
                            .frame(minHeight: 40)
                            .background(
                                RoundedRectangle(cornerRadius: 10, style: .continuous)
                                    .fill(chip.isPlaced ? Color.black.opacity(0.25) : (isDark ? Color(red: 0.15, green: 0.18, blue: 0.31) : Color(red: 0.92, green: 0.94, blue: 0.97)))
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 10, style: .continuous)
                                    .stroke(
                                        chip.isPlaced ? Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.20) : tokenColor.opacity(0.60),
                                        style: StrokeStyle(lineWidth: 1.4, dash: chip.isPlaced ? [3, 3] : [])
                                    )
                            )
                            .shadow(color: chip.isPlaced ? Color.clear : tokenColor.opacity(0.18), radius: 4, x: 0, y: 2)
                    }
                    .disabled(chip.isPlaced)
                    .buttonStyle(.plain)
                }
            }
        }
        .padding(14)
        .liquidGlass(
            cornerRadius: 20,
            isDark: isDark,
            isSelected: false,
            displacementScale: 28
        )
    }

    // MARK: - 4. Pinned Bottom Sticky Action Bar
    private func pinnedBottomBar(isDark: Bool) -> some View {
        VStack(spacing: 10) {
            // Row 1: Assist Buttons (Dica & Gabarito)
            HStack(spacing: 10) {
                // Tip Button
                Button(action: {
                    triggerHaptic()
                    viewModel.openTip()
                }) {
                    HStack(spacing: 6) {
                        Text("💡 DICA")
                            .font(.system(size: 13, weight: .black, design: .monospaced))
                            .foregroundColor(viewModel.tipsUsed >= viewModel.maxTips ? (isDark ? Color(red: 0.45, green: 0.50, blue: 0.60) : Color(red: 0.39, green: 0.45, blue: 0.54)) : (isDark ? ThemeColors.amber : Color(red: 0.71, green: 0.33, blue: 0.04)))

                        Text("\(viewModel.tipsUsed)/\(viewModel.maxTips)")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(viewModel.tipsUsed >= viewModel.maxTips ? (isDark ? Color(red: 0.45, green: 0.50, blue: 0.60) : Color(red: 0.39, green: 0.45, blue: 0.54)) : (isDark ? ThemeColors.amber : Color(red: 0.71, green: 0.33, blue: 0.04)))
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(
                                Capsule(style: .continuous)
                                    .fill(viewModel.tipsUsed >= viewModel.maxTips ? Color.white.opacity(0.08) : ThemeColors.amber.opacity(0.16))
                            )
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 46)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(isDark ? Color(red: 0.12, green: 0.14, blue: 0.24) : Color(red: 0.94, green: 0.95, blue: 0.98))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(viewModel.tipsUsed >= viewModel.maxTips ? Color.white.opacity(0.10) : ThemeColors.amber.opacity(0.40), lineWidth: 1.2)
                    )
                }
                .buttonStyle(.plain)

                // Solution / Gabarito Button
                Button(action: {
                    triggerHaptic()
                    viewModel.revealSolution()
                }) {
                    HStack(spacing: 6) {
                        Text("👁️ GABARITO")
                            .font(.system(size: 13, weight: .black, design: .monospaced))
                            .foregroundColor(isDark ? ThemeColors.rose : Color(red: 0.75, green: 0.07, blue: 0.24))

                        Text("0 XP")
                            .font(.system(size: 10.5, weight: .bold, design: .monospaced))
                            .foregroundColor(isDark ? ThemeColors.rose : Color(red: 0.75, green: 0.07, blue: 0.24))
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(
                                Capsule(style: .continuous)
                                    .fill(ThemeColors.rose.opacity(0.15))
                            )
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 46)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(isDark ? Color(red: 0.12, green: 0.14, blue: 0.24) : Color(red: 0.94, green: 0.95, blue: 0.98))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(ThemeColors.rose.opacity(0.40), lineWidth: 1.2)
                    )
                }
                .buttonStyle(.plain)
            }

            // Row 2: Primary Verification Button: Lilac #9E85FF
            Button(action: {
                triggerHaptic()
                viewModel.verifyCommand()
            }) {
                Text(viewModel.placedChips.isEmpty ? "toque nos blocos para montar" : "VERIFICAR RESPOSTA ↵")
                    .font(.system(size: 15, weight: .black, design: .monospaced))
                    .italic(viewModel.placedChips.isEmpty)
                    .foregroundColor(viewModel.placedChips.isEmpty ? (isDark ? Color(red: 0.55, green: 0.60, blue: 0.72) : Color(red: 0.39, green: 0.45, blue: 0.54)) : Color(red: 0.04, green: 0.06, blue: 0.10))
                    .frame(maxWidth: .infinity, alignment: .center)
                    .frame(height: 54)
                    .background(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(viewModel.placedChips.isEmpty ? (isDark ? Color(red: 0.12, green: 0.14, blue: 0.24) : Color(red: 0.90, green: 0.92, blue: 0.95)) : Color(red: 0.62, green: 0.52, blue: 1.0))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .stroke(viewModel.placedChips.isEmpty ? (isDark ? Color.white.opacity(0.10) : Color.black.opacity(0.08)) : Color.clear, lineWidth: 1.2)
                    )
                    .shadow(color: viewModel.placedChips.isEmpty ? Color.clear : Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.45), radius: 12, x: 0, y: 4)
            }
            .disabled(viewModel.placedChips.isEmpty)
            .buttonStyle(.plain)

            // Row 3: Secondary Navigation (Pausar Trilha • Voltar ao Início)
            HStack(spacing: 12) {
                Button(action: {
                    triggerHaptic()
                    viewModel.pauseTrack()
                }) {
                    Text("⏸ Pausar Trilha")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? ThemeColors.amber : Color(red: 0.71, green: 0.33, blue: 0.04))
                        .padding(.horizontal, 14)
                        .padding(.vertical, 7)
                        .background(
                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                .fill(isDark ? Color(red: 0.12, green: 0.14, blue: 0.24) : Color(red: 0.94, green: 0.95, blue: 0.98))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                .stroke(ThemeColors.amber.opacity(0.35), lineWidth: 1)
                        )
                }
                .buttonStyle(.plain)

                Text("•")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? Color.white.opacity(0.20) : Color.black.opacity(0.20))

                Button(action: {
                    triggerHaptic()
                    viewModel.exitToHome()
                }) {
                    Text("🏠 Voltar para o Início")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? ThemeColors.azureCyan : Color(red: 0.01, green: 0.41, blue: 0.63))
                        .padding(.horizontal, 14)
                        .padding(.vertical, 7)
                        .background(
                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                .fill(isDark ? Color(red: 0.12, green: 0.14, blue: 0.24) : Color(red: 0.94, green: 0.95, blue: 0.98))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                .stroke(ThemeColors.azureCyan.opacity(0.35), lineWidth: 1)
                        )
                }
                .buttonStyle(.plain)
            }
            .padding(.top, 2)
        }
        .padding(.horizontal, 16)
        .padding(.top, 10)
        .padding(.bottom, 12)
        .background(
            Rectangle()
                .fill(Material.ultraThinMaterial)
                .overlay(
                    LinearGradient(
                        colors: [
                            isDark ? Color.white.opacity(0.12) : Color.white.opacity(0.60),
                            Color.clear
                        ],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .overlay(
                    Divider().background(Color.white.opacity(0.08)),
                    alignment: .top
                )
                .ignoresSafeArea(edges: .bottom)
        )
    }

    private func triggerHaptic() {
        #if canImport(UIKit)
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.prepare()
        generator.impactOccurred()
        #endif
    }

    private func syntaxColorForToken(_ token: String) -> Color {
        let lower = token.lowercased()
        if ["docker", "kubectl", "git", "chmod", "aws", "terraform", "cat", "grep", "ls", "pwd", "mkdir", "datadog-agent"].contains(lower) {
            return Color(red: 0.98, green: 0.44, blue: 0.52) // coral / command
        } else if lower.hasPrefix("-") {
            return Color(red: 0.98, green: 0.75, blue: 0.14) // amber / flags
        } else if ["run", "build", "commit", "push", "pull", "apply", "init", "plan", "exec", "ps", "stop", "start", "logs", "create", "delete", "get"].contains(lower) {
            return Color(red: 0.62, green: 0.52, blue: 1.0) // lilac / subcommands
        } else if lower.contains(":") || lower.contains("/") || lower.contains(".") || lower.hasPrefix("\"") || lower.hasPrefix("'") {
            return Color(red: 0.0, green: 0.88, blue: 0.55) // mint green / parameters/values
        }
        return Color(red: 0.0, green: 0.94, blue: 0.99) // cyan / default args
    }
}

// Simple FlowLayout helper for chips
public struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    public func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let width = proposal.width ?? 320
        var height: CGFloat = 0
        var x: CGFloat = 0
        var y: CGFloat = 0
        var maxHeightInRow: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > width, x > 0 {
                x = 0
                y += maxHeightInRow + spacing
                maxHeightInRow = 0
            }
            x += size.width + spacing
            maxHeightInRow = max(maxHeightInRow, size.height)
            height = max(height, y + maxHeightInRow)
        }
        return CGSize(width: width, height: max(height, maxHeightInRow))
    }

    public func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        var x = bounds.minX
        var y = bounds.minY
        var maxHeightInRow: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > bounds.maxX, x > bounds.minX {
                x = bounds.minX
                y += maxHeightInRow + spacing
                maxHeightInRow = 0
            }
            subview.place(at: CGPoint(x: x, y: y), proposal: .unspecified)
            x += size.width + spacing
            maxHeightInRow = max(maxHeightInRow, size.height)
        }
    }
}
