import Foundation
#if canImport(ActivityKit)
import ActivityKit
#endif

/// DevOpsLabActivityAttributes - ActivityKit attributes for DevOpsHero Interactive Terminal Labs
/// Compliant with iOS 16.1+ Live Activities & Dynamic Island (ActivityKit & WidgetKit)
/// Reference: 1998code/iOS16-Live-Activities
public struct DevOpsLabActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        public var missionId: String
        public var missionIndex: Int
        public var missionTitle: String
        public var objective: String
        public var xpReward: Int
        public var status: String // "ONLINE", "VERIFYING", "COMPLETED", "PAUSED"
        public var secondsElapsed: Int
        public var speedScoreMultiplier: Double
        public var completedCount: Int
        public var totalMissions: Int

        public init(
            missionId: String,
            missionIndex: Int,
            missionTitle: String,
            objective: String,
            xpReward: Int,
            status: String = "ONLINE",
            secondsElapsed: Int = 0,
            speedScoreMultiplier: Double = 1.0,
            completedCount: Int = 0,
            totalMissions: Int = 10
        ) {
            self.missionId = missionId
            self.missionIndex = missionIndex
            self.missionTitle = missionTitle
            self.objective = objective
            self.xpReward = xpReward
            self.status = status
            self.secondsElapsed = secondsElapsed
            self.speedScoreMultiplier = speedScoreMultiplier
            self.completedCount = completedCount
            self.totalMissions = totalMissions
        }
    }

    public var trackId: String
    public var trackName: String
    public var trackIcon: String
    public var operatorHandle: String

    public init(
        trackId: String,
        trackName: String,
        trackIcon: String,
        operatorHandle: String = "@devops"
    ) {
        self.trackId = trackId
        self.trackName = trackName
        self.trackIcon = trackIcon
        self.operatorHandle = operatorHandle
    }
}

