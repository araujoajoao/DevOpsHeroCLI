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
    - Linha superior com **um único badge exclusivo com o logotipo vetorial oficial da tecnologia** (ex: pinguim Tux oficial para Linux, prompt para SysAdmin/Bash, logo oficial do Git, baleia oficial do Docker, AWS, Terraform, Kubernetes e Datadog) em container arredondado contínuo (`34x34pt` com curvatura contínua).
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
- **Referência Oficial**: Console Flocí (`media_1793712818825_196aa998.jpg`) e Estilo macOS Window (`media_1793714309288_cf334ed3.png`).
- **Padrão Oficial da TUI (`devopsherocli`)**:
  - **Paleta Slate-Navy**: Fundo geral `#131627`, sidebar `#0F1220`, cabeçalho `#181D33`, painéis `#161B2E` / `#1E243E` e bordas `#272E4F`.
  - **Barra Lateral Esquerda (Sidebar)**:
    - Categorias técnicas em caixa alta (`GENERAL`, `CLOUD SERVICES · DEVOPS`, `COMPUTE`, `STORAGE & VCS`, `PROVISIONING`, `OBSERVABILITY`).
    - Itens de navegação: `⊞ Console Home`, `⚡ Terminal Lab` e acesso direto às trilhas com ícones técnicos.
    - Rodapé: `Flocí DevTools · Local «`.
  - **Barra Superior (Top Header)**:
    - Ícone e título dinâmico (`Console Home` / `Terminal Lab`), subtítulo e pílulas de filtro rápido de trilhas (`Linux`, `Docker`, `K8s`, `AWS`, `IaC`, `Obs`) e pílula dinâmica de `Update`.
  - **Modo Console Home (Dashboard)**:
    - **Hero Banner Card**: Fundo `#1E243E`, borda esquerda contínua em verde esmeralda neon (`#10B981`), tag `SELECTED RUNTIME`, título da trilha selecionada, descrição completa sem cortes e botão de ação `▶ Iniciar Prática (Enter)`.
    - **Barra de Métricas de Runtime**: 4 cartões com `CLOUD / WORKSPACE`, `RUNTIME (Reachable ((•)))`, `ACTIVE TRACKS` e `RESOURCES / XP`.
    - **Chips Micro-Status**: `UI: Console Home`, `PROXY: /api/terminal`, `ADAPTER: Oh My Zsh`, `RUNTIME: DevOpsHero Core`.
    - **Grid de Cartões de Serviço**: Grid 4 colunas x 2 linhas de cards com ícone em badge escuro, nome do serviço, indicador `● available` (verde) ou `● coming soon` (cinza), contagem de missões e subtexto.
  - **Modo Terminal Lab (Prática Interativa)**:
    - **Painel Esquerdo (Briefing)**: Cenário, objetivo da missão (borda arredondada lilás `#9E85FF`), regras speed score e botões de auxílio centralizados.
    - **Janela de Terminal (macOS Style Window)**:
      - Title Bar: Fundo `#181D33`, semáforos macOS `🔴🟡🟢` (`#ff5f56`, `#ffbd2e`, `#27c93f`), aba ativa com o nome do script `{mission.id}.sh` e badge de XP e status `⭐ +{xp} XP │ ● ONLINE`.
      - Numeração de Linhas Integrada: Linha `1 # {mission.objective}` comentada no topo do log e prompt de comando iniciando em linha `2 ➜ ~ {cwd}`.
    - **Regra de Não-Truncamento e Alinhamento**:
      - Nunca truncar ou quebrar palavras arbitrariamente no meio de frases em nenhuma plataforma (CLI ou Mobile).
      - Todos os botões, badges, títulos e réguas de prompt devem manter perfeito alinhamento e centralização vertical e horizontal.
  - **Alternância**: Tecla `F2` alterna instantaneamente entre o `Console Home` e o `Terminal Lab`.

## 7. Montagem de Comandos e Drawer de Avaliação (Question & Code Assembly Screen)
- **Referência Oficial**: Mimo Code Flow & Feedback Drawer (`media_1793714309288_cf334ed3.png`).
- **Padrão Oficial (SwiftUI & React Native)**:
  - **Editor de Código / Área de Montagem (Code Editor Window)**:
    - Container estilizado como janela de código (`#1E243E` / `#272E4F`), bordas suaves e numeração de linhas.
    - **Linha 1**: Número `1` e comentário técnico com o objetivo da missão (`# {mission.objective}`).
    - **Linha 2**: Número `2`, símbolo de prompt neon green (`$`) e slot receptacle de montagem dinâmica.
    - **Slot Receptacle de Montagem**:
      - Receptáculo com cantos arredondados contínuos (`borderRadius: 8`, `minHeight: 38`, `paddingHorizontal: 8`, `paddingVertical: 5`).
      - Estado vazio: borda tracejada em tom lilás (`rgba(158, 133, 255, 0.40)`), fundo sutil e texto placeholder `toque nos blocos abaixo para montar...` em 12pt itálico.
      - Tokens montados: chips compactos (`minHeight: 28`, `paddingHorizontal: 9`, `paddingVertical: 4.5`, `fontSize: 13pt` bold monospaced, `borderRadius: 6`) com preenchimento translúcido e borda na cor semântica do token.
    - **Syntax Highlighting nos Tokens**:
      - Utilitários / Comandos raiz (`docker`, `kubectl`, `git`, `chmod`, `aws`, etc.): Coral/pink `#FB7185`.
      - Modificadores e Flags (`-`): Amber `#FBBF24`.
      - Subcomandos (`run`, `build`, `commit`, `apply`, `exec`, etc.): Lilás `#9E85FF`.
      - Parâmetros, paths e strings com pontuação (`:`, `/`, `.`, aspas): Mint green `#00DF89` / `#10B981`.
      - Argumentos padrão: Azure Cyan `#00F2FE`.
  - **Word Bank (Banco de Opções de Comando)**:
    - Botões compactos estilizados no mesmo acabamento do terminal: fundo slate-navy (`#272E4F`), bordas de syntax highlighting e tipografia monospaced em negrito (`minHeight: 36`, `paddingHorizontal: 12`, `paddingVertical: 7`, `borderRadius: 8`, `fontSize: 13.5pt` bold monospaced, espaçamento `gap: 8`).
    - Destaque sintático individual por tipo de token (`border` e `color` com base na categoria técnica).
    - Estado montado/desabilitado: fundo sutil slate com opacidade reduzida (`0.28`), borda tracejada e texto esmaecido.
    - Acessibilidade Apple HIG: área de toque mínima garantida de 44x44 pontos via `hitSlop` e frames acessíveis.
  - **Barra de Ações Inferior (Rodapé de Comandos)**:
    - **Botões de Auxílio (Dica e Gabarito)**: Acabamento slate-navy (`#272E4F`) idêntico ao terminal, cantos contínuos (`borderRadius: 12`), altura mínima de 44pt e bordas semânticas (âmbar para dicas e coral para gabarito).
    - **Botão Principal de Ação (Verificar Resposta)**: Lilás `#9E85FF` quando ativo com sombra e brilho suave, texto em caixa alta `VERIFICAR RESPOSTA ↵` (ou `CONTINUAR PARA PRÓXIMA ETAPA ➔`) em tipografia tech monospaced; quando desabilitado, assume fundo slate-navy (`#272E4F`) com texto discreto.
    - **Ações Secundárias**: Pílulas compactas de `Pausar Trilha` e `Voltar ao Início` em fundo escuro com bordas sutis.
  - **Drawer / Bottom Sheet de Avaliação (Evaluation Sheet)**:
    - **Pílula de Status Superior**:
      - Incorreto: `Almost there..` em coral `#FB7185` com fundo suave e borda translúcida.
      - Correto: `Excelente!` em verde neon `#00DF89`.
      - Gabarito: `Gabarito Oficial` em âmbar `#FBBF24`.
    - **Mascote CRT Retrô**:
      - Monitor CRT com moldura cinza, tela escura `#0B0F19`, pés de apoio e LED indicador.
      - Expressões da tela: Cruz em pixels `✕` coral quando incorreto, olhos indagadores `• •` âmbar quando gabarito, checkmark/olhos felizes `✓` quando correto.
    - **Balão de Feedback (Speech Bubble)**:
      - Posicionado ao lado do mascote com texto explicativo/orientativo.
      - Botão de ação rápida `✨ GET HELP` integrado diretamente no balão para acionamento de dicas progressivas.
    - **Botão de Ação Inferior em Lilás (`#9E85FF`)**:
      - Botão largo de altura 54-56pt com cantos arredondados contínuos e sombra lilás suave.
      - Texto `↺ TRY AGAIN` (quando incorreto) ou `CONTINUAR ➔` (quando correto).





