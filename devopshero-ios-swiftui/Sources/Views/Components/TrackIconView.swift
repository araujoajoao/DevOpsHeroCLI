import SwiftUI

public struct TrackIconView: View {
    public let trackId: String
    public var size: CGFloat = 20
    public var badgeSize: CGFloat = 34
    public var showBadge: Bool = true

    public init(trackId: String, size: CGFloat = 20, badgeSize: CGFloat = 34, showBadge: Bool = true) {
        self.trackId = trackId
        self.size = size
        self.badgeSize = badgeSize
        self.showBadge = showBadge
    }

    private var trackMeta: (assetName: String, sfFallback: String, badgeColor: Color, iconColor: Color) {
        let lower = trackId.lowercased()
        if lower.contains("linux") {
            return ("icon-linux", "terminal.fill", Color(red: 0.98, green: 0.78, blue: 0.14), Color.black)
        } else if lower.contains("sysadmin") || lower.contains("bash") || lower.contains("shell") {
            return ("icon-sysadmin", "command", Color(red: 0.16, green: 0.19, blue: 0.22), Color(red: 0.31, green: 0.67, blue: 0.15))
        } else if lower.contains("git") {
            return ("icon-git", "arrow.triangle.branch", Color(red: 0.94, green: 0.31, blue: 0.20), Color.white)
        } else if lower.contains("docker") || lower.contains("container") {
            return ("icon-docker", "shippingbox.fill", Color(red: 0.14, green: 0.59, blue: 0.93), Color.white)
        } else if lower.contains("aws") || lower.contains("cloud") {
            return ("icon-aws", "cloud.fill", Color(red: 0.14, green: 0.18, blue: 0.24), Color(red: 1.0, green: 0.60, blue: 0.0))
        } else if lower.contains("terraform") || lower.contains("iac") {
            return ("icon-terraform", "cube.transparent.fill", Color(red: 0.52, green: 0.31, blue: 0.73), Color.white)
        } else if lower.contains("k8s") || lower.contains("kube") {
            return ("icon-k8s", "helm", Color(red: 0.20, green: 0.42, blue: 0.90), Color.white)
        } else if lower.contains("datadog") || lower.contains("obs") {
            return ("icon-datadog", "chart.xyaxis.line", Color(red: 0.39, green: 0.17, blue: 0.65), Color.white)
        }
        return ("icon-linux", "terminal.fill", Color(red: 0.98, green: 0.78, blue: 0.14), Color.black)
    }

    public var body: some View {
        let meta = trackMeta

        let iconView = Group {
            #if canImport(AppKit) && !targetEnvironment(macCatalyst)
            #if SWIFT_PACKAGE
            if let image = Bundle.module.image(forResource: meta.assetName) {
                Image(nsImage: image)
                    .resizable()
                    .renderingMode(.template)
                    .foregroundColor(meta.iconColor)
                    .aspectRatio(contentMode: .fit)
                    .frame(width: size, height: size)
            } else {
                Image(meta.assetName)
                    .resizable()
                    .renderingMode(.template)
                    .foregroundColor(meta.iconColor)
                    .aspectRatio(contentMode: .fit)
                    .frame(width: size, height: size)
            }
            #else
            Image(meta.assetName)
                .resizable()
                .renderingMode(.template)
                .foregroundColor(meta.iconColor)
                .aspectRatio(contentMode: .fit)
                .frame(width: size, height: size)
            #endif
            #else
            Image(meta.assetName)
                .resizable()
                .renderingMode(.template)
                .foregroundColor(meta.iconColor)
                .aspectRatio(contentMode: .fit)
                .frame(width: size, height: size)
            #endif
        }

        if showBadge {
            ZStack {
                RoundedRectangle(cornerRadius: badgeSize * 0.26, style: .continuous)
                    .fill(meta.badgeColor)
                    .frame(width: badgeSize, height: badgeSize)
                    .shadow(color: Color.black.opacity(0.25), radius: 3, x: 0, y: 2)

                iconView
            }
            .frame(width: badgeSize, height: badgeSize)
        } else {
            iconView
        }
    }
}

