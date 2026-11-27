import SwiftUI
#if canImport(WidgetKit) && canImport(ActivityKit)
import WidgetKit
import ActivityKit

/// DevOpsLabActivityWidget - Apple ActivityKit Widget Configuration
/// Compliant with iOS 16.1+ Live Activities & Dynamic Island
/// Reference implementation: 1998code/iOS16-Live-Activities
@available(iOS 16.1, *)
public struct DevOpsLabActivityWidget: Widget {
    public init() {}

    public var body: some WidgetConfiguration {
        ActivityConfiguration(for: DevOpsLabActivityAttributes.self) { context in
            // Lock Screen / Notification Center Presentation
            DevOpsLockScreenLiveActivityView(
                trackId: context.attributes.trackId,
                trackName: context.attributes.trackName,
                missionTitle: context.state.missionTitle,
                objective: context.state.objective,
                xpReward: context.state.xpReward,
                status: context.state.status,
                completedCount: context.state.completedCount,
                totalMissions: context.state.totalMissions,
                secondsElapsed: context.state.secondsElapsed,
                speedScoreMultiplier: context.state.speedScoreMultiplier
            )
            .activityBackgroundTint(Color(red: 0.07, green: 0.09, blue: 0.15))
            .activitySystemActionForegroundColor(Color(red: 0.62, green: 0.52, blue: 1.0))
        } dynamicIsland: { context in
            DynamicIsland {
                // Expanded Leading
                DynamicIslandExpandedRegion(.leading) {
                    DevOpsDynamicIslandExpandedLeadingView(
                        trackId: context.attributes.trackId,
                        trackName: context.attributes.trackName
                    )
                }

                // Expanded Trailing
                DynamicIslandExpandedRegion(.trailing) {
                    DevOpsDynamicIslandExpandedTrailingView(
                        xpReward: context.state.xpReward,
                        status: context.state.status
                    )
                }

                // Expanded Center
                DynamicIslandExpandedRegion(.center) {
                    DevOpsDynamicIslandExpandedCenterView(
                        objective: context.state.objective,
                        trackId: context.attributes.trackId
                    )
                }

                // Expanded Bottom
                DynamicIslandExpandedRegion(.bottom) {
                    DevOpsDynamicIslandExpandedBottomView(
                        completedCount: context.state.completedCount,
                        totalMissions: context.state.totalMissions,
                        speedScoreMultiplier: context.state.speedScoreMultiplier,
                        secondsElapsed: context.state.secondsElapsed
                    )
                }
            } compactLeading: {
                HStack(spacing: 4) {
                    TrackIconView(trackId: context.attributes.trackId, size: 14)
                }
            } compactTrailing: {
                HStack(spacing: 3) {
                    Text("+\(context.state.xpReward)")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(red: 0.98, green: 0.75, blue: 0.14))
                }
            } minimal: {
                TrackIconView(trackId: context.attributes.trackId, size: 13)
            }
        }
    }
}
#endif

