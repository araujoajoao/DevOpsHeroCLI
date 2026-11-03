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

## 4. Layout Oficial da Tela Inicial (Cards de Trilhas DevOps / Career Path Cards)
- **Padrão Oficial e Exclusivo**: O layout oficial, definitivo e exclusivo da aplicação para iOS SwiftUI (`devopshero-ios-swiftui`) e React Native Mobile (`devopshero-mobile`) é o **Career Path Cards** (estilo visual da referência oficial `Select Path` / `Career Paths`):
  - **Anatomia dos Cards**:
    - Fundo slate-navy (`#272E4F`) sobre tela dark violet-navy (`#131627`).
    - Linha superior com **ícones da stack tecnológica** (`[🐳][📦][🐧][🌐][📜]`) em pequenos blocos coloridos contínuos.
    - Título da trilha em **tipografia tech monospaced em negrito** (`SF Mono` / `Menlo`): `Full-Stack DevOps`, `Docker & Containers`, `Kubernetes Cluster Admin`.
    - Linha de progresso com etiqueta `SECTION` à esquerda e fração `18/20` ou `8/10` à direita.
    - **Barra de progresso arredondada lilás** (`#9E85FF`) sobre trilha escura.
    - **Destaque da Trilha Ativa**: Borda externa dupla iluminada em lilás (`#9E85FF`) contornando o card selecionado.
  - **Identidade Educacional**: Estritamente voltado a laboratórios práticos de linha de comando DevOps & SRE. Sem metáforas financeiras, sem cifras monetárias (`$`) ou números de cartão de crédito.
  - **Modal Select Path**: Cabeçalho com `✕` à esquerda, título centralizado `Select Path` e lista vertical rolável de Career Path Cards.
  - **Botão de Ação**: FAB neon com ícone `▶` centralizado no eixo X disparando o laboratório prático CLI da trilha ativa.
  - **Interface Unificada e Limpa**: A experiência é 100% padronizada no modo Cards de Trilhas, eliminando alternâncias ou modos legados obsoletos.

## 5. Tela de Questões e Missões da Trilha (Coding Path / DevOps Path)
- **Padrão Oficial e Exclusivo**: Ao selecionar um card de Career Path (ou acessar a aba de Trilhas), o aplicativo apresenta a lista de missões/perguntas da trilha com a seguinte anatomia:
  - **Barra Superior**: Botão `✕` à esquerda (retorno à tela inicial), título centralizado `DevOps Path` (em fonte monospaced tech negrito) e botão de tema à direita. Área mínima de toque de 44x44 pontos.
  - **Título da Trilha**: Nome da trilha em fonte `SF Mono` / `Menlo` em negrito (24pt) acompanhado do botão de alternância `⇄` (que abre o modal `Select Path` para troca rápida de trilha).
  - **Progresso da Trilha**: Linha com `SECTION` à esquerda e fração `X/Y` à direita, com barra de progresso arredondada lilás (`#9E85FF`).
  - **Cards de Missões (Perguntas)**:
    - Cards retangulares com cantos arredondados contínuos (`RoundedRectangle(cornerRadius: 18, style: .continuous)` / `borderRadius: 18`).
    - Fundo slate-navy (`#272E4F`) no modo escuro e cinza suave (`#EDF0F7`) no modo claro.
    - Título da missão no lado esquerdo em tipografia `SF Mono` / `Menlo` em negrito.
    - Indicador de estado no lado direito:
      - **Bloqueada**: Ícone de cadeado (`Image(systemName: "lock.fill")` / `🔒`) dentro de badge suave contínuo.
      - **Concluída**: Ícone de checkmark (`✓`) em verde neon (`#00ff87`).
      - **Ativa / Próxima**: Ícone play (`▶`) em lilás (`#9E85FF`).
    - Ao tocar em uma missão desbloqueada, o laboratório prático é aberto imediatamente no terminal CLI da missão selecionada.

## 6. Arquitetura e Estilo da CLI (Flocí Cloud Console TUI)
- **Referência Oficial**: Console Flocí (`media_1793712818825_196aa998.jpg`).
- **Padrão Oficial da TUI (`devopsherocli`)**:
  - **Barra Lateral Esquerda (Sidebar)**:
    - Categorias técnicas em caixa alta (`GENERAL`, `CLOUD SERVICES · DEVOPS`, `COMPUTE`, `STORAGE & VCS`, `PROVISIONING`, `OBSERVABILITY`).
    - Itens de navegação: `⊞ Console Home`, `⚡ Terminal Lab` e acesso direto às trilhas com ícones técnicos.
    - Rodapé: `Flocí DevTools · Local «`.
  - **Barra Superior (Top Header)**:
    - Ícone e título dinâmico (`Console Home` / `Terminal Lab`), subtítulo e pílulas de filtro rápido de trilhas (`Linux`, `Docker`, `K8s`, `AWS`, `IaC`, `Obs`) e pílula dinâmica de `Update`.
  - **Modo Console Home (Dashboard)**:
    - **Hero Banner Card**: Borda esquerda contínua em verde esmeralda neon (`#10B981`), tag `SELECTED RUNTIME`, título da trilha selecionada, descrição e botão de ação `▶ Iniciar Prática (Enter)`.
    - **Barra de Métricas de Runtime**: 4 cartões com `CLOUD / WORKSPACE`, `RUNTIME (Reachable ((•)))`, `ACTIVE TRACKS` e `RESOURCES / XP`.
    - **Chips Micro-Status**: `UI: Console Home`, `PROXY: /api/terminal`, `ADAPTER: Oh My Zsh`, `RUNTIME: DevOpsHero Core`.
    - **Grid de Cartões de Serviço**: Grid 4 colunas x 2 linhas de cards com ícone em badge escuro, nome do serviço, indicador `● available` (verde) ou `● coming soon` (cinza), contagem de missões e subtexto.
  - **Modo Terminal Lab (Prática Interativa)**:
    - Painel esquerdo com briefing da missão (cenário, objetivo, regras e botões de auxílio).
    - Janela de terminal iTerm2 com Oh My Zsh, prompt contextual `➜ ~ git:(main)` e executor interativo de comandos.
  - **Alternância**: Tecla `F2` alterna instantaneamente entre o `Console Home` e o `Terminal Lab`.




