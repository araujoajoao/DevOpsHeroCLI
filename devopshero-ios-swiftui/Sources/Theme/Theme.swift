import SwiftUI

public enum ThemeMode: String, CaseIterable, Identifiable {
    case dark
    case light

    public var id: String { rawValue }
}

public struct ThemeColors {
    public static let neonGreen = Color(red: 0.0, green: 1.0, blue: 0.529) // #00ff87
    public static let mintGreen = Color(red: 0.0, green: 0.875, blue: 0.537) // #00DF89
    public static let azureCyan = Color(red: 0.0, green: 0.949, blue: 0.996) // #00f2fe
    public static let amber = Color(red: 0.984, green: 0.749, blue: 0.141) // #fbbf24
    public static let rose = Color(red: 0.984, green: 0.443, blue: 0.522) // #fb7185
    public static let coral = Color(red: 0.984, green: 0.443, blue: 0.522) // alias for rose
    public static let indigo = Color(red: 0.506, green: 0.549, blue: 0.973) // #818cf8
    public static let purple = Color(red: 0.753, green: 0.518, blue: 0.988) // #c084fc

    public static let lilac = Color(red: 0.620, green: 0.522, blue: 1.0) // #9E85FF

    public static func background(for mode: ThemeMode) -> Color {
        mode == .dark ? Color(red: 0.075, green: 0.086, blue: 0.153) : Color(red: 0.941, green: 0.953, blue: 0.976) // #131627 / #F0F3F9
    }

    public static func cardBackground(for mode: ThemeMode) -> Color {
        mode == .dark ? Color(red: 0.153, green: 0.180, blue: 0.310) : Color(red: 0.929, green: 0.941, blue: 0.969) // #272E4F / #EDF0F7
    }

    public static func cardHeader(for mode: ThemeMode) -> Color {
        mode == .dark ? Color(red: 0.094, green: 0.114, blue: 0.200) : Color(red: 0.941, green: 0.957, blue: 0.976)
    }

    public static func cardSubtle(for mode: ThemeMode) -> Color {
        mode == .dark ? Color(red: 0.110, green: 0.133, blue: 0.235) : Color(red: 0.925, green: 0.945, blue: 0.969)
    }

    public static func border(for mode: ThemeMode) -> Color {
        mode == .dark ? Color.white.opacity(0.08) : Color.black.opacity(0.06)
    }

    public static func textMain(for mode: ThemeMode) -> Color {
        mode == .dark ? Color(red: 0.969, green: 0.976, blue: 0.988) : Color(red: 0.059, green: 0.090, blue: 0.165)
    }

    public static func textMuted(for mode: ThemeMode) -> Color {
        mode == .dark ? Color(red: 0.580, green: 0.639, blue: 0.722) : Color(red: 0.392, green: 0.455, blue: 0.545)
    }
}

