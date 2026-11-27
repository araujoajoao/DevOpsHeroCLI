import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

/// FloatingDockView - Liquid Glass Floating Tab Bar (LiquidLensView Architecture)
/// 100% Parity with devopshero-mobile/src/components/FloatingDock.tsx
/// Features:
/// - Real Apple systemUltraThinMaterial frosted glass capsule
/// - Translucent crystal body allowing ambient orbs to shine through
/// - Directional -45° specular glare reflection
/// - Chromatic refraction bevel on top rim
/// - Morphing Liquid Lens active pill with neon rim, specular highlight, and drop shadow
/// - Taptic Engine haptic responses
public struct FloatingDockView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    private let visibleTabs: [TabType] = [.home, .tracks, .profile]

    public var body: some View {
        let isDark = viewModel.themeMode == .dark

        HStack(spacing: 8) {
            ForEach(visibleTabs) { tab in
                let isActive = viewModel.activeTab == tab
                let color = tabColor(tab)

                Button(action: {
                    triggerHaptic()
                    withAnimation(.spring(response: 0.35, dampingFraction: 0.72)) {
                        viewModel.activeTab = tab
                    }
                }) {
                    HStack(spacing: 6) {
                        Text(tab.icon)
                            .font(.system(size: 17))

                        if isActive {
                            Text(tab.label)
                                .font(.system(size: 13, weight: .bold, design: .monospaced))
                                .foregroundColor(color)
                        }
                    }
                    .padding(.horizontal, isActive ? 16 : 12)
                    .frame(height: 44)
                    .background(
                        ZStack {
                            if isActive {
                                RoundedRectangle(cornerRadius: 18, style: .continuous)
                                    .fill(color.opacity(isDark ? 0.28 : 0.20))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                                            .stroke(color, lineWidth: 1.5)
                                    )
                                    .overlay(
                                        LinearGradient(
                                            colors: [Color.white.opacity(0.45), Color.white.opacity(0.10), Color.clear],
                                            startPoint: .topLeading,
                                            endPoint: .bottomTrailing
                                        )
                                        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                                    )
                                    .shadow(color: color.opacity(0.55), radius: 8, x: 0, y: 3)
                            }
                        }
                    )
                }
                .buttonStyle(.plain)
                .contentShape(Rectangle())
            }
        }
        .padding(.horizontal, 14)
        .frame(maxWidth: 380)
        .frame(height: 64)
        .liquidGlass(
            cornerRadius: 26,
            isDark: isDark,
            isSelected: false,
            displacementScale: 36
        )
        .padding(.horizontal, 16)
    }

    private func triggerHaptic() {
        #if canImport(UIKit)
        let impact = UIImpactFeedbackGenerator(style: .light)
        impact.impactOccurred()
        #endif
    }

    private func tabColor(_ tab: TabType) -> Color {
        switch tab {
        case .home: return Color(red: 0.62, green: 0.52, blue: 1.0) // Lilac #9E85FF
        case .tracks: return Color(red: 0.0, green: 0.88, blue: 0.54) // Mint #00DF89
        case .practice: return Color(red: 0.0, green: 1.0, blue: 0.53) // Neon Green #00ff87
        case .profile: return Color(red: 0.0, green: 0.95, blue: 1.0) // Azure Cyan #00f2fe
        }
    }
}
