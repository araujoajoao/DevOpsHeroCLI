import SwiftUI
#if canImport(WidgetKit)
import WidgetKit
#endif
#if canImport(ActivityKit)
import ActivityKit
#endif

/// DevOpsDynamicIslandWidgetView - Live Activities & Dynamic Island Presentation Views
/// Built with Apple ActivityKit & WidgetKit principles (Reference: 1998code/iOS16-Live-Activities)
/// Strict Apple HIG & DevOpsHero Rules:
/// - Slate-Navy Palettes (#131627 / #1E243E / #272E4F)
/// - Continuous Squircle Curvature (.continuous)
/// - SF Mono / Menlo Tech Typography
/// - Lilac #9E85FF & Emerald Neon #00DF89 Semantics

// MARK: - 1. Dynamic Island: Expanded Leading View
public struct DevOpsDynamicIslandExpandedLeadingView: View {
    public var trackId: String
    public var trackName: String

    public init(trackId: String, trackName: String) {
        self.trackId = trackId
        self.trackName = trackName
    }

    public var body: some View {
        HStack(spacing: 8) {
            // Official Single Tech Badge Container (34x34pt squircle)
            ZStack {
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(Color(red: 0.12, green: 0.14, blue: 0.24)) // #1E243E
                    .frame(width: 32, height: 32)
                    .overlay(
                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .stroke(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.35), lineWidth: 1)
                    )

                TrackIconView(trackId: trackId, size: 18)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(trackName)
                    .font(.system(size: 13, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
                    .lineLimit(1)

                Text("DevOpsHero Lab")
                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                    .foregroundColor(Color(red: 0.65, green: 0.71, blue: 0.99)) // #A5B4FC
            }
        }
    }
}

// MARK: - 2. Dynamic Island: Expanded Trailing View
public struct DevOpsDynamicIslandExpandedTrailingView: View {
    public var xpReward: Int
    public var status: String

    public init(xpReward: Int, status: String) {
        self.xpReward = xpReward
        self.status = status
    }

    public var body: some View {
        VStack(alignment: .trailing, spacing: 3) {
            // XP Pill Badge
            HStack(spacing: 3) {
                Text("⭐")
                    .font(.system(size: 10))
                Text("+\(xpReward) XP")
                    .font(.system(size: 11, weight: .heavy, design: .monospaced))
                    .foregroundColor(Color(red: 0.98, green: 0.75, blue: 0.14)) // #FBBF24
            }
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .background(Color(red: 0.98, green: 0.75, blue: 0.14).opacity(0.14))
            .cornerRadius(6)

            // Status Indicator
            HStack(spacing: 4) {
                Circle()
                    .fill(status == "ONLINE" || status == "RUNNING" ? Color(red: 0.0, green: 0.87, blue: 0.54) : Color(red: 0.98, green: 0.75, blue: 0.14))
                    .frame(width: 6, height: 6)

                Text(status)
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundColor(status == "ONLINE" || status == "RUNNING" ? Color(red: 0.0, green: 0.87, blue: 0.54) : Color(red: 0.98, green: 0.75, blue: 0.14))
            }
        }
    }
}

// MARK: - 3. Dynamic Island: Expanded Center / Command View
public struct DevOpsDynamicIslandExpandedCenterView: View {
    public var objective: String
    public var trackId: String

    public init(objective: String, trackId: String) {
        self.objective = objective
        self.trackId = trackId
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            // Numbered terminal comment line
            HStack(spacing: 4) {
                Text("1")
                    .font(.system(size: 11, weight: .medium, design: .monospaced))
                    .foregroundColor(Color.gray.opacity(0.7))
                Text("# \(objective)")
                    .font(.system(size: 11, weight: .semibold, design: .monospaced))
                    .foregroundColor(Color(red: 0.65, green: 0.71, blue: 0.99)) // #A5B4FC
                    .lineLimit(1)
            }

            // Command prompt line
            HStack(spacing: 4) {
                Text("2")
                    .font(.system(size: 11, weight: .medium, design: .monospaced))
                    .foregroundColor(Color.gray.opacity(0.7))
                Text("➜")
                    .font(.system(size: 11, weight: .bold))
                    .foregroundColor(Color(red: 0.0, green: 0.87, blue: 0.54)) // #00DF89
                Text("~ \(trackId) $")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }
        }
        .padding(6)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(red: 0.07, green: 0.09, blue: 0.15)) // #131627
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(red: 0.15, green: 0.18, blue: 0.31), lineWidth: 1) // #272E4F
        )
    }
}

// MARK: - 4. Dynamic Island: Expanded Bottom / Progress View
public struct DevOpsDynamicIslandExpandedBottomView: View {
    public var completedCount: Int
    public var totalMissions: Int
    public var speedScoreMultiplier: Double
    public var secondsElapsed: Int

    public init(
        completedCount: Int,
        totalMissions: Int,
        speedScoreMultiplier: Double,
        secondsElapsed: Int
    ) {
        self.completedCount = completedCount
        self.totalMissions = max(totalMissions, 1)
        self.speedScoreMultiplier = speedScoreMultiplier
        self.secondsElapsed = secondsElapsed
    }

    public var body: some View {
        VStack(spacing: 4) {
            HStack {
                Text("SECTION \(completedCount)/\(totalMissions)")
                    .font(.system(size: 10, weight: .heavy, design: .monospaced))
                    .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0)) // #9E85FF

                Spacer()

                HStack(spacing: 3) {
                    Text("⚡")
                        .font(.system(size: 9))
                    Text(String(format: "%.1fx XP Speed Boost", speedScoreMultiplier))
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(red: 0.0, green: 0.87, blue: 0.54)) // #00DF89
                }

                Text("⏱️ \(secondsElapsed)s")
                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                    .foregroundColor(Color(red: 0.65, green: 0.71, blue: 0.99))
            }

            // Lilac Progress Bar
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(Color.white.opacity(0.12))
                        .frame(height: 4)

                    Capsule()
                        .fill(Color(red: 0.62, green: 0.52, blue: 1.0)) // #9E85FF
                        .frame(width: geo.size.width * CGFloat(Double(completedCount) / Double(totalMissions)), height: 4)
                }
            }
            .frame(height: 4)
        }
    }
}

// MARK: - 5. Lock Screen / Banner Presentation View (Apple Liquid Glass)
public struct DevOpsLockScreenLiveActivityView: View {
    public var trackId: String
    public var trackName: String
    public var missionTitle: String
    public var objective: String
    public var xpReward: Int
    public var status: String
    public var completedCount: Int
    public var totalMissions: Int
    public var secondsElapsed: Int
    public var speedScoreMultiplier: Double

    public init(
        trackId: String,
        trackName: String,
        missionTitle: String,
        objective: String,
        xpReward: Int,
        status: String,
        completedCount: Int,
        totalMissions: Int,
        secondsElapsed: Int,
        speedScoreMultiplier: Double
    ) {
        self.trackId = trackId
        self.trackName = trackName
        self.missionTitle = missionTitle
        self.objective = objective
        self.xpReward = xpReward
        self.status = status
        self.completedCount = completedCount
        self.totalMissions = max(totalMissions, 1)
        self.secondsElapsed = secondsElapsed
        self.speedScoreMultiplier = speedScoreMultiplier
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            // Row 1: Header (Badge + Track Name + Status + XP)
            HStack(spacing: 8) {
                // Official Single Badge Container (34x34pt squircle)
                ZStack {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                        .fill(Color(red: 0.12, green: 0.14, blue: 0.24)) // #1E243E
                        .frame(width: 34, height: 34)
                        .overlay(
                            RoundedRectangle(cornerRadius: 10, style: .continuous)
                                .stroke(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.40), lineWidth: 1.2)
                        )

                    TrackIconView(trackId: trackId, size: 20)
                }

                VStack(alignment: .leading, spacing: 2) {
                    Text(trackName)
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                        .lineLimit(1)

                    Text(missionTitle)
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundColor(Color(red: 0.65, green: 0.71, blue: 0.99))
                        .lineLimit(1)
                }

                Spacer()

                // XP Badge
                HStack(spacing: 3) {
                    Text("⭐")
                        .font(.system(size: 11))
                    Text("+\(xpReward) XP")
                        .font(.system(size: 12, weight: .heavy, design: .monospaced))
                        .foregroundColor(Color(red: 0.98, green: 0.75, blue: 0.14))
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color(red: 0.98, green: 0.75, blue: 0.14).opacity(0.14))
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color(red: 0.98, green: 0.75, blue: 0.14).opacity(0.35), lineWidth: 1)
                )
            }

            // Row 2: Code Editor Window Preview
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text("1")
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundColor(Color.gray.opacity(0.6))
                    Text("# \(objective)")
                        .font(.system(size: 12, weight: .semibold, design: .monospaced))
                        .foregroundColor(Color(red: 0.65, green: 0.71, blue: 0.99))
                        .lineLimit(1)
                }

                HStack(spacing: 6) {
                    Text("2")
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundColor(Color.gray.opacity(0.6))
                    Text("➜")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundColor(Color(red: 0.0, green: 0.87, blue: 0.54))
                    Text("~ \(trackId) $")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                    Text("online")
                        .font(.system(size: 10, weight: .semibold, design: .monospaced))
                        .foregroundColor(Color(red: 0.0, green: 0.87, blue: 0.54))
                        .padding(.horizontal, 5)
                        .padding(.vertical, 2)
                        .background(Color(red: 0.0, green: 0.87, blue: 0.54).opacity(0.12))
                        .cornerRadius(4)
                }
            }
            .padding(8)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color(red: 0.07, green: 0.09, blue: 0.15)) // #131627
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(red: 0.15, green: 0.18, blue: 0.31), lineWidth: 1) // #272E4F
            )

            // Row 3: Progress & Speed Score
            VStack(spacing: 4) {
                HStack {
                    Text("SECTION")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(red: 0.65, green: 0.71, blue: 0.99))

                    Text("\(completedCount)/\(totalMissions)")
                        .font(.system(size: 11, weight: .heavy, design: .monospaced))
                        .foregroundColor(Color(red: 0.62, green: 0.52, blue: 1.0)) // #9E85FF

                    Spacer()

                    HStack(spacing: 3) {
                        Text("⚡")
                            .font(.system(size: 10))
                        Text(String(format: "%.1fx XP", speedScoreMultiplier))
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(Color(red: 0.0, green: 0.87, blue: 0.54))
                    }

                    Text("⏱️ \(secondsElapsed)s")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundColor(.white)
                }

                // Lilac Progress Bar
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule()
                            .fill(Color.white.opacity(0.12))
                            .frame(height: 5)

                        Capsule()
                            .fill(Color(red: 0.62, green: 0.52, blue: 1.0)) // #9E85FF
                            .frame(width: geo.size.width * CGFloat(Double(completedCount) / Double(totalMissions)), height: 5)
                    }
                }
                .frame(height: 5)
            }
        }
        .padding(14)
        .background(
            ZStack {
                Color(red: 0.07, green: 0.09, blue: 0.15) // #131627
                LinearGradient(
                    colors: [Color.white.opacity(0.08), Color.clear],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            }
        )
        .cornerRadius(18)
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.35), lineWidth: 1.5)
        )
    }
}

// MARK: - 6. Dynamic Island In-App Simulator & Preview Banner
public struct DevOpsDynamicIslandPreviewBanner: View {
    @ObservedObject var manager = DevOpsLiveActivityManager.shared
    @State private var isExpanded: Bool = false

    public init() {}

    public var body: some View {
        if manager.isActivityRunning,
           let attrs = manager.lastAttributes,
           let state = manager.lastContentState {
            VStack(spacing: 0) {
                // Notch Pill Container
                Button(action: {
                    withAnimation(.spring(response: 0.38, dampingFraction: 0.75)) {
                        isExpanded.toggle()
                    }
                }) {
                    if isExpanded {
                        // Expanded Dynamic Island View
                        VStack(spacing: 10) {
                            HStack {
                                DevOpsDynamicIslandExpandedLeadingView(
                                    trackId: attrs.trackId,
                                    trackName: attrs.trackName
                                )
                                Spacer()
                                DevOpsDynamicIslandExpandedTrailingView(
                                    xpReward: state.xpReward,
                                    status: state.status
                                )
                            }

                            DevOpsDynamicIslandExpandedCenterView(
                                objective: state.objective,
                                trackId: attrs.trackId
                            )

                            DevOpsDynamicIslandExpandedBottomView(
                                completedCount: state.completedCount,
                                totalMissions: state.totalMissions,
                                speedScoreMultiplier: state.speedScoreMultiplier,
                                secondsElapsed: state.secondsElapsed
                            )
                        }
                        .padding(14)
                        .background(Color.black)
                        .cornerRadius(28)
                        .overlay(
                            RoundedRectangle(cornerRadius: 28, style: .continuous)
                                .stroke(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.4), lineWidth: 1.2)
                        )
                    } else {
                        // Compact Dynamic Island Pill
                        HStack(spacing: 8) {
                            // Compact Leading
                            HStack(spacing: 5) {
                                TrackIconView(trackId: attrs.trackId, size: 14)
                                Text(attrs.trackName)
                                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                                    .foregroundColor(.white)
                                    .lineLimit(1)
                            }

                            Spacer()

                            // Compact Trailing
                            HStack(spacing: 4) {
                                Text("⚡")
                                    .font(.system(size: 9))
                                Text("+\(state.xpReward) XP")
                                    .font(.system(size: 10, weight: .heavy, design: .monospaced))
                                    .foregroundColor(Color(red: 0.98, green: 0.75, blue: 0.14))

                                Text("⏱️ \(state.secondsElapsed)s")
                                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                                    .foregroundColor(Color(red: 0.65, green: 0.71, blue: 0.99))
                            }
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 8)
                        .background(Color.black)
                        .cornerRadius(20)
                        .overlay(
                            RoundedRectangle(cornerRadius: 20, style: .continuous)
                                .stroke(Color(red: 0.62, green: 0.52, blue: 1.0).opacity(0.3), lineWidth: 1)
                        )
                    }
                }
                .buttonStyle(.plain)
                .padding(.horizontal, 16)
                .padding(.vertical, 4)
            }
        }
    }
}

