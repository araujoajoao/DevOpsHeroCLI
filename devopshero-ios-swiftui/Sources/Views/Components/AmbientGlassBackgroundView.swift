import SwiftUI

/// AmbientGlassBackgroundView - Apple Liquid Glass Atmospheric Backing Engine (iOS 27 Physics)
/// 100% Parity with devopshero-mobile/src/components/AmbientGlassBackground.tsx
/// Provides vibrant, luminous aurora light orbs and optical streaks that shine through
/// native .ultraThinMaterial frosted glass layers (LiquidGlassModifier, FloatingDock, Cards).
/// Includes smooth fluid drift animation simulating Apple physics.
public struct AmbientGlassBackgroundView: View {
    public var themeMode: ThemeMode
    @State private var isDrifting: Bool = false

    public init(themeMode: ThemeMode = .dark) {
        self.themeMode = themeMode
    }

    public var body: some View {
        let isDark = themeMode == .dark

        GeometryReader { geo in
            let w = geo.size.width
            let h = geo.size.height

            ZStack {
                // 1. Base Atmospheric Space Gradient
                LinearGradient(
                    colors: isDark
                        ? [
                            Color(red: 0.027, green: 0.035, blue: 0.078), // #070914
                            Color(red: 0.043, green: 0.055, blue: 0.125), // #0B0E20
                            Color(red: 0.071, green: 0.086, blue: 0.188), // #121630
                            Color(red: 0.027, green: 0.035, blue: 0.078)  // #070914
                        ]
                        : [
                            Color(red: 0.973, green: 0.980, blue: 0.988), // #F8FAFC
                            Color(red: 0.933, green: 0.949, blue: 1.0),   // #EEF2FF
                            Color(red: 0.878, green: 0.906, blue: 1.0),   // #E0E7FF
                            Color(red: 0.945, green: 0.961, blue: 0.976)  // #F1F5F9
                        ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                // 2. Top-Right Luminous Violet / Purple Aurora Orb
                Circle()
                    .fill(
                        RadialGradient(
                            colors: isDark
                                ? [
                                    Color(red: 0.659, green: 0.333, blue: 0.969).opacity(0.60), // #A855F7
                                    Color(red: 0.388, green: 0.400, blue: 0.945).opacity(0.35), // #6366F1
                                    Color(red: 0.545, green: 0.361, blue: 0.965).opacity(0.10), // #8B5CF6
                                    Color.clear
                                ]
                                : [
                                    Color(red: 0.659, green: 0.333, blue: 0.969).opacity(0.28),
                                    Color(red: 0.388, green: 0.400, blue: 0.945).opacity(0.15),
                                    Color.clear
                                ],
                            center: .center,
                            startRadius: 0,
                            endRadius: w * 0.58
                        )
                    )
                    .frame(width: w * 1.15, height: w * 1.15)
                    .position(x: w * 0.85 + (isDrifting ? 18 : 0), y: h * 0.08 + (isDrifting ? -14 : 0))
                    .blur(radius: 20)

                // 3. Center Atmospheric Magenta / Lilac Bloom
                Circle()
                    .fill(
                        RadialGradient(
                            colors: isDark
                                ? [
                                    Color(red: 0.851, green: 0.275, blue: 0.937).opacity(0.35), // #D946EF
                                    Color(red: 0.659, green: 0.333, blue: 0.969).opacity(0.18), // #A855F7
                                    Color.clear
                                ]
                                : [
                                    Color(red: 0.851, green: 0.275, blue: 0.937).opacity(0.18),
                                    Color(red: 0.659, green: 0.333, blue: 0.969).opacity(0.08),
                                    Color.clear
                                ],
                            center: .center,
                            startRadius: 0,
                            endRadius: w * 0.45
                        )
                    )
                    .frame(width: w * 0.90, height: w * 0.90)
                    .position(x: w * 0.25 + (isDrifting ? -16 : 0), y: h * 0.45 + (isDrifting ? 18 : 0))
                    .blur(radius: 25)

                // 4. Bottom-Left Luminous Electric Cyan / Azure Aurora Orb
                Circle()
                    .fill(
                        RadialGradient(
                            colors: isDark
                                ? [
                                    Color(red: 0.024, green: 0.714, blue: 0.831).opacity(0.50), // #06B6D4
                                    Color(red: 0.055, green: 0.647, blue: 0.914).opacity(0.28), // #0EA5E9
                                    Color(red: 0.0, green: 0.949, blue: 0.996).opacity(0.08),   // #00F2FE
                                    Color.clear
                                ]
                                : [
                                    Color(red: 0.024, green: 0.714, blue: 0.831).opacity(0.25),
                                    Color(red: 0.055, green: 0.647, blue: 0.914).opacity(0.12),
                                    Color.clear
                                ],
                            center: .center,
                            startRadius: 0,
                            endRadius: w * 0.55
                        )
                    )
                    .frame(width: w * 1.10, height: w * 1.10)
                    .position(x: w * 0.15 + (isDrifting ? 18 : 0), y: h * 0.85 + (isDrifting ? 14 : 0))
                    .blur(radius: 22)

                // 5. Bottom-Center Neon Emerald / Mint Glow (behind Dock)
                Capsule()
                    .fill(
                        RadialGradient(
                            colors: isDark
                                ? [
                                    Color(red: 0.063, green: 0.725, blue: 0.506).opacity(0.40), // #10B981
                                    Color(red: 0.020, green: 0.588, blue: 0.412).opacity(0.16), // #059669
                                    Color.clear
                                ]
                                : [
                                    Color(red: 0.063, green: 0.725, blue: 0.506).opacity(0.20),
                                    Color(red: 0.020, green: 0.588, blue: 0.412).opacity(0.08),
                                    Color.clear
                                ],
                            center: .center,
                            startRadius: 0,
                            endRadius: w * 0.48
                        )
                    )
                    .frame(width: w * 0.95, height: 140)
                    .position(x: w * 0.5, y: h * 0.94 + (isDrifting ? -8 : 0))
                    .blur(radius: 18)

                // 6. Optical Diagonal Refraction Streak Lines (-35° Angle)
                Rectangle()
                    .fill(isDark ? Color.white.opacity(0.10) : Color.black.opacity(0.04))
                    .frame(width: w * 1.25, height: 1.5)
                    .rotationEffect(.degrees(-35))
                    .position(x: w * 0.35, y: h * 0.18)
                    .blur(radius: 0.8)

                Rectangle()
                    .fill(isDark ? Color(red: 0.659, green: 0.333, blue: 0.969).opacity(0.16) : Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.08))
                    .frame(width: w * 1.15, height: 1.5)
                    .rotationEffect(.degrees(-35))
                    .position(x: w * 0.65, y: h * 0.75)
                    .blur(radius: 0.8)
            }
            .ignoresSafeArea()
            .allowsHitTesting(false)
            .onAppear {
                withAnimation(
                    .easeInOut(duration: 8.5)
                    .repeatForever(autoreverses: true)
                ) {
                    isDrifting = true
                }
            }
        }
    }
}

