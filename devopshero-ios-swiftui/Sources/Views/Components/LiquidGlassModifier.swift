import SwiftUI

/// LiquidGlassModifier - Implements Apple Liquid Glass principles based on LiquidGlassKit & rdev/liquid-glass-react
/// 100% Parity with devopshero-mobile/src/components/LiquidGlassView.tsx:
/// - Real Apple Backdrop Material (.ultraThinMaterial)
/// - Optical Refraction & Edge Bending via displacementScale (0-64)
/// - Refractive Corner Caustics (light focusing through squircle geometry)
/// - Directional Specular Glare (-45° angle convex lens sheen)
/// - Fresnel Rim Lighting (high specular edge highlight on incident angle)
/// - Chromatic Aberration & Dispersion Fringe (prismatic spectral refraction)
/// - Continuous squircle corner rounding with soft ambient occlusion shadows
/// - Active / Lifted state with neon ambient glow
public struct LiquidGlassModifier: ViewModifier {
    public var cornerRadius: CGFloat = 20
    public var isDark: Bool = true
    public var isSelected: Bool = false
    public var selectedColor: Color = Color(red: 0.62, green: 0.52, blue: 1.0) // Lilac #9E85FF
    public var showSheen: Bool = true
    public var showDispersion: Bool = true
    public var displacementScale: CGFloat = 32
    public var chromaticAberration: CGFloat = 1.5

    public func body(content: Content) -> some View {
        let refractionFactor = min(max(displacementScale / 64.0, 0), 1.0)

        content
            .background(
                ZStack {
                    // 1. Native Apple Backdrop Frosted Material
                    RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                        .fill(Material.ultraThinMaterial)

                    // 2. Base Translucent Material Tint (True Crystal Liquid Glass allowing vibrant aurora to shine through)
                    RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                        .fill(
                            isDark
                                ? Color(red: 0.11, green: 0.14, blue: 0.26).opacity(0.48) // Subtle slate-navy crystal tint
                                : Color.white.opacity(0.48)
                        )

                    // 3. Optical Refraction & Edge Bending Map (liquid-glass-react displacementScale parity)
                    if refractionFactor > 0 {
                        LinearGradient(
                            colors: isDark
                                ? [
                                    Color.white.opacity(0.14 * refractionFactor),
                                    Color.white.opacity(0.04 * refractionFactor),
                                    Color.clear,
                                    Color.black.opacity(0.18 * refractionFactor)
                                ]
                                : [
                                    Color.white.opacity(0.42 * refractionFactor),
                                    Color.white.opacity(0.12 * refractionFactor),
                                    Color.clear,
                                    Color.black.opacity(0.06 * refractionFactor)
                                ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))

                        // Corner Caustic Focus (light bending through squircle curves)
                        VStack {
                            HStack {
                                RadialGradient(
                                    colors: isDark
                                        ? [
                                            Color.white.opacity(0.26 * refractionFactor),
                                            Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.14 * refractionFactor),
                                            Color.clear
                                        ]
                                        : [
                                            Color.white.opacity(0.65 * refractionFactor),
                                            Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.18 * refractionFactor),
                                            Color.clear
                                        ],
                                    center: .topLeading,
                                    startRadius: 0,
                                    endRadius: cornerRadius * 2.5
                                )
                                .frame(width: cornerRadius * 3, height: cornerRadius * 3)
                                Spacer()
                            }
                            Spacer()
                        }
                        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
                    }

                    // 4. Directional Specular Glare (-45° Sheen)
                    if showSheen {
                        LinearGradient(
                            colors: isDark
                                ? [
                                    Color.white.opacity(0.42),
                                    Color.white.opacity(0.14),
                                    Color.white.opacity(0.02),
                                    Color.clear
                                ]
                                : [
                                    Color.white.opacity(0.95),
                                    Color.white.opacity(0.48),
                                    Color.white.opacity(0.12),
                                    Color.clear
                                ],
                            startPoint: .topLeading,
                            endPoint: UnitPoint(x: 0.80, y: 0.80)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
                    }

                    // 5. Chromatic Dispersion Fringe (Prismatic Refraction Bevel)
                    if showDispersion {
                        VStack {
                            LinearGradient(
                                colors: [
                                    Color(red: 0.62, green: 0.52, blue: 1.0).opacity(isDark ? 0.40 : 0.28), // Lilac
                                    Color(red: 0.0, green: 0.95, blue: 1.0).opacity(isDark ? 0.30 : 0.20),  // Cyan
                                    Color.white.opacity(isDark ? 0.50 : 0.75),                              // Highlight
                                    Color(red: 0.0, green: 0.88, blue: 0.54).opacity(isDark ? 0.30 : 0.20), // Mint
                                    Color.clear
                                ],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                            .frame(height: chromaticAberration)
                            Spacer()
                        }
                        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
                    }

                    // 6. Active Selection Neon Energy Overlay
                    if isSelected {
                        LinearGradient(
                            colors: [selectedColor.opacity(0.24), selectedColor.opacity(0.06), Color.clear],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
                    }
                }
            )
            // 7. Fresnel Rim Stroke & Bevel Highlights (Double Rim)
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(
                        isSelected
                            ? selectedColor
                            : (isDark ? Color.white.opacity(0.30) : Color.white.opacity(0.88)),
                        lineWidth: isSelected ? 2.4 : 1.2
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: max(0, cornerRadius - 1), style: .continuous)
                    .stroke(
                        isSelected
                            ? selectedColor.opacity(0.50)
                            : (isDark ? Color.white.opacity(0.16) : Color.white.opacity(0.65)),
                        lineWidth: 0.75
                    )
                    .padding(1)
            )
            // 8. Multi-Stage Soft Ambient Shadow
            .shadow(
                color: isSelected
                    ? selectedColor.opacity(0.55)
                    : Color.black.opacity(isDark ? 0.28 : 0.08),
                radius: isSelected ? 18 : 12,
                x: 0,
                y: isSelected ? 6 : 4
            )
    }
}

public extension View {
    func liquidGlass(
        cornerRadius: CGFloat = 20,
        isDark: Bool = true,
        isSelected: Bool = false,
        selectedColor: Color = Color(red: 0.62, green: 0.52, blue: 1.0),
        showSheen: Bool = true,
        showDispersion: Bool = true,
        displacementScale: CGFloat = 32,
        chromaticAberration: CGFloat = 1.5
    ) -> some View {
        modifier(LiquidGlassModifier(
            cornerRadius: cornerRadius,
            isDark: isDark,
            isSelected: isSelected,
            selectedColor: selectedColor,
            showSheen: showSheen,
            showDispersion: showDispersion,
            displacementScale: displacementScale,
            chromaticAberration: chromaticAberration
        ))
    }
}
