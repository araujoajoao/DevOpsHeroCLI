import SwiftUI
import Combine
#if os(iOS)
import UIKit
#endif

public struct AppUpdateModalView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel
    @State private var progress: Double = 0.0
    @State private var isCompleted: Bool = false
    @State private var showWhatsNew: Bool = false
    let timer = Timer.publish(every: 0.12, on: .main, in: .common).autoconnect()

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    private func triggerHaptic(type: String = "light") {
        #if os(iOS)
        switch type {
        case "success":
            UINotificationFeedbackGenerator().notificationOccurred(.success)
        case "medium":
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        default:
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
        }
        #endif
    }

    public var body: some View {
        ZStack {
            // Apple HIG Dimmed Modal Backdrop (48% Dimming)
            Color.black.opacity(0.48)
                .ignoresSafeArea()
                .onTapGesture {
                    triggerHaptic(type: "light")
                    viewModel.showUpdateModal = false
                }

            // Apple HIG Continuous Card (Width capped at 360-420pt)
            VStack(alignment: .leading, spacing: 0) {
                // Top Row: App Icon + Titles / Pill + Apple Standard 44pt Close Button
                HStack(alignment: .top, spacing: 12) {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .fill(Color(red: 0.878, green: 0.322, blue: 0.212)) // #E05236
                        .frame(width: 44, height: 44)
                        .overlay(
                            Image(systemName: "bolt.fill")
                                .font(.system(size: 22, weight: .bold))
                                .foregroundColor(.white)
                        )
                        .shadow(color: Color(red: 0.878, green: 0.322, blue: 0.212).opacity(0.3), radius: 6, x: 0, y: 3)

                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 6) {
                            Text("DevOpsHero")
                                .font(.system(.headline, design: .default).weight(.bold))
                                .foregroundColor(Color(uiColor: .label))

                            Text("by @araujoajoao")
                                .font(.system(.caption, design: .default))
                                .foregroundColor(Color(uiColor: .secondaryLabel))

                            Text("UPDATE")
                                .font(.system(size: 9, weight: .heavy, design: .default))
                                .foregroundColor(.white)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2.5)
                                .background(Color(red: 0.878, green: 0.322, blue: 0.212))
                                .clipShape(RoundedRectangle(cornerRadius: 4, style: .continuous))
                        }

                        Text("v1.0.0 to \(viewModel.targetVersion)")
                            .font(.system(.caption, design: .monospaced))
                            .foregroundColor(Color(uiColor: .secondaryLabel))
                    }

                    Spacer()

                    // Apple HIG 44x44pt Accessible Close Button with SF Symbol
                    Button(action: {
                        triggerHaptic(type: "light")
                        viewModel.showUpdateModal = false
                    }) {
                        Image(systemName: "xmark")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(Color(uiColor: .tertiaryLabel))
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                }

                // Middle Section: Progress Indicator & Status Line
                VStack(alignment: .leading, spacing: 10) {
                    HStack(spacing: 8) {
                        if isCompleted {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.system(size: 15, weight: .bold))
                                .foregroundColor(.green)
                        } else {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle())
                                .scaleEffect(0.85)
                        }

                        Text(isCompleted ? "DevOpsHero atualizado com sucesso!" : "Downloading and installing update...")
                            .font(.system(.subheadline, design: .default).weight(.medium))
                            .foregroundColor(Color(uiColor: .label))
                    }

                    // Native-styled Continuous Progress Track
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            RoundedRectangle(cornerRadius: 2, style: .continuous)
                                .fill(Color(uiColor: .systemFill))
                                .frame(height: 3.5)

                            RoundedRectangle(cornerRadius: 2, style: .continuous)
                                .fill(isCompleted ? Color.green : Color(red: 0.878, green: 0.322, blue: 0.212))
                                .frame(width: geo.size.width * CGFloat(progress / 100.0), height: 3.5)
                                .animation(.linear(duration: 0.12), value: progress)
                        }
                    }
                    .frame(height: 3.5)
                }
                .padding(.top, 16)
                .padding(.bottom, 6)

                // Expandable What's New Box (Apple HIG Inset Grouped style)
                if showWhatsNew {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("O que há de novo na versão 0.21.0:")
                            .font(.system(.caption, design: .default).weight(.bold))
                            .foregroundColor(Color(uiColor: .label))
                            .padding(.bottom, 2)

                        Group {
                            HStack(alignment: .top, spacing: 6) {
                                Image(systemName: "sparkles")
                                    .font(.system(size: 10))
                                    .foregroundColor(Color(red: 0.878, green: 0.322, blue: 0.212))
                                    .padding(.top, 2)
                                Text("8 Trilhas alinhadas às documentações oficiais")
                                    .font(.system(.caption, design: .default))
                                    .foregroundColor(Color(uiColor: .secondaryLabel))
                            }

                            HStack(alignment: .top, spacing: 6) {
                                Image(systemName: "lock.shield.fill")
                                    .font(.system(size: 10))
                                    .foregroundColor(Color(red: 0.878, green: 0.322, blue: 0.212))
                                    .padding(.top, 2)
                                Text("Bloqueio estrito de trilhas por Senioridade e XP")
                                    .font(.system(.caption, design: .default))
                                    .foregroundColor(Color(uiColor: .secondaryLabel))
                            }

                            HStack(alignment: .top, spacing: 6) {
                                Image(systemName: "shuffle")
                                    .font(.system(size: 10))
                                    .foregroundColor(Color(red: 0.878, green: 0.322, blue: 0.212))
                                    .padding(.top, 2)
                                Text("Modo aleatório de tarefas (Shuffled tasks) a cada sessão")
                                    .font(.system(.caption, design: .default))
                                    .foregroundColor(Color(uiColor: .secondaryLabel))
                            }

                            HStack(alignment: .top, spacing: 6) {
                                Image(systemName: "terminal.fill")
                                    .font(.system(size: 10))
                                    .foregroundColor(Color(red: 0.878, green: 0.322, blue: 0.212))
                                    .padding(.top, 2)
                                Text("Novo comando nativo 'dh update' no terminal")
                                    .font(.system(.caption, design: .default))
                                    .foregroundColor(Color(uiColor: .secondaryLabel))
                            }
                        }
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color(uiColor: .secondarySystemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                    .padding(.top, 8)
                    .transition(.opacity.combined(with: .scale(scale: 0.98, anchor: .top)))
                }

                // Apple Hairline Divider
                Divider()
                    .padding(.vertical, 14)

                // Footer Actions: What's New Link & Apple HIG Bordered Action Button
                HStack(alignment: .center) {
                    Button(action: {
                        triggerHaptic(type: "light")
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                            showWhatsNew.toggle()
                        }
                    }) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("What's new")
                                .font(.system(.subheadline, design: .default).weight(.bold))
                                .foregroundColor(Color(uiColor: .label))

                            Rectangle()
                                .fill(Color(red: 0.878, green: 0.322, blue: 0.212))
                                .frame(height: 1.5)
                        }
                        .frame(minHeight: 44)
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)

                    Spacer()

                    // Apple HIG Bordered Secondary Button with 44pt Touch Target
                    Button(action: {
                        triggerHaptic(type: "medium")
                        viewModel.showUpdateModal = false
                    }) {
                        Text(isCompleted ? "CONCLUIR" : "DISMISS")
                            .font(.system(.caption, design: .monospaced).weight(.bold))
                            .foregroundColor(Color(uiColor: .secondaryLabel))
                            .padding(.horizontal, 22)
                            .frame(height: 36)
                            .overlay(
                                RoundedRectangle(cornerRadius: 6, style: .continuous)
                                    .stroke(Color(uiColor: .separator), lineWidth: 1)
                            )
                            .frame(minHeight: 44)
                            .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(20)
            .background(Color(uiColor: .systemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .shadow(color: Color.black.opacity(0.24), radius: 24, x: 0, y: 12)
            .padding(.horizontal, 24)
            .frame(maxWidth: 420)
        }
        .onReceive(timer) { _ in
            if progress < 100 {
                progress += 5.5
            } else if !isCompleted {
                isCompleted = true
                triggerHaptic(type: "success")
            }
        }
    }
}

#if !canImport(UIKit)
private struct FakeUIColor {
    let color: Color
    static let label = FakeUIColor(color: .primary)
    static let secondaryLabel = FakeUIColor(color: .secondary)
    static let tertiaryLabel = FakeUIColor(color: .secondary.opacity(0.7))
    static let systemFill = FakeUIColor(color: Color.gray.opacity(0.2))
    static let secondarySystemBackground = FakeUIColor(color: Color.gray.opacity(0.15))
    static let separator = FakeUIColor(color: Color.gray.opacity(0.3))
    static let systemBackground = FakeUIColor(color: Color(red: 0.12, green: 0.14, blue: 0.24))
}

private extension Color {
    init(uiColor: FakeUIColor) {
        self = uiColor.color
    }
}
#endif
