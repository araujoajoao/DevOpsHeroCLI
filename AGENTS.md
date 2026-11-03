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
    - **Bandeja de Tokens (Word Bank Tray)**: Container dedicado (`#1E243E` / `rgba(30, 36, 62, 0.70)`), bordas suaves (`#272E4F`), cantos arredondados contínuos (`borderRadius: 18`) e padding interno generoso.
    - **Cabeçalho da Bandeja**: Badge tech embutido `⌨️ TOKENS` em lilás (`#9E85FF`) à esquerda e etiqueta itálica `toque para selecionar` em cinza suave à direita, separados por divisor sutil.
    - **Tokens / Blocos de Comando**:
      - Botões com cantos arredondados contínuos (`borderRadius: 10`, `minHeight: 40`, `paddingHorizontal: 14`, `paddingVertical: 8`, tipografia `SF Mono` / `Menlo` em negrito 13.5-14pt).
      - Fundo slate-navy (`#272E4F`) com borda colorida de 1.5pt no syntax highlighting da categoria técnica.
      - **Estado Encaixado / Desabilitado (Socket Receptacle)**: Ao selecionar um token, o espaço original na bandeja transforma-se em um receptáculo rebaixado (fundo translúcido, borda tracejada em lilás sutil e texto atenuado a 22% de opacidade), transmitindo sensação tátil de bloco físico movido para o terminal.
      - Acessibilidade Apple HIG: área de toque mínima garantida de 44x44 pontos via `hitSlop` e frames acessíveis.
  - **Barra de Ações Inferior (Rodapé de Comandos)**:
    - **Botões de Auxílio (Dica e Gabarito)**: Acabamento slate-navy (`#1E243E`), cantos contínuos (`borderRadius: 14`), altura de 46pt e badges embutidos:
      - `💡 DICA`: borda âmbar translúcida, texto em negrito monospaced e pílula embutida com o contador `{tipsUsed}/{MAX_TIPS}`.
      - `👁️ GABARITO`: borda coral translúcida, texto em negrito monospaced e pílula embutida `0 XP`.
    - **Botão Principal de Ação (Verificar Resposta)**: Lilás `#9E85FF` ativo com sombra neon e brilho suave, altura 54pt, cantos contínuos (`borderRadius: 16`), texto em caixa alta `VERIFICAR RESPOSTA ↵` (ou `CONTINUAR PARA PRÓXIMA ETAPA ➔`) em tipografia tech monospaced; quando desabilitado, assume fundo slate-navy (`#1E243E`) com texto placeholder `toque nos blocos para montar`.
    - **Ações Secundárias**: Pílulas compactas (`borderRadius: 20`) de `⏸ Pausar Trilha` e `🏠 Voltar ao Início` em fundo escuro com bordas sutis.
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

## 8. Arquitetura da Tela de Login / Cadastro e Integração EmailJS (Mobile Auth Flow)
- **Referência Oficial**: Mobile Login & Registration Screen (`media_1793722525475_bf6d246b.jpg`).
- **Padrão Oficial (SwiftUI & React Native)**:
  - **Identidade Visual e Emblema (`BrandEmblem`)**:
    - Fundo com gradiente violeta escuro profundo (`#131627` / `#1E1B4B` / `#2E1065`) decorado com pílulas flutuantes diagonais translúcidas e traços luminosos (streak lines).
    - Emblema central de 3 barras horizontais em gradiente cromado/prateado (`#FFFFFF` -> `#A5B4FC` -> `#818CF8`) com cantos arredondados contínuos e o nó esférico luminoso conectado à barra central (representando nós de infraestrutura e orquestração).
  - **Fluxo de 3 Etapas**:
    1. **Tela A - Welcome / Apresentação**:
       - Emblema central grande (88-90pt) com aura luminosa lilás.
       - Marca e tipografia `DevOpsHero` em negrito tech com subtítulo descritivo de laboratórios práticos.
       - Botão primário estilo pílula `Get Started` em branco puro com texto contrastante escuro e cantos totalmente arredondados (`borderRadius: 28`).
       - Link secundário `I already have an account` com feedback tátil e transição suave para login.
    2. **Tela B - Sheet de Login / Registro**:
       - Bottom sheet deslizante com curvatura de canto superior ampla (`borderTopLeftRadius: 36`).
       - Cabeçalho amigável `hello!` em tipografia negrito monospaced acompanhado de alternância rápida entre `Sign Up` e `Sign In`.
       - Campos de entrada estilizados com bordas arredondadas contínuas (`borderRadius: 22`, altura mínima 50pt) e ícones semânticos à esquerda (`👤 Username`, `✉️ Email`, `🛡️ Password`).
       - Campo de senha com alternador de visibilidade (ícone de olho `👁️` / `🔒`) com área de toque mínima de 44x44pt.
       - Checkbox acessível de concordância com termos (`I agree to the terms and conditions`).
       - Botão primário lilás neon (`#9E85FF`) com sombra e curvatura contínua para disparar o envio de verificação.
       - Divisor `or` e botões de provedores sociais SSO em formato de squircle arredondado (Vermelho Google, Dourado AWS, Azul GitHub).
    3. **Tela C - Verificação OTP via EmailJS**:
       - Disparo de código OTP de 6 dígitos via API REST do EmailJS (`https://api.emailjs.com/api/v1.0/email/send`) utilizando as credenciais oficiais do projeto (`service_gxm4z5e`, `template_1hondid`, `ZUXg-zLHTMAg-LqnX`).
       - Interface com 6 caixas numéricas individuais com foco automático e detecção de entrada.
       - Temporizador regressivo de expiração do código e opção de reenvio (`Resend Code`).
       - Validação instantânea e persistência do operador na sessão do aplicativo (`isLoggedIn = true`).

## 9. Arquitetura e Estilo da CLI Superfile (Multi-Pane Terminal Architecture)
- **Referência Oficial**: Superfile TUI (`media_1793725195504_2eedbd64.jpg`).
- **Padrão Oficial da TUI (`devopsherocli`)**:
  - **Paleta Obsidian & Neon Superfile**: Fundo geral escuro `#0f111a`, sidebar `#0d0f17`, painéis `#131622` / `#161928`, bordas arredondadas semânticas (`round`).
  - **Bordas com Títulos e Subtítulos Embutidos (`border: round <color>`)**:
    - **Sidebar Esquerda**: Borda rose/coral `#fb7185`, título embutido `📁 Super File`, subtítulo `v1.1.0`. Navegação em lista com itens colapsáveis (`Pinned`, `Disks/Runtimes`).
    - **Painel Explorador de Missões (Directory Pane)**: Borda lilás `#9e85ff`, título embutido `📁 .../{track.id}`, subtítulo `👁 Browser {idx}/{total}`. Campo de busca superior `🔍 (/) Filter missions or type...` e lista de missões em estilo arquivos executáveis (`❯ {id}.sh` ativo com chevron neon cyan, `✓ {id}.sh` concluído em verde esmeralda, `🔒 {id}.sh` bloqueado).
    - **Painel Terminal & Code Window (Code Pane)**: Borda azure cyan `#38bdf8`, título embutido `💻 {mission.id}.sh`, subtítulo `⭐ +{xp} XP │ ● ONLINE`. Semáforos macOS `🔴 🟡 🟢` no topo, saída de terminal limpa com syntax highlighting e prompt de entrada integrado `➜ ~ `.
  - **Tri-Panel Tray Inferior (Bandeja Tripla Modular)**: Três painéis lado a lado com `border: round #272e4f`:
    - **Painel 1: `[ Processes ]`**: Monitor de Speed Score (Anti-Cola), barra de progresso visual de XP em gradiente e status de Streak.
    - **Painel 2: `[ Metadata ]`**: Metadados detalhados do arquivo/missão (`FileName`, `FileSize`, `FileModifyDate`, `Track`, `Difficulty`) e contextualização do cenário.
    - **Painel 3: `[ Clipboard ]`**: Ações rápidas de suporte (`💡 Dica (F3)`, `👁️ Solução (F4)`, `🧹 Reset (F5)`, `🗺️ Trilhas (F2)`) e caixas dinâmicas de exibição de dicas progressivas e gabarito.
  - **Regra de Não-Truncamento e Alinhamento**:
    - Jamais truncar ou quebrar palavras no meio de termos ou descrições em nenhuma janela da TUI.
    - Manter alinhamento horizontal e vertical preciso em todos os painéis e botões de ação.
  - **Navegação por Tab e Filosofia Sem Clique (Keyboard-First TUI)**:
    - O console terminal é estritamente orientado a teclado e navegação rápida via `Tab` / `Shift+Tab`.
    - Eliminação de botões GUI que quebram layout ou aprisionam o foco:
      - Cabeçalho superior: barra limpa de 1 linha interna com título da console, breadcrumb da trilha ativa e status de navegação.
      - Painel de Clipboard: cheat-sheet elegante de atalhos globais (`[F3] Dica`, `[F4] Gabarito`, `[F5] Reset`, `[F2] Trilhas`, `[Tab] Painéis`).
      - Navegação fluida entre os 6 painéis principais (`floci-sidebar` ⇄ `mission-panel` ⇄ `term-input` ⇄ `panel-processes` ⇄ `panel-metadata` ⇄ `panel-clipboard`).
      - O painel focado recebe destaque imediato de borda iluminada (`:focus` / `:focus-within`).
      - Nas listas (Sidebar e Missões), as teclas `↑` / `↓` (ou `k` / `j`) movem o cursor e `Enter` seleciona. No terminal, digitação direta no prompt com histórico.







