import Foundation
import Combine
#if canImport(ActivityKit)
import ActivityKit
#endif

/// DevOpsLiveActivityManager - Lifecycle Manager for Live Activities & Dynamic Island
/// Based on Apple ActivityKit & reference implementation: 1998code/iOS16-Live-Activities
@MainActor
public class DevOpsLiveActivityManager: ObservableObject {
    public static let shared = DevOpsLiveActivityManager()

    #if canImport(ActivityKit)
    @Published public private(set) var activeActivity: Any? = nil
    #endif

    @Published public private(set) var isActivityRunning: Bool = false
    @Published public private(set) var lastContentState: DevOpsLabActivityAttributes.ContentState? = nil
    @Published public private(set) var lastAttributes: DevOpsLabActivityAttributes? = nil

    private init() {}

    /// Checks if the device and user authorization permit Live Activities
    public var areActivitiesEnabled: Bool {
        #if canImport(ActivityKit)
        if #available(iOS 16.1, *) {
            return ActivityAuthorizationInfo().areActivitiesEnabled
        }
        #endif
        return false
    }

    /// Starts a Live Activity for the specified Track and Mission
    public func startLabActivity(
        trackId: String,
        trackName: String,
        trackIcon: String,
        missionId: String,
        missionIndex: Int,
        missionTitle: String,
        objective: String,
        xpReward: Int,
        completedCount: Int,
        totalMissions: Int,
        operatorHandle: String = "@devops"
    ) {
        let attributes = DevOpsLabActivityAttributes(
            trackId: trackId,
            trackName: trackName,
            trackIcon: trackIcon,
            operatorHandle: operatorHandle
        )

        let initialState = DevOpsLabActivityAttributes.ContentState(
            missionId: missionId,
            missionIndex: missionIndex,
            missionTitle: missionTitle,
            objective: objective,
            xpReward: xpReward,
            status: "ONLINE",
            secondsElapsed: 0,
            speedScoreMultiplier: 1.5,
            completedCount: completedCount,
            totalMissions: totalMissions
        )

        self.lastAttributes = attributes
        self.lastContentState = initialState
        self.isActivityRunning = true

        #if canImport(ActivityKit)
        if #available(iOS 16.1, *) {
            guard areActivitiesEnabled else {
                print("DevOpsHero: Live Activities are not enabled or supported on this device.")
                return
            }

            // End any previously running activity before starting a fresh one
            endLabActivity()

            do {
                let activity = try Activity<DevOpsLabActivityAttributes>.request(
                    attributes: attributes,
                    content: .init(state: initialState, staleDate: nil),
                    pushType: nil
                )
                self.activeActivity = activity
                print("DevOpsHero: Live Activity started successfully. ID: \(activity.id)")
            } catch {
                print("DevOpsHero: Error requesting Live Activity: \(error.localizedDescription)")
            }
        }
        #endif
    }

    /// Updates the dynamic content state of the active Live Activity (e.g. elapsed time, XP, status)
    public func updateLabActivity(
        secondsElapsed: Int? = nil,
        status: String? = nil,
        xpReward: Int? = nil,
        speedScoreMultiplier: Double? = nil,
        missionId: String? = nil,
        missionIndex: Int? = nil,
        missionTitle: String? = nil,
        objective: String? = nil,
        completedCount: Int? = nil,
        totalMissions: Int? = nil
    ) {
        guard isActivityRunning, var currentState = lastContentState else { return }

        if let seconds = secondsElapsed { currentState.secondsElapsed = seconds }
        if let st = status { currentState.status = st }
        if let xp = xpReward { currentState.xpReward = xp }
        if let mult = speedScoreMultiplier { currentState.speedScoreMultiplier = mult }
        if let mId = missionId { currentState.missionId = mId }
        if let mIdx = missionIndex { currentState.missionIndex = mIdx }
        if let mTitle = missionTitle { currentState.missionTitle = mTitle }
        if let obj = objective { currentState.objective = obj }
        if let comp = completedCount { currentState.completedCount = comp }
        if let tot = totalMissions { currentState.totalMissions = tot }

        self.lastContentState = currentState

        #if canImport(ActivityKit)
        if #available(iOS 16.1, *), let activity = self.activeActivity as? Activity<DevOpsLabActivityAttributes> {
            Task {
                await activity.update(.init(state: currentState, staleDate: nil))
            }
        }
        #endif
    }

    /// Ends the active Live Activity immediately or with a dismissal policy
    public func endLabActivity(dismissalPolicy: String = "immediate") {
        self.isActivityRunning = false

        #if canImport(ActivityKit)
        if #available(iOS 16.1, *), let activity = self.activeActivity as? Activity<DevOpsLabActivityAttributes> {
            Task {
                if dismissalPolicy == "default" {
                    await activity.end(nil, dismissalPolicy: .default)
                } else {
                    await activity.end(nil, dismissalPolicy: .immediate)
                }
            }
            self.activeActivity = nil
            print("DevOpsHero: Live Activity ended.")
        }
        #endif
    }
}

