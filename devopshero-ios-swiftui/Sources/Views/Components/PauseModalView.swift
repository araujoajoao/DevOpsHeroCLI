import SwiftUI

public struct PauseModalView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.75).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 18) {
                // Header
                HStack(spacing: 12) {
                    Text("⏸")
                        .font(.system(size: 22))
                        .frame(width: 44, height: 44)
                        .background(ThemeColors.amber.opacity(0.18))
                        .cornerRadius(12)

                    VStack(alignment: .leading, spacing: 2) {
                        Text("Trilha Pausada")
                            .font(.system(size: 20, weight: .heavy))
                            .foregroundColor(ThemeColors.textMain(for: viewModel.themeMode))

                        if let track = viewModel.currentTrack {
                            Text("\(track.name) · Missão \(viewModel.selectedMissionIndex + 1)")
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundColor(ThemeColors.textMuted(for: viewModel.themeMode))
                        }
                    }
                }

                // Mission info card
                if let mission = viewModel.currentMission {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(mission.title)
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(ThemeColors.textMain(for: viewModel.themeMode))

                        HStack {
                            Text("⏱️ Tempo: \(viewModel.secondsElapsed)s (pausado)")
                                .font(.system(size: 13, weight: .bold, design: .monospaced))
                                .foregroundColor(ThemeColors.neonGreen)

                            Spacer()

                            Text("⭐ \(viewModel.xp) XP")
                                .font(.system(size: 13, weight: .bold, design: .monospaced))
                                .foregroundColor(ThemeColors.azureCyan)
                        }
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(
                        RoundedRectangle(cornerRadius: 14)
                            .fill(ThemeColors.cardSubtle(for: viewModel.themeMode))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(ThemeColors.border(for: viewModel.themeMode), lineWidth: 1)
                    )
                }

                // Action 1: Resume
                Button(action: {
                    viewModel.resumeTrack()
                }) {
                    Text("▶ Continuar Prática")
                        .font(.system(size: 16, weight: .black))
                        .multilineTextAlignment(.center)
                        .foregroundColor(viewModel.themeMode == .dark ? Color(red: 0.024, green: 0.027, blue: 0.039) : .white)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .frame(height: 52)
                        .background(viewModel.themeMode == .dark ? ThemeColors.neonGreen : Color(red: 0.09, green: 0.64, blue: 0.29))
                        .cornerRadius(14)
                        .shadow(color: ThemeColors.neonGreen.opacity(0.3), radius: 8, x: 0, y: 4)
                }
                .buttonStyle(.plain)

                // Action 2: Exit to Home
                Button(action: {
                    viewModel.exitToHome()
                }) {
                    Text("🏠 Voltar para a Tela Inicial")
                        .font(.system(size: 15, weight: .bold))
                        .multilineTextAlignment(.center)
                        .foregroundColor(ThemeColors.textMain(for: viewModel.themeMode))
                        .frame(maxWidth: .infinity, alignment: .center)
                        .frame(height: 48)
                        .background(ThemeColors.cardSubtle(for: viewModel.themeMode))
                        .cornerRadius(14)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(ThemeColors.border(for: viewModel.themeMode), lineWidth: 1.2)
                        )
                }
                .buttonStyle(.plain)

                // Action 3: Switch Track
                Button(action: {
                    viewModel.exitToTracks()
                }) {
                    Text("📚 Trocar de Trilha")
                        .font(.system(size: 14, weight: .bold))
                        .multilineTextAlignment(.center)
                        .foregroundColor(viewModel.themeMode == .dark ? ThemeColors.azureCyan : Color(red: 0.01, green: 0.41, blue: 0.63))
                        .frame(maxWidth: .infinity, alignment: .center)
                        .frame(height: 40)
                }
                .buttonStyle(.plain)
            }
            .padding(22)
            .frame(maxWidth: 360)
            .background(
                RoundedRectangle(cornerRadius: 24)
                    .fill(ThemeColors.cardBackground(for: viewModel.themeMode))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 24)
                    .stroke(ThemeColors.amber, lineWidth: 1.5)
            )
            .shadow(color: Color.black.opacity(0.5), radius: 24, x: 0, y: 12)
            .padding(20)
        }
    }
}

