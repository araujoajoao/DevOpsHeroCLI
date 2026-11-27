import SwiftUI
import Combine
#if canImport(UIKit)
import UIKit
#endif

@MainActor
public class DevOpsHeroViewModel: ObservableObject {
    @Published public var themeMode: ThemeMode = .dark
    @Published public var activeTab: TabType = .home
    @Published public var dataset: AppDataset?

    @Published public var selectedTrackIndex: Int = 0
    @Published public var selectedMissionIndex: Int = 0

    @Published public var xp: Int = 350
    @Published public var streak: Int = 3
    @Published public var userName: String = "joao_araujo"
    @Published public var userEmail: String = "joao_araujo@devopshero.io"
    @Published public var userRole: String = "DevOps Engineer · Nível 2"
    @Published public var isLoggedIn: Bool = true

    public func login(username: String, email: String, role: String) {
        self.userName = username
        self.userEmail = email
        self.userRole = role
        self.isLoggedIn = true
        self.activeTab = .home
    }

    public func logout() {
        self.isLoggedIn = false
    }

    public var deviceTypeBadge: String {
        #if targetEnvironment(macCatalyst)
        return "🖥️ DESKTOP (macOS Catalyst)"
        #elseif canImport(UIKit)
        if ProcessInfo.processInfo.isiOSAppOnMac {
            return "🖥️ DESKTOP (Apple Silicon Mac)"
        }
        switch UIDevice.current.userInterfaceIdiom {
        case .pad:
            return "📟 TABLET (Apple iPad)"
        case .mac:
            return "🖥️ DESKTOP (Mac)"
        default:
            return "📱 MOBILE (Apple iPhone)"
        }
        #else
        return "🖥️ DESKTOP"
        #endif
    }

    // Practice State
    @Published public var placedChips: [String] = []
    @Published public var availableChips: [ChipItem] = []
    @Published public var secondsElapsed: Int = 0
    @Published public var isPaused: Bool = false
    @Published public var showPauseModal: Bool = false
    @Published public var showTipModal: Bool = false
    @Published public var currentTipText: String = ""
    @Published public var hasMoreTips: Bool = true
    @Published public var currentTipNumber: Int = 1
    public let maxTips: Int = 3
    @Published public var showEvaluationSheet: Bool = false
    @Published public var isCorrect: Bool = false
    @Published public var tipsUsed: Int = 0
    @Published public var solutionUsed: Bool = false
    @Published public var lastAward: AwardResult?
    @Published public var showingEditUser: Bool = false
    @Published public var newUsername: String = ""
    @Published public var shuffledMissionsByTrack: [String: [Mission]] = [:]
    @Published public var completedMissionIds: Set<String> = []
    @Published public var showUpdateModal: Bool = false
    @Published public var hasUpdateAvailable: Bool = false
    @Published public var targetVersion: String = "0.21.0"

    private var accumulatedSeconds: Int = 0
    private var startTime: Date = Date()
    private var timerCancellable: AnyCancellable?

    public init() {
        loadDataset()
        checkForRemoteUpdates()
    }

    public var currentTrack: Track? {
        guard let dataset = dataset, !dataset.tracks.isEmpty else { return nil }
        if selectedTrackIndex < dataset.tracks.count {
            return dataset.tracks[selectedTrackIndex]
        }
        return dataset.tracks.first
    }

    public var currentMission: Mission? {
        guard let track = currentTrack, !track.missions.isEmpty else { return nil }
        let list = shuffledMissionsByTrack[track.id] ?? track.missions
        if selectedMissionIndex < list.count {
            return list[selectedMissionIndex]
        }
        return list.first
    }

    public func loadDataset() {
        var targetURL: URL? = Bundle.main.url(forResource: "missions", withExtension: "json")
        #if SWIFT_PACKAGE
        if targetURL == nil {
            targetURL = Bundle.module.url(forResource: "missions", withExtension: "json")
        }
        #endif
        if let url = targetURL {
            do {
                let data = try Data(contentsOf: url)
                let decoded = try JSONDecoder().decode(AppDataset.self, from: data)
                self.dataset = decoded
                var map: [String: [Mission]] = [:]
                for t in decoded.tracks {
                    map[t.id] = t.missions.shuffled()
                }
                self.shuffledMissionsByTrack = map
                prepareMission()
                return
            } catch {
                print("Failed to decode missions.json from bundle: \(error)")
            }
        }
        
        // Fallback embedded dataset for development / testing
        self.dataset = AppDataset(
            appTitle: "DevOpsHero",
            tagline: "Aprenda DevOps na prática",
            totalTracks: 1,
            totalMissions: 1,
            tracks: [
                Track(
                    id: "linux",
                    name: "Linux Essencial",
                    icon: "🐧",
                    description: "Domine o terminal Linux, permissões e processos.",
                    missionsCount: 1,
                    missions: [
                        Mission(
                            id: "linux-01",
                            trackId: "linux",
                            trackName: "Linux Essencial",
                            trackIcon: "🐧",
                            title: "Diretório de Trabalho Atual",
                            difficulty: "Iniciante",
                            xp: 100,
                            scenario: "Você acessou o servidor de produção e precisa se situar.",
                            objective: "Exiba no terminal o caminho absoluto do diretório atual.",
                            tip: "O comando para imprimir o diretório de trabalho é 'pwd'.",
                            solution: "pwd",
                            exerciseTypes: ExerciseTypes(
                                wordBank: WordBankExercise(
                                    instruction: "Monte o comando correto tocando nos blocos:",
                                    targetTokens: ["pwd"],
                                    chips: ["-rf", "pwd", "ls", "-la", "grep"]
                                ),
                                fillInTheBlank: nil
                            )
                        )
                    ]
                )
            ]
        )
        var fallbackMap: [String: [Mission]] = [:]
        for t in self.dataset?.tracks ?? [] {
            fallbackMap[t.id] = t.missions.shuffled()
        }
        self.shuffledMissionsByTrack = fallbackMap
        prepareMission()
    }

    public func prepareMission() {
        guard let mission = currentMission else { return }

        let rawTokens = (mission.exerciseTypes.wordBank.chips?.isEmpty == false)
            ? (mission.exerciseTypes.wordBank.chips ?? mission.exerciseTypes.wordBank.targetTokens)
            : mission.exerciseTypes.wordBank.targetTokens

        self.availableChips = rawTokens.shuffled().enumerated().map { (idx, token) in
            ChipItem(id: "\(idx)-\(token)", text: token, isPlaced: false)
        }
        self.placedChips = []
        self.showEvaluationSheet = false
        self.showPauseModal = false
        self.showTipModal = false
        self.tipsUsed = 0
        self.currentTipText = ""
        self.hasMoreTips = true
        self.currentTipNumber = 1
        self.solutionUsed = false
        self.lastAward = nil
        self.accumulatedSeconds = 0
        self.secondsElapsed = 0

        // Live Activities & Dynamic Island integration (ActivityKit - 1998code/iOS16-Live-Activities)
        if let track = currentTrack {
            DevOpsLiveActivityManager.shared.startLabActivity(
                trackId: track.id,
                trackName: track.name,
                trackIcon: track.icon,
                missionId: mission.id,
                missionIndex: selectedMissionIndex,
                missionTitle: mission.title,
                objective: mission.objective,
                xpReward: mission.xp,
                completedCount: completedMissionsCount(for: track),
                totalMissions: track.missions.count,
                operatorHandle: "@\(userName)"
            )
        }

        startTimer()
    }

    public func startTimer() {
        stopTimer()
        startTime = Date()
        timerCancellable = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self = self else { return }
                let currentRun = Int(Date().timeIntervalSince(self.startTime))
                self.secondsElapsed = self.accumulatedSeconds + currentRun

                let speedMultiplier = self.secondsElapsed <= 5 ? 1.5 : (self.secondsElapsed <= 15 ? 1.2 : 1.0)
                DevOpsLiveActivityManager.shared.updateLabActivity(
                    secondsElapsed: self.secondsElapsed,
                    speedScoreMultiplier: speedMultiplier
                )
            }
    }

    public func stopTimer() {
        if timerCancellable != nil {
            let currentRun = Int(Date().timeIntervalSince(startTime))
            accumulatedSeconds += currentRun
            timerCancellable?.cancel()
            timerCancellable = nil
        }
    }

    public func pauseTrack() {
        stopTimer()
        isPaused = true
        showPauseModal = true
        DevOpsLiveActivityManager.shared.updateLabActivity(status: "PAUSED")
    }

    public func resumeTrack() {
        isPaused = false
        showPauseModal = false
        DevOpsLiveActivityManager.shared.updateLabActivity(status: "ONLINE")
        startTimer()
    }

    public func exitToHome() {
        stopTimer()
        isPaused = false
        showPauseModal = false
        DevOpsLiveActivityManager.shared.endLabActivity()
        activeTab = .home
    }

    public func exitToTracks() {
        stopTimer()
        isPaused = false
        showPauseModal = false
        DevOpsLiveActivityManager.shared.endLabActivity()
        activeTab = .tracks
    }

    public func addChip(chipId: String, text: String) {
        placedChips.append(text)
        if let idx = availableChips.firstIndex(where: { $0.id == chipId }) {
            availableChips[idx].isPlaced = true
        }
    }

    public func removeChip(at index: Int) {
        guard index < placedChips.count else { return }
        let textToRemove = placedChips.remove(at: index)
        if let idx = availableChips.firstIndex(where: { $0.text == textToRemove && $0.isPlaced }) {
            availableChips[idx].isPlaced = false
        }
    }

    public func progressiveTips(for mission: Mission) -> [String] {
        let tokens = mission.exerciseTypes.wordBank.targetTokens
        let solution = mission.solution.trimmingCharacters(in: .whitespacesAndNewlines)
        let rawTip = mission.tip.trimmingCharacters(in: .whitespacesAndNewlines)
        let objective = mission.objective.trimmingCharacters(in: .whitespacesAndNewlines)

        let firstCmd = tokens.first ?? (solution.split(separator: " ").first.map(String.init) ?? "comando")
        let numTokens = tokens.count

        // Dica 1: Ponto de partida
        let hint1 = "Início da operação: O comando inicia com o utilitário \"\(firstCmd)\". Objetivo: \(objective)"

        // Dica 2: Estrutura da sintaxe, flags e operadores
        let hint2: String
        if numTokens <= 1 {
            hint2 = "Estrutura simples: Este comando não requer argumentos adicionais. Ele é composto por apenas um bloco no terminal."
        } else if tokens.contains("&&") || tokens.contains("|") {
            let ops = tokens.filter { ["&&", "|", "||", ";"].contains($0) }
            hint2 = "Comando composto: Esta tarefa requer o operador \"\(ops.joined(separator: " "))\" conectando as operações em cadeia."
        } else {
            let flags = tokens.dropFirst().filter { $0.hasPrefix("-") }
            let args = tokens.dropFirst().filter { !$0.hasPrefix("-") }
            if let firstFlag = flags.first, let firstArg = args.first {
                hint2 = "Parâmetros e argumentos: Combine \"\(firstCmd)\" com a flag \(firstFlag) apontando para \"\(firstArg)\". (Total de \(numTokens) blocos)."
            } else if !flags.isEmpty {
                hint2 = "Modificadores: Utilize a(s) opção(ões) \(flags.joined(separator: ", ")) junto com \"\(firstCmd)\"."
            } else if let firstArg = args.first {
                hint2 = "Argumento alvo: O comando atua sobre \"\(firstArg)\". Linha montada com \(numTokens) blocos."
            } else {
                hint2 = "Estrutura da linha de comando: Selecione \(numTokens) blocos na ordem correta de execução."
            }
        }

        // Dica 3: Orientação técnica aprofundada
        let hint3 = "Orientação avançada: \(rawTip)"

        return [hint1, hint2, hint3]
    }

    public func openTip() {
        guard let mission = currentMission else { return }
        let tips = progressiveTips(for: mission)

        if tipsUsed < maxTips {
            tipsUsed += 1
            currentTipText = tips[tipsUsed - 1]
            hasMoreTips = true
            currentTipNumber = tipsUsed
            showTipModal = true
        } else {
            // Limite de 3 dicas atingido: não repete e encerra
            currentTipText = "🛑 Não há mais dicas disponíveis para esta missão.\n\nVocê já visualizou todas as 3 orientações. Monte o comando no terminal com os blocos disponíveis ou use o Gabarito se precisar da resposta completa."
            hasMoreTips = false
            currentTipNumber = maxTips
            showTipModal = true
        }
    }

    public func revealSolution() {
        guard let mission = currentMission else { return }
        stopTimer()
        solutionUsed = true
        streak = 0

        let targetTokens = mission.exerciseTypes.wordBank.targetTokens
        placedChips = targetTokens
        availableChips = availableChips.map { chip in
            var updated = chip
            updated.isPlaced = targetTokens.contains(chip.text)
            return updated
        }

        let award = AwardResult(
            xp: 0,
            baseXP: mission.xp,
            factor: 0,
            tierName: "Gabarito Revelado (0 XP)",
            elapsedSeconds: Double(secondsElapsed),
            tipsUsed: tipsUsed,
            streakBonusPct: 0,
            isNinja: false,
            solutionUsed: true
        )

        self.isCorrect = true
        self.lastAward = award
        self.showEvaluationSheet = true
    }

    public func verifyCommand() {
        guard !placedChips.isEmpty, let mission = currentMission else { return }
        stopTimer()

        let userCmd = placedChips.joined(separator: " ")
        let targetCmd = mission.exerciseTypes.wordBank.targetTokens.joined(separator: " ")
        let correct = (userCmd == targetCmd || userCmd == mission.solution)

        let factor: Double
        let tierName: String
        let isNinja: Bool

        if secondsElapsed <= 5 {
            factor = 1.5
            tierName = "NINJA SPEED"
            isNinja = true
        } else if secondsElapsed <= 12 {
            factor = 1.0
            tierName = "STANDARD"
            isNinja = false
        } else {
            factor = 0.8
            tierName = "THOUGHTFUL"
            isNinja = false
        }

        let penaltyFactor: Double
        if tipsUsed == 0 {
            penaltyFactor = 1.0
        } else if tipsUsed == 1 {
            penaltyFactor = 0.4
        } else if tipsUsed == 2 {
            penaltyFactor = 0.2
        } else {
            penaltyFactor = 0.1
        }

        let bonusPct = min(streak * 10, 50)
        let calcXP = Int(Double(mission.xp) * factor * penaltyFactor * (1.0 + Double(bonusPct) / 100.0))
        let earnedXP = max(5, calcXP)

        let award = AwardResult(
            xp: earnedXP,
            baseXP: mission.xp,
            factor: factor * penaltyFactor,
            tierName: tierName,
            elapsedSeconds: Double(secondsElapsed),
            tipsUsed: tipsUsed,
            streakBonusPct: bonusPct,
            isNinja: isNinja,
            solutionUsed: false
        )

        self.isCorrect = correct
        self.lastAward = award
        self.showEvaluationSheet = true

        if correct {
            self.xp += earnedXP
            self.streak += 1
            self.completedMissionIds.insert(mission.id)
            if let track = currentTrack {
                DevOpsLiveActivityManager.shared.updateLabActivity(
                    status: "COMPLETED",
                    completedCount: completedMissionsCount(for: track)
                )
            }
        } else {
            DevOpsLiveActivityManager.shared.updateLabActivity(status: "TRY AGAIN")
        }
    }

    public func continueAfterEvaluation() {
        showEvaluationSheet = false
        if isCorrect {
            nextMission()
        } else {
            startTimer()
        }
    }

    public func nextMission() {
        guard let track = currentTrack else { return }
        let missions = shuffledMissionsByTrack[track.id] ?? track.missions
        if selectedMissionIndex + 1 < missions.count {
            selectedMissionIndex += 1
            prepareMission()
        } else if let dataset = dataset, selectedTrackIndex + 1 < dataset.tracks.count {
            let nextTrack = dataset.tracks[selectedTrackIndex + 1]
            if isTrackUnlocked(nextTrack) {
                shuffledMissionsByTrack[nextTrack.id] = nextTrack.missions.shuffled()
                selectedTrackIndex += 1
                selectedMissionIndex = 0
                prepareMission()
            } else {
                activeTab = .home
            }
        } else {
            activeTab = .home
        }
    }

    public func isTrackUnlocked(_ track: Track) -> Bool {
        let req = track.requiredXp ?? 0
        return self.xp >= req
    }

    public func isMissionUnlocked(track: Track, missionIndex: Int) -> Bool {
        guard isTrackUnlocked(track) else { return false }
        if missionIndex == 0 { return true }
        let missions = shuffledMissionsByTrack[track.id] ?? track.missions
        guard missionIndex < missions.count else { return false }
        let mission = missions[missionIndex]
        if completedMissionIds.contains(mission.id) { return true }
        let prevMission = missions[missionIndex - 1]
        return completedMissionIds.contains(prevMission.id)
    }

    public func isMissionCompleted(missionId: String) -> Bool {
        return completedMissionIds.contains(missionId)
    }

    public func completedMissionsCount(for track: Track) -> Int {
        let missions = shuffledMissionsByTrack[track.id] ?? track.missions
        return missions.filter { completedMissionIds.contains($0.id) }.count
    }

    public func selectTrack(index: Int) {
        guard let dataset = dataset, index < dataset.tracks.count else { return }
        let track = dataset.tracks[index]
        if !isTrackUnlocked(track) { return }
        if shuffledMissionsByTrack[track.id] == nil {
            shuffledMissionsByTrack[track.id] = track.missions.shuffled()
        }
        selectedTrackIndex = index
        selectedMissionIndex = 0
        prepareMission()
        activeTab = .tracks
    }

    public func startMission(trackIndex: Int, missionIndex: Int) {
        guard let dataset = dataset, trackIndex < dataset.tracks.count else { return }
        let track = dataset.tracks[trackIndex]
        if !isTrackUnlocked(track) { return }
        if shuffledMissionsByTrack[track.id] == nil {
            shuffledMissionsByTrack[track.id] = track.missions.shuffled()
        }
        selectedTrackIndex = trackIndex
        selectedMissionIndex = missionIndex
        prepareMission()
        activeTab = .practice
    }

    public func toggleTheme() {
        themeMode = (themeMode == .dark) ? .light : .dark
    }

    public func checkForRemoteUpdates() {
        guard let url = URL(string: "https://raw.githubusercontent.com/araujoajoao/DevOpsHeroCLI/main/pyproject.toml") else { return }
        URLSession.shared.dataTask(with: url) { [weak self] data, _, _ in
            guard let data = data, let text = String(data: data, encoding: .utf8) else { return }
            if let range = text.range(of: "version = \"") {
                let sub = text[range.upperBound...]
                if let endRange = sub.range(of: "\"") {
                    let remoteVer = String(sub[..<endRange.lowerBound])
                    let localVer = "1.0.0"
                    let rParts = remoteVer.split(separator: ".").compactMap { Int($0) }
                    let lParts = localVer.split(separator: ".").compactMap { Int($0) }
                    var isNewer = false
                    for i in 0..<max(rParts.count, lParts.count) {
                        let r = (i < rParts.count) ? rParts[i] : 0
                        let l = (i < lParts.count) ? lParts[i] : 0
                        if r > l { isNewer = true; break }
                        if r < l { break }
                    }
                    if isNewer {
                        DispatchQueue.main.async {
                            self?.hasUpdateAvailable = true
                            self?.targetVersion = remoteVer
                        }
                    }
                }
            }
        }.resume()
    }
}
