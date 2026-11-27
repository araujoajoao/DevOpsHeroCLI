# DevOpsHero (SwiftUI 100% Nativo)

Aplicativo nativo para iOS construído com **Swift 6** e **SwiftUI**, seguindo as diretrizes oficiais de design da Apple ([Apple HIG](https://developer.apple.com/ios/get-started/)) e as práticas do [Currículo Oficial de Desenvolvimento Swift](https://www.apple.com/br/education/docs/App_Development_with_Swift_Curriculum_Guide.pdf).

## ✨ Características
- **100% SwiftUI Declarativo**: Sem nenhum arquivo `.storyboard` ou `.xib`.
- **Ciclo de Vida Nativo Moderno**: `@main struct DevOpsHeroApp: App`
- **Padrão MVVM Reativo**: `DevOpsHeroViewModel` com publicação de estado para toda a aplicação.
- **Telas Implementadas**:
  - `HomeView`: Large Titles, Status Pill do operador, Hero CTA de Prática (`▶ Iniciar Prática ➔`), lista Inset Grouped de trilhas com ícones e chevrons `›`.
  - `TracksView`: Catálogo de trilhas com badges coloridos (Linux, Docker, Kubernetes, Git, AWS, CI/CD).
  - `PracticeView`: Cabeçalho fixo no topo (`‹ Início`, `⏸ Pausar`), terminal interativo `$`, Word Bank de blocos selecionáveis, barra de ação inferior (`Verificar Resposta ↵`, `[⏸ Pausar Trilha] • [🏠 Voltar para o Início]`), `PauseModalView`, e Bottom Sheet com `UNLOCKED` / `LOCKED`.
  - `ProfileView`: Terminal `whoami`, detalhes de SSH, troca de usuário, seletor de tema e grade de métricas.
  - `FloatingDockView`: Dock de navegação flutuante em vidro com 4 abas (`Início`, `Trilhas`, `Prática`, `Perfil`).

## 🚀 Como Abrir no Xcode

Para abrir diretamente no Xcode:
```bash
open devopshero-ios-swiftui/Package.swift
```
Ou no terminal:
```bash
xed devopshero-ios-swiftui
```

No Xcode, selecione qualquer simulador (ex: **iPhone 17 Pro Max** ou **iPhone 17**) e pressione `Cmd + R` para rodar ou visualize instantaneamente com o Canvas (`Cmd + Option + Return`).

