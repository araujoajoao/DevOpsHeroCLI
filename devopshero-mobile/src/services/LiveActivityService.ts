/**
 * LiveActivityService - Service for Apple Live Activities & Dynamic Island (ActivityKit)
 * Parity with devopshero-ios-swiftui and reference implementation 1998code/iOS16-Live-Activities
 */

export interface DevOpsLabActivityContentState {
  missionId: string;
  missionIndex: number;
  missionTitle: string;
  objective: string;
  xpReward: number;
  status: 'ONLINE' | 'VERIFYING' | 'COMPLETED' | 'PAUSED' | 'TRY AGAIN';
  secondsElapsed: number;
  speedScoreMultiplier: number;
  completedCount: number;
  totalMissions: number;
}

export interface DevOpsLabActivityAttributes {
  trackId: string;
  trackName: string;
  trackIcon: string;
  operatorHandle: string;
}

export interface LiveActivitySnapshot {
  isActive: boolean;
  attributes: DevOpsLabActivityAttributes | null;
  state: DevOpsLabActivityContentState | null;
}

type LiveActivityListener = (snapshot: LiveActivitySnapshot) => void;

class LiveActivityServiceImpl {
  private currentSnapshot: LiveActivitySnapshot = {
    isActive: false,
    attributes: null,
    state: null,
  };

  private listeners: Set<LiveActivityListener> = new Set();

  public subscribe(listener: LiveActivityListener): () => void {
    this.listeners.add(listener);
    listener(this.currentSnapshot);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify() {
    this.listeners.forEach((fn) => fn(this.currentSnapshot));
  }

  public getSnapshot(): LiveActivitySnapshot {
    return this.currentSnapshot;
  }

  /**
   * Starts a Live Activity for the current interactive lab session
   */
  public startLabActivity(
    attributes: DevOpsLabActivityAttributes,
    initialState: DevOpsLabActivityContentState
  ) {
    this.currentSnapshot = {
      isActive: true,
      attributes,
      state: initialState,
    };
    this.notify();
    // Native ActivityKit bridge emission when running native build
  }

  /**
   * Updates dynamic attributes in real-time (e.g. elapsed seconds, speed score, XP)
   */
  public updateLabActivity(partialState: Partial<DevOpsLabActivityContentState>) {
    if (!this.currentSnapshot.isActive || !this.currentSnapshot.state) return;

    this.currentSnapshot = {
      ...this.currentSnapshot,
      state: {
        ...this.currentSnapshot.state,
        ...partialState,
      },
    };
    this.notify();
  }

  /**
   * Ends the active Live Activity session
   */
  public endLabActivity() {
    this.currentSnapshot = {
      isActive: false,
      attributes: null,
      state: null,
    };
    this.notify();
  }
}

export const LiveActivityService = new LiveActivityServiceImpl();

