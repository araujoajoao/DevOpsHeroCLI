import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

/// TracksView - DevOps Path & Missions Questions Screen
/// 100% Parity with devopshero-mobile/src/screens/TracksScreen.tsx
/// Apple HIG & iPhone 17 Pro Max Framing:
/// - Pinned Liquid Glass Top Bar via .safeAreaInset(edge: .top)
/// - Continuous Squircle Curvature (.continuous)
/// - Authentic Liquid Glass Cards for All Missions
public struct TracksView: View {
    @ObservedObject var viewModel: DevOpsHeroViewModel
    @State private var showSelectPathSheet: Bool = false
    @State private var lockedAlertMissionTitle: String? = nil

    public init(viewModel: DevOpsHeroViewModel) {
        self.viewModel = viewModel
    }

    private var currentTrack: Track? {
        viewModel.currentTrack
    }

    private var missionsList: [Mission] {
        guard let track = currentTrack else { return [] }
        return viewModel.shuffledMissionsByTrack[track.id] ?? track.missions
    }

    private var completedCount: Int {
        guard let track = currentTrack else { return 0 }
        return viewModel.completedMissionsCount(for: track)
    }

    private var totalMissionsCount: Int {
        guard let track = currentTrack else { return 10 }
        return track.missionsCount > 0 ? track.missionsCount : max(missionsList.count, 10)
    }

    public var body: some View {
        let isDark = viewModel.themeMode == .dark

        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 18) {
                // 1. Track Title Row with '⇄' Switch Button
                trackTitleRow
                    .padding(.top, 16)

                // 2. Section Counter & Lilac Progress Bar
                sectionProgressRow

                // 3. Missions / Questions Cards List
                missionsCardsList
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
        .sheet(isPresented: $showSelectPathSheet) {
            selectPathBottomSheet
        }
        .alert("Etapa Bloqueada", isPresented: Binding<Bool>(
            get: { lockedAlertMissionTitle != nil },
            set: { if !$0 { lockedAlertMissionTitle = nil } }
        )) {
            Button("OK", role: .cancel) { }
        } message: {
            if let title = lockedAlertMissionTitle {
                Text("A missão \"\(title)\" requer a conclusão das etapas anteriores desta trilha.")
            }
        }
    }

    // MARK: - 1. Pinned Top Navigation Bar
    private var topBarView: some View {
        let isDark = viewModel.themeMode == .dark
        let titleColor = isDark ? Color(red: 0.85, green: 0.88, blue: 0.98) : Color(red: 0.12, green: 0.16, blue: 0.25)

        return HStack {
            // '✕' Button to return to Home
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
            .accessibilityLabel("Voltar ao início")

            Spacer()

            // Centered "DevOps Path" Title
            Text("DevOps Path")
                .font(.system(size: 17, weight: .bold, design: .monospaced))
                .foregroundColor(titleColor)

            Spacer()

            // Theme Toggle Button
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

    // MARK: - 2. Track Title Row with '⇄' Switch Button
    private var trackTitleRow: some View {
        let isDark = viewModel.themeMode == .dark

        return HStack(alignment: .center, spacing: 12) {
            Text(currentTrack?.name ?? "Full-Stack DevOps")
                .font(.system(size: 24, weight: .bold, design: .monospaced))
                .foregroundColor(isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22))
                .lineLimit(2)

            Spacer()

            Button(action: {
                triggerHaptic()
                showSelectPathSheet = true
            }) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .fill(isDark ? Color.white.opacity(0.08) : Color.black.opacity(0.05))
                        .frame(width: 44, height: 44)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .stroke(isDark ? Color.white.opacity(0.12) : Color.black.opacity(0.08), lineWidth: 1)
                        )

                    Text("⇄")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                }
                .frame(width: 44, height: 44)
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Alternar trilha")
        }
    }

    // MARK: - 3. Section Counter & Lilac Progress Bar
    private var sectionProgressRow: some View {
        let isDark = viewModel.themeMode == .dark
        let progressRatio = Double(completedCount) / Double(max(1, totalMissionsCount))

        return VStack(spacing: 8) {
            HStack {
                Text("SECTION")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.39, green: 0.40, blue: 0.95))

                Spacer()

                Text("\(completedCount)/\(totalMissionsCount)")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? Color(red: 0.78, green: 0.82, blue: 0.99) : Color(red: 0.28, green: 0.33, blue: 0.41))
            }

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
    }

    // MARK: - 4. Missions Cards List
    private var missionsCardsList: some View {
        LazyVStack(spacing: 12) {
            ForEach(Array(missionsList.enumerated()), id: \.element.id) { index, mission in
                missionCardView(mission: mission, index: index)
            }
        }
    }

    private func missionCardView(mission: Mission, index: Int) -> some View {
        let isDark = viewModel.themeMode == .dark
        let isCompleted = viewModel.completedMissionIds.contains(mission.id)
        let isUnlocked = currentTrack.map { viewModel.isMissionUnlocked(track: $0, missionIndex: index) } ?? (index == 0)

        return Button(action: {
            triggerHaptic()
            if isUnlocked {
                viewModel.startMission(trackIndex: viewModel.selectedTrackIndex, missionIndex: index)
            } else {
                lockedAlertMissionTitle = mission.title
            }
        }) {
            HStack(spacing: 14) {
                // Title on left in Monospaced font
                Text(mission.title)
                    .font(.system(size: 15, weight: .bold, design: .monospaced))
                    .foregroundColor(
                        isUnlocked
                            ? (isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22))
                            : (isDark ? Color.white.opacity(0.45) : Color.black.opacity(0.35))
                    )
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)

                Spacer()

                // State Indicator on Right
                if isCompleted {
                    // Completed Checkmark
                    ZStack {
                        Circle()
                            .fill(Color(red: 0.0, green: 0.88, blue: 0.54).opacity(0.18))
                            .frame(width: 32, height: 32)
                            .overlay(
                                Circle().stroke(Color(red: 0.0, green: 0.88, blue: 0.54), lineWidth: 1.5)
                            )

                        Text("✓")
                            .font(.system(size: 15, weight: .black))
                            .foregroundColor(Color(red: 0.0, green: 0.88, blue: 0.54))
                    }
                } else if !isUnlocked {
                    // Locked Badge
                    ZStack {
                        Circle()
                            .fill(isDark ? Color.white.opacity(0.08) : Color.black.opacity(0.05))
                            .frame(width: 32, height: 32)
                            .overlay(
                                Circle().stroke(isDark ? Color.white.opacity(0.14) : Color.black.opacity(0.08), lineWidth: 1)
                            )

                        Text("🔒")
                            .font(.system(size: 12))
                    }
                } else {
                    // Active / Play Badge
                    ZStack {
                        Circle()
                            .fill(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.20))
                            .frame(width: 32, height: 32)
                            .overlay(
                                Circle().stroke(Color(red: 0.62, green: 0.52, blue: 1.0), lineWidth: 1.5)
                            )

                        Text("▶")
                            .font(.system(size: 11, weight: .black))
                            .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .liquidGlass(
                cornerRadius: 18,
                isDark: isDark,
                isSelected: false,
                displacementScale: 28
            )
        }
        .buttonStyle(.plain)
    }

    // MARK: - 5. Select Path Modal Bottom Sheet
    private var selectPathBottomSheet: some View {
        let isDark = viewModel.themeMode == .dark

        return VStack(spacing: 0) {
            // Drag Handle
            Capsule()
                .fill(isDark ? Color.white.opacity(0.25) : Color.black.opacity(0.20))
                .frame(width: 40, height: 5)
                .padding(.top, 12)
                .padding(.bottom, 14)

            // Header Row
            HStack {
                Button(action: {
                    triggerHaptic()
                    showSelectPathSheet = false
                }) {
                    Text("✕")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.28, green: 0.33, blue: 0.41))
                        .frame(width: 44, height: 44)
                }
                .buttonStyle(.plain)

                Spacer()

                Text("Select Path")
                    .font(.system(size: 17, weight: .bold, design: .monospaced))
                    .foregroundColor(isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22))

                Spacer()

                Color.clear.frame(width: 44, height: 44)
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 8)

            // Paths List
            ScrollView(showsIndicators: false) {
                LazyVStack(spacing: 14) {
                    ForEach(Array((viewModel.dataset?.tracks ?? []).enumerated()), id: \.element.id) { index, track in
                        Button(action: {
                            triggerHaptic()
                            viewModel.selectTrack(index: index)
                            showSelectPathSheet = false
                        }) {
                            HStack(spacing: 14) {
                                TrackIconView(trackId: track.id, size: 20, badgeSize: 34, showBadge: true)

                                VStack(alignment: .leading, spacing: 4) {
                                    Text(track.name)
                                        .font(.system(size: 15, weight: .bold, design: .monospaced))
                                        .foregroundColor(isDark ? .white : Color(red: 0.08, green: 0.10, blue: 0.22))
                                        .lineLimit(1)

                                    Text("\(track.missionsCount) Missões")
                                        .font(.system(size: 12, weight: .semibold, design: .monospaced))
                                        .foregroundColor(isDark ? Color(red: 0.65, green: 0.71, blue: 0.99) : Color(red: 0.39, green: 0.40, blue: 0.95))
                                }

                                Spacer()

                                if viewModel.selectedTrackIndex == index {
                                    Text("✓")
                                        .font(.system(size: 16, weight: .black))
                                        .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
                                }
                            }
                            .padding(14)
                            .liquidGlass(
                                cornerRadius: 18,
                                isDark: isDark,
                                isSelected: viewModel.selectedTrackIndex == index,
                                selectedColor: Color(red: 0.62, green: 0.52, blue: 1.0)
                            )
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 24)
            }
        }
        .background(
            Rectangle()
                .fill(isDark ? Color(red: 0.08, green: 0.10, blue: 0.18) : Color(red: 0.95, green: 0.96, blue: 0.98))
                .ignoresSafeArea()
        )
        .presentationDetents([.medium, .large])
    }

    private func triggerHaptic() {
        #if canImport(UIKit)
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
        #endif
    }
}
