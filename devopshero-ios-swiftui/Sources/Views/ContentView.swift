import SwiftUI

/// ContentView - Root Navigation & Atmospheric Liquid Glass Container
/// 100% Parity with devopshero-mobile/App.tsx
/// Apple HIG & iPhone 17 Pro Max Framing:
/// - Full Atmospheric Liquid Glass Aurora Backing Engine (AmbientGlassBackgroundView)
/// - Bottom Safe Area Inset for Floating Dock (Clear of Physical Home Indicator)
/// - Adaptive Screen Transitions and Modal Overlays
public struct ContentView: View {
    @StateObject private var viewModel = DevOpsHeroViewModel()

    public init() {}

    public var body: some View {
        ZStack {
            // 1. Apple Liquid Glass Atmospheric Backing Engine (iOS 27 Physics)
            AmbientGlassBackgroundView(themeMode: viewModel.themeMode)

            // 2. Active Screen Content Layer
            if !viewModel.isLoggedIn {
                AuthView(viewModel: viewModel)
                    .transition(.opacity.combined(with: .scale(scale: 0.98)))
            } else {
                Group {
                    switch viewModel.activeTab {
                    case .home:
                        HomeView(viewModel: viewModel)
                    case .tracks:
                        TracksView(viewModel: viewModel)
                    case .practice:
                        PracticeView(viewModel: viewModel)
                    case .profile:
                        ProfileView(viewModel: viewModel)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .animation(.spring(response: 0.38, dampingFraction: 0.72), value: viewModel.activeTab)
                .transition(.opacity.combined(with: .scale(scale: 0.975)))
                .safeAreaInset(edge: .bottom) {
                    // Floating Dock Navigation (Hidden during practice to maximize terminal space)
                    // Floats comfortably above the physical iPhone Home Indicator
                    if viewModel.activeTab != .practice {
                        FloatingDockView(viewModel: viewModel)
                            .padding(.bottom, 6)
                            .transition(.move(edge: .bottom).combined(with: .opacity))
                    }
                }

                // 3. App Update Modal Overlay
                if viewModel.showUpdateModal {
                    AppUpdateModalView(viewModel: viewModel)
                        .transition(.opacity)
                        .zIndex(100)
                }
            }
        }
        .preferredColorScheme(viewModel.themeMode == .dark ? .dark : .light)
    }
}
