import Foundation

public struct AppDataset: Codable {
    public let appTitle: String
    public let tagline: String
    public let totalTracks: Int
    public let totalMissions: Int
    public let tracks: [Track]

    enum CodingKeys: String, CodingKey {
        case appTitle = "app_title"
        case tagline
        case totalTracks = "total_tracks"
        case totalMissions = "total_missions"
        case tracks
    }
}

public struct Track: Codable, Identifiable, Hashable {
    public let id: String
    public let name: String
    public let icon: String
    public let description: String
    public let requiredXp: Int?
    public let requiredSeniority: String?
    public let missionsCount: Int
    public let missions: [Mission]

    public init(
        id: String,
        name: String,
        icon: String,
        description: String,
        requiredXp: Int? = nil,
        requiredSeniority: String? = nil,
        missionsCount: Int,
        missions: [Mission]
    ) {
        self.id = id
        self.name = name
        self.icon = icon
        self.description = description
        self.requiredXp = requiredXp
        self.requiredSeniority = requiredSeniority
        self.missionsCount = missionsCount
        self.missions = missions
    }

    enum CodingKeys: String, CodingKey {
        case id, name, icon, description
        case requiredXp = "required_xp"
        case requiredSeniority = "required_seniority"
        case missionsCount = "missions_count"
        case missions
    }
}

public struct Mission: Codable, Identifiable, Hashable {
    public let id: String
    public let trackId: String
    public let trackName: String
    public let trackIcon: String
    public let title: String
    public let difficulty: String
    public let xp: Int
    public let scenario: String
    public let objective: String
    public let tip: String
    public let solution: String
    public let exerciseTypes: ExerciseTypes

    enum CodingKeys: String, CodingKey {
        case id
        case trackId = "track_id"
        case trackName = "track_name"
        case trackIcon = "track_icon"
        case title, difficulty, xp, scenario, objective, tip, solution
        case exerciseTypes = "exercise_types"
    }
}

public struct ExerciseTypes: Codable, Hashable {
    public let wordBank: WordBankExercise
    public let fillInTheBlank: FillInBlankExercise?

    enum CodingKeys: String, CodingKey {
        case wordBank = "word_bank"
        case fillInTheBlank = "fill_in_the_blank"
    }
}

public struct WordBankExercise: Codable, Hashable {
    public let instruction: String
    public let targetTokens: [String]
    public let chips: [String]?

    enum CodingKeys: String, CodingKey {
        case instruction
        case targetTokens = "target_tokens"
        case chips
    }
}

public struct FillInBlankExercise: Codable, Hashable {
    public let instruction: String
    public let sentence: String
    public let correctChoice: String
    public let choices: [String]

    enum CodingKeys: String, CodingKey {
        case instruction, sentence
        case correctChoice = "correct_choice"
        case choices
    }
}

public struct ChipItem: Identifiable, Hashable {
    public let id: String
    public let text: String
    public var isPlaced: Bool

    public init(id: String, text: String, isPlaced: Bool = false) {
        self.id = id
        self.text = text
        self.isPlaced = isPlaced
    }
}

public struct AwardResult: Identifiable {
    public let id = UUID()
    public let xp: Int
    public let baseXP: Int
    public let factor: Double
    public let tierName: String
    public let elapsedSeconds: Double
    public let tipsUsed: Int
    public let streakBonusPct: Int
    public let isNinja: Bool
    public let solutionUsed: Bool

    public init(
        xp: Int,
        baseXP: Int,
        factor: Double,
        tierName: String,
        elapsedSeconds: Double,
        tipsUsed: Int,
        streakBonusPct: Int,
        isNinja: Bool,
        solutionUsed: Bool
    ) {
        self.xp = xp
        self.baseXP = baseXP
        self.factor = factor
        self.tierName = tierName
        self.elapsedSeconds = elapsedSeconds
        self.tipsUsed = tipsUsed
        self.streakBonusPct = streakBonusPct
        self.isNinja = isNinja
        self.solutionUsed = solutionUsed
    }
}

public enum TabType: String, CaseIterable, Identifiable {
    case home
    case tracks
    case practice
    case profile

    public var id: String { rawValue }

    public var label: String {
        switch self {
        case .home: return "Início"
        case .tracks: return "Trilhas"
        case .practice: return "Prática"
        case .profile: return "Perfil"
        }
    }

    public var icon: String {
        switch self {
        case .home: return "🏠"
        case .tracks: return "📚"
        case .practice: return "⚡"
        case .profile: return "👤"
        }
    }
}

