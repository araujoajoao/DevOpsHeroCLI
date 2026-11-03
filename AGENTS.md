# DevOpsHero Project Rules & Architecture Guidelines

## 1. Apple Design Resources & iOS HIG Compliance
- **Official Kit Reference**: [Apple Design Resources for iOS Apps](https://developer.apple.com/design/resources/#ios-apps)
- **Mandate**: Para todas as implementações mobile iOS (tanto no aplicativo nativo `devopshero-ios-swiftui` quanto no app React Native `devopshero-mobile`):
  - **Componentes e Layout**: Utilizar rigorosamente a anatomia dos kits oficiais da Apple (Navigation Bars, Tab Bars, Inset Grouped Lists, Modals, Action Sheets e Alerts).
  - **Curvatura Contínua (Squircle)**: Aplicar sempre cantos arredondados contínuos (`RoundedRectangle(cornerRadius: 16, style: .continuous)` no SwiftUI e proporções squircle correspondentes no React Native).
  - **Touch Targets (Acessibilidade)**: Garantir área de toque mínima de **44x44 pontos** (`.frame(minHeight: 44)` e `hitSlop`) em todos os elementos clicáveis (botões, ícones de fechar, links).
  - **Iconografia**: Utilizar a biblioteca oficial **SF Symbols** da Apple (`Image(systemName: ...)`).
  - **Tipografia**: SF Pro (com Dynamic Type) para interface e SF Mono (`Menlo`) para identificadores técnicos, versões e comandos de terminal.
  - **Materiais e Cores do Sistema**: Utilizar cores semânticas nativas (`Color(uiColor: .systemBackground)`, `Color(uiColor: .secondarySystemBackground)`, `.ultraThinMaterial`, `Divider()` nativo).
  - **Feedback Háptico**: Integrar respostas táteis nativas do Taptic Engine (`UIImpactFeedbackGenerator`, `UINotificationFeedbackGenerator`, `expo-haptics`).

## 2. Paridade entre Plataformas (CLI & Mobile)
- **Regra**: Sempre que adicionar ou modificar conteúdo (novas missões, trilhas, recursos visuais, modais, etc.), adicionar e sincronizar em ambos:
  - **CLI**: `devopsherocli` (Textual TUI / Python).
  - **Mobile**: `devopshero-mobile` (React Native Expo) e `devopshero-ios-swiftui` (Swift / Xcode).

## 3. Comportamento do Botão de Atualização (Update)
- O botão/pílula de atualização (`UPDATE`) deve ser **oculto por padrão** e exibido **exclusivamente quando houver uma nova versão ou alteração disponível** em relação ao repositório remoto.

