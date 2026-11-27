import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

/// HomeView - Official Career Path Cards Screen
/// 100% Parity with devopshero-mobile/src/screens/HomeScreen.tsx
/// Apple HIG & iPhone 17 Pro Max Framing:
/// - Pinned Liquid Glass Top Bar via .safeAreaInset(edge: .top)
/// - Continuous Squircle Curvature (.continuous)
/// - Authentic Liquid Glass Material with Optical Refraction
public struct HomeView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel
    @State private var selectedCardIndex: Int = 0

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    private var tracks: [Track] {
        viewModel.dataset?.tracks ?? []
    }

    public var body: some View {
        let isDark = viewModel.themeMode == .dark

        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 18) {
                // Career Paths Section Title
                Text("Career Paths")
                    .font(.system(size: 20, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? .white : Color(red: 0.1, green: 0.12, blue: 0.22))
                    .padding(.horizontal, 20)
                    .padding(.top, 16)

                // Official Vertical Stack of Career Path Cards
                LazyVStack(spacing: 16) {
                    ForEach(Array(tracks.enumerated()), id: \.element.id) { index, track in
                        cardView(track: track, index: index, isCurrentSelected: index == selectedCardIndex)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 24)
            }
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
    }

    // MARK: - 1. Pinned Top Bar View
    private var topBarView: some View {
        let isDark = viewModel.themeMode == .dark

        return HStack(alignment: .center) {
            // Left: Profile Avatar with Glowing Ring
            Button(action: {
                triggerHaptic()
                viewModel.activeTab = .profile
            }) {
                ZStack {
                    Circle()
                        .stroke(
                            LinearGradient(
                                colors: [Color(red: 0.62, green: 0.52, blue: 1.0), Color(red: 0.0, green: 0.88, blue: 0.54), Color(red: 0.0, green: 0.95, blue: 1.0)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 2.2
                        )
                        .frame(width: 44, height: 44)
                        .shadow(color: Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.50), radius: 6, x: 0, y: 0)

                    Circle()
                        .fill(isDark ? Color(red: 0.12, green: 0.14, blue: 0.24) : Color.white)
                        .frame(width: 38, height: 38)

                    Text("👨‍💻")
                        .font(.system(size: 19))
                }
                .frame(width: 44, height: 44)
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Abrir Perfil do Operador")

            Spacer()

            // Center: Title 'DevOpsHero'
            Text("DevOpsHero")
                .font(.system(size: 17, weight: .bold, design: .monospaced))
                .foregroundColor(isDark ? Color(red: 0.92, green: 0.94, blue: 1.0) : Color(red: 0.08, green: 0.10, blue: 0.22))

            Spacer()

            // Right: Update Pill & Theme Toggle
            HStack(spacing: 8) {
                if viewModel.hasUpdateAvailable {
                    Button(action: {
                        triggerHaptic()
                        viewModel.showUpdateModal = true
                    }) {
                        Text("UPDATE")
                            .font(.system(size: 10, weight: .heavy, design: .monospaced))
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .frame(height: 30)
                            .background(Color(red: 0.878, green: 0.322, blue: 0.212))
                            .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }

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
        }
        .frame(height: 48)
    }

    // MARK: - 2. Single DevOps Career Path Card
    private func cardView(track: Track, index: Int, isCurrentSelected: Bool) -> some View {
        let isDark = viewModel.themeMode == .dark
        let isUnlocked = viewModel.isTrackUnlocked(track)
        let completedMissions = index == 0 ? 8 : (index == 1 ? 1 : 6)
        let totalMissions = track.missionsCount > 0 ? track.missionsCount : 10
        let progressRatio = Double(completedMissions) / Double(totalMissions)

        return Button(action: {
            triggerHaptic()
            selectedCardIndex = index
            if isUnlocked {
                viewModel.selectTrack(index: index)
            }
        }) {
            VStack(alignment: .leading, spacing: 12) {
                // Row 1: Single Tech Badge with Real Logo + Lock Pill
                HStack {
                    TrackIconView(trackId: track.id, size: 20, badgeSize: 34, showBadge: true)

                    Spacer()

                    if !isUnlocked {
                        HStack(spacing: 4) {
                            Text("🔒")
                                .font(.system(size: 10))
                            Text("\(track.requiredXp ?? 0) XP")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                        }
                        .foregroundColor(isDark ? Color(red: 0.98, green: 0.82, blue: 0.30) : Color(red: 0.71, green: 0.33, blue: 0.04))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(isDark ? Color.black.opacity(0.40) : Color(red: 0.96, green: 0.62, blue: 0.05).opacity(0.15))
                        .clipShape(Capsule(style: .continuous))
                        .overlay(
                            Capsule(style: .continuous)
                                .stroke(isDark ? Color(red: 0.98, green: 0.82, blue: 0.30).opacity(0.35) : Color(red: 0.71, green: 0.33, blue: 0.04).opacity(0.25), lineWidth: 1)
                        )
                    }
                }

                // Row 2: Track Title in Tech Monospaced Font
                Text(track.name)
                    .font(.system(size: 18, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22))
                    .lineLimit(1)

                // Row 3: Section / Missions Label
                HStack {
                    Text("SECTION")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.39, green: 0.40, blue: 0.95))

                    Spacer()

                    Text("\(completedMissions)/\(totalMissions)")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(isDark ? Color(red: 0.78, green: 0.82, blue: 0.99) : Color(red: 0.28, green: 0.33, blue: 0.41))
                }

                // Row 4: Lilac Rounded Progress Bar with Specular Sheen
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule(style: .continuous)
                            .fill(isDark ? Color.white.opacity(0.10) : Color.black.opacity(0.08))
                            .frame(height: 7)

                        Capsule(style: .continuous)
                            .fill(Color(red: 0.62, green: 0.52, blue: 1.0)) // Lilac #9E85FF
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
            .padding(18)
            .liquidGlass(
                cornerRadius: 24,
                isDark: isDark,
                isSelected: isCurrentSelected,
                selectedColor: Color(red: 0.62, green: 0.52, blue: 1.0)
            )
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
