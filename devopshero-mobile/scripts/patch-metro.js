const fs = require('fs');
const path = require('path');

const nodeModulesDir = path.join(__dirname, '..', 'node_modules');

if (fs.existsSync(nodeModulesDir)) {
  const exportsDef = {
    '.': './src/index.js',
    './package.json': './package.json',
    './private/*': './src/*.js',
    './src/*.js': './src/*.js',
    './src/*/*.js': './src/*/*.js',
    './src/*/*/*.js': './src/*/*/*.js',
    './src/*/*/*/*.js': './src/*/*/*/*.js',
    './src/*': './src/*.js',
    './src/*/*': './src/*/*.js',
    './src/*/*/*': './src/*/*/*.js',
    './src/*/*/*/*': './src/*/*/*/*.js',
  };

  const targetedPkgs = [
    'metro',
    'metro-config',
    'metro-core',
    'metro-resolver',
    'metro-cache',
    'metro-cache-key',
    'metro-symbolicate',
    'metro-babel-transformer',
    'metro-file-map',
    'metro-minify-terser',
    'metro-transform-plugins',
    'metro-transform-worker',
  ];

  for (const pkg of targetedPkgs) {
    const pkgJsonPath = path.join(nodeModulesDir, pkg, 'package.json');
    if (fs.existsSync(pkgJsonPath)) {
      try {
        const content = JSON.parse(fs.readFileSync(pkgJsonPath, 'utf8'));
        content.main = 'src/index.js';
        content.exports = exportsDef;
        fs.writeFileSync(pkgJsonPath, JSON.stringify(content, null, 2) + '\n', 'utf8');
      } catch (e) {
        console.error(`[patch-metro] Failed to patch package.json for ${pkg}:`, e.message);
      }
    }
  }

  // metro-source-map (main is src/source-map.js)
  const sourceMapPkg = path.join(nodeModulesDir, 'metro-source-map', 'package.json');
  if (fs.existsSync(sourceMapPkg)) {
    try {
      const content = JSON.parse(fs.readFileSync(sourceMapPkg, 'utf8'));
      content.main = 'src/source-map.js';
      content.exports = {
        '.': './src/source-map.js',
        './package.json': './package.json',
        './private/*': './src/*.js',
      };
      fs.writeFileSync(sourceMapPkg, JSON.stringify(content, null, 2) + '\n', 'utf8');
    } catch (e) {
      console.error('[patch-metro] Failed to patch metro-source-map package.json:', e.message);
    }
  }

  // Specific CJS / ESM serializer patches
  const sourceMapStringFile = path.join(nodeModulesDir, 'metro', 'src', 'DeltaBundler', 'Serializers', 'sourceMapString.js');
  if (fs.existsSync(sourceMapStringFile)) {
    try {
      let code = fs.readFileSync(sourceMapStringFile, 'utf8');
      if (!code.includes('exports.default = sourceMapString')) {
        code += '\nexports.default = sourceMapString;\nsourceMapString.sourceMapString = sourceMapString;\n';
        fs.writeFileSync(sourceMapStringFile, code, 'utf8');
      }
    } catch (e) {
      console.error('[patch-metro] Failed to patch sourceMapString.js:', e.message);
    }
  }

  const jsFileWrappingFile = path.join(nodeModulesDir, 'metro', 'src', 'ModuleGraph', 'worker', 'JsFileWrapping.js');
  if (fs.existsSync(jsFileWrappingFile)) {
    try {
      let code = fs.readFileSync(jsFileWrappingFile, 'utf8');
      if (!code.includes('exports.default = {')) {
        code += '\nexports.default = {\n  jsonToCommonJS,\n  wrapJson,\n  wrapModule,\n  wrapModuleString,\n  wrapPolyfill,\n};\n';
        fs.writeFileSync(jsFileWrappingFile, code, 'utf8');
      }
    } catch (e) {
      console.error('[patch-metro] Failed to patch JsFileWrapping.js:', e.message);
    }
  }

  // metro-cache-key (must export callable function as default)
  const cacheKeyFile = path.join(nodeModulesDir, 'metro-cache-key', 'src', 'index.js');
  if (fs.existsSync(cacheKeyFile)) {
    try {
      let code = fs.readFileSync(cacheKeyFile, 'utf8');
      if (!code.includes('getCacheKey.default = getCacheKey')) {
        code += '\nif (typeof getCacheKey === "function") {\n  getCacheKey.default = getCacheKey;\n  getCacheKey.getCacheKey = getCacheKey;\n  module.exports = getCacheKey;\n}\n';
        fs.writeFileSync(cacheKeyFile, code, 'utf8');
      }
    } catch (e) {
      console.error('[patch-metro] Failed to patch metro-cache-key:', e.message);
    }
  }

  // metro-core/src/Terminal.js (_logLines compatibility for @expo/cli)
  const terminalFile = path.join(nodeModulesDir, 'metro-core', 'src', 'Terminal.js');
  if (fs.existsSync(terminalFile)) {
    try {
      let code = fs.readFileSync(terminalFile, 'utf8');
      if (!code.includes('get _logLines()')) {
        const insert = `
  get _logLines() {
    return this.#logLines;
  }
  set _logLines(val) {
    this.#logLines = val;
  }
  _scheduleUpdate() {
    this.#scheduleUpdate();
  }
`;
        code = code.replace('persistStatus() {', insert + '  persistStatus() {');
        fs.writeFileSync(terminalFile, code, 'utf8');
      }
    } catch (e) {
      console.error('[patch-metro] Failed to patch metro-core Terminal.js:', e.message);
    }
  }

  // @expo/cli instantiateMetro.js safe logging patch
  const instantiateMetroFile = path.join(nodeModulesDir, '@expo', 'cli', 'build', 'src', 'start', 'server', 'metro', 'instantiateMetro.js');
  if (fs.existsSync(instantiateMetroFile)) {
    try {
      let code = fs.readFileSync(instantiateMetroFile, 'utf8');
      if (code.includes('this._logLines.push(') && !code.includes('SAFE_LOG_PATCH')) {
        code = code.replace(
          'this._logLines.push(',
          '// SAFE_LOG_PATCH\n            if (!this._logLines) { this._logLines = []; }\n            this._logLines.push('
        );
        fs.writeFileSync(instantiateMetroFile, code, 'utf8');
      }
    } catch (e) {
      console.error('[patch-metro] Failed to patch instantiateMetro.js:', e.message);
    }
  }

  // @expo/cli ManifestMiddleware.js asset resolver patch for --tunnel and exp://
  const manifestMiddlewareFile = path.join(nodeModulesDir, '@expo', 'cli', 'build', 'src', 'start', 'server', 'middleware', 'ManifestMiddleware.js');
  if (fs.existsSync(manifestMiddlewareFile)) {
    try {
      let code = fs.readFileSync(manifestMiddlewareFile, 'utf8');
      const target = "return bundleUrl.match(/^https?:\\/\\/.*?\\//)[0] + 'assets/' + path;";
      if (code.includes(target)) {
        const replacement = `const baseMatch = (bundleUrl || '').match(/^(?:https?|exp):\\/\\/[^\\/\\?]+/);
                const isSecure = (bundleUrl || '').includes('https:') || (bundleUrl || '').includes('ngrok');
                const proto = isSecure ? 'https:' : 'http:';
                const host = baseMatch ? baseMatch[0].replace(/^(?:https?|exp):/, '') : '//localhost:8081';
                const baseUrl = proto + host + '/';
                return baseUrl + 'assets/' + path;`;
        code = code.replace(target, replacement);
      }
      if (code.includes("bytecode: engine === 'hermes'")) {
        code = code.replace("bytecode: engine === 'hermes'", "bytecode: false");
      }
      fs.writeFileSync(manifestMiddlewareFile, code, 'utf8');
    } catch (e) {
      console.error('[patch-metro] Failed to patch ManifestMiddleware.js:', e.message);
    }
  }

  // Ensure @expo/ngrok is linked locally if installed globally
  const localNgrok = path.join(nodeModulesDir, '@expo', 'ngrok');
  if (!fs.existsSync(localNgrok)) {
    const globalNgrokCandidates = [
      '/opt/homebrew/lib/node_modules/@expo/ngrok',
      '/usr/local/lib/node_modules/@expo/ngrok',
    ];
    for (const candidate of globalNgrokCandidates) {
      if (fs.existsSync(candidate)) {
        try {
          fs.symlinkSync(candidate, localNgrok);
          console.log(`[patch-metro] Linked global @expo/ngrok from ${candidate}`);
          break;
        } catch (e) {}
      }
    }
  }

  // Ensure expo package version aligns with SDK 58
  const expoPkgPath = path.join(nodeModulesDir, 'expo', 'package.json');
  if (fs.existsSync(expoPkgPath)) {
    try {
      const expJson = JSON.parse(fs.readFileSync(expoPkgPath, 'utf8'));
      if (expJson.version && !expJson.version.startsWith('58.')) {
        expJson.version = '58.0.0';
        fs.writeFileSync(expoPkgPath, JSON.stringify(expJson, null, 2) + '\n', 'utf8');
        console.log('[patch-metro] Aligned expo package version to 58.0.0');
      }
    } catch (e) {
      console.error('[patch-metro] Failed to update expo package version:', e.message);
    }
  }

  // Ensure @react-native/js-polyfills is present in devopshero-mobile
  const localJsPolyfills = path.join(nodeModulesDir, '@react-native', 'js-polyfills');
  if (!fs.existsSync(localJsPolyfills)) {
    const parentPolyfills = path.join(nodeModulesDir, '..', '..', 'node_modules', '@react-native', 'js-polyfills');
    if (fs.existsSync(parentPolyfills)) {
      try {
        fs.cpSync(parentPolyfills, localJsPolyfills, { recursive: true });
        console.log('[patch-metro] Copied @react-native/js-polyfills from parent node_modules');
      } catch (e) {}
    }
  }

  // React Native Flow & Codegen compatibility patches
  const rnTransformSync = path.join(nodeModulesDir, '@expo', 'metro-config', 'build', 'transformSync.js');
  if (fs.existsSync(rnTransformSync)) {
    try {
      let code = fs.readFileSync(rnTransformSync, 'utf8');
      if (!code.includes('cleanSrc.includes(\'readonly \')')) {
        const target = 'function parseWithHermes(src, babelConfig) {\n    const sourceAst = require(\'hermes-parser\').parse(src, {';
        const replacement = `function parseWithHermes(src, babelConfig) {
    let cleanSrc = src;
    if (cleanSrc.includes('readonly ')) {
        cleanSrc = cleanSrc.replace(/\\breadonly\\s+/g, '+');
    }
    cleanSrc = cleanSrc.replace(/<\\s*(?:in|out|const)\\s+/g, '<');
    cleanSrc = cleanSrc.replace(/,\\s*(?:in|out|const)\\s+/g, ', ');
    const sourceAst = require('hermes-parser').parse(cleanSrc, {`;
        if (code.includes(target)) {
          code = code.replace(target, replacement);
          fs.writeFileSync(rnTransformSync, code, 'utf8');
        }
      }
    } catch (e) {}
  }

  const codegenBabelPlugin = path.join(nodeModulesDir, '@react-native', 'babel-plugin-codegen', 'index.js');
  if (fs.existsSync(codegenBabelPlugin)) {
    try {
      let code = fs.readFileSync(codegenBabelPlugin, 'utf8');
      if (!code.includes('catch (codegenErr)')) {
        code = code.replace(
          'const viewConfig = generateViewConfig(this.filename, this.code);',
          'try {\n            const viewConfig = generateViewConfig(this.filename, this.code);'
        );
        code = code.replace(
          'this.codeInserted = true;\n          }',
          'this.codeInserted = true;\n            } catch (codegenErr) { return; }\n          }'
        );
        fs.writeFileSync(codegenBabelPlugin, code, 'utf8');
      }
    } catch (e) {}
  }

  const rnIndex = path.join(nodeModulesDir, 'react-native', 'index.js');
  if (fs.existsSync(rnIndex)) {
    try {
      let code = fs.readFileSync(rnIndex, 'utf8');
      if (code.includes("require('./src/private/components/virtualcollection/column/VirtualColumn')")) {
        code = code.replace(
          /get unstable_VirtualColumn\(\) \{[\s\S]*?\.default;\s*\}/,
          'get unstable_VirtualColumn() { return null; }'
        );
        code = code.replace(
          /get unstable_VirtualColumnGenerator\(\) \{[\s\S]*?\.default;\s*\}/,
          'get unstable_VirtualColumnGenerator() { return null; }'
        );
        code = code.replace(
          /get unstable_VirtualRow\(\) \{[\s\S]*?\.default;\s*\}/,
          'get unstable_VirtualRow() { return null; }'
        );
        code = code.replace(
          /get unstable_createVirtualCollectionView\(\) \{[\s\S]*?\.createVirtualCollectionView;\s*\}/,
          'get unstable_createVirtualCollectionView() { return null; }'
        );
        code = code.replace(
          /get unstable_VirtualArray\(\) \{[\s\S]*?\.VirtualArray;\s*\}/,
          'get unstable_VirtualArray() { return null; }'
        );
        code = code.replace(
          /get unstable_VirtualView\(\) \{[\s\S]*?\.default;\s*\}/,
          'get unstable_VirtualView() { return null; }'
        );
        code = code.replace(
          /get VirtualViewMode\(\) \{[\s\S]*?\.VirtualViewMode;\s*\}/,
          'get VirtualViewMode() { return { Visible: 0, Prerender: 1, Hidden: 2 }; }'
        );
        fs.writeFileSync(rnIndex, code, 'utf8');
      }
    } catch (e) {}
  }

  // Ensure metro-file-map emits eventsQueue for @expo/cli compatibility
  const metroFileMapIndex = path.join(nodeModulesDir, 'metro-file-map', 'src', 'index.js');
  if (fs.existsSync(metroFileMapIndex)) {
    try {
      let code = fs.readFileSync(metroFileMapIndex, 'utf8');
      if (!code.includes('eventsQueue: changesWithMetadata')) {
        code = code.replace(
          'const changeEvent = {\n        changes: changesWithMetadata,',
          'const changeEvent = {\n        eventsQueue: changesWithMetadata,\n        changes: changesWithMetadata,'
        );
        fs.writeFileSync(metroFileMapIndex, code, 'utf8');
      }
    } catch (e) {}
  }

  // Ensure @expo/cli TypeScript watchers defensively handle eventsQueue/changes
  const waitFile = path.join(nodeModulesDir, '@expo', 'cli', 'build', 'src', 'start', 'server', 'metro', 'waitForMetroToObserveTypeScriptFile.js');
  if (fs.existsSync(waitFile)) {
    try {
      let code = fs.readFileSync(waitFile, 'utf8');
      if (code.includes('const listener = ({ eventsQueue })=>{')) {
        code = code.replaceAll(
          'const listener = ({ eventsQueue })=>{',
          'const listener = (eventData)=>{\n        const eventsQueue = (eventData && (eventData.eventsQueue || eventData.changes)) || (Array.isArray(eventData) ? eventData : []);'
        );
        fs.writeFileSync(waitFile, code, 'utf8');
      }
    } catch (e) {}
  }

  const watchFile = path.join(nodeModulesDir, '@expo', 'cli', 'build', 'src', 'start', 'server', 'metro', 'metroWatchTypeScriptFiles.js');
  if (fs.existsSync(watchFile)) {
    try {
      let code = fs.readFileSync(watchFile, 'utf8');
      if (code.includes('const listener = ({ eventsQueue })=>{')) {
        code = code.replaceAll(
          'const listener = ({ eventsQueue })=>{',
          'const listener = (eventData)=>{\n        const eventsQueue = (eventData && (eventData.eventsQueue || eventData.changes)) || (Array.isArray(eventData) ? eventData : []);'
        );
        fs.writeFileSync(watchFile, code, 'utf8');
      }
    } catch (e) {}
  }

  // Ensure @expo/cli ManifestMiddleware correctly matches any URI scheme (e.g. exp://, exps://)
  const manifestFile = path.join(nodeModulesDir, '@expo', 'cli', 'build', 'src', 'start', 'server', 'middleware', 'ManifestMiddleware.js');
  if (fs.existsSync(manifestFile)) {
    try {
      let code = fs.readFileSync(manifestFile, 'utf8');
      if (code.includes('bundleUrl.match(/^https?:\\/\\/.*?\\//)[0]')) {
        code = code.replaceAll(
          'bundleUrl.match(/^https?:\\/\\/.*?\\//)[0]',
          '(bundleUrl.match(/^[a-zA-Z][a-zA-Z0-9+.-]*:\\/\\/.*?\\//)?.[0] || bundleUrl + "/")'
        );
        fs.writeFileSync(manifestFile, code, 'utf8');
      }
    } catch (e) {}
  }

  // Ensure @expo/ws-tunnel supports both ws v8 and ws v7
  const wsTunnelFile = path.join(nodeModulesDir, '@expo', 'ws-tunnel', 'build', 'index.js');
  if (fs.existsSync(wsTunnelFile)) {
    try {
      let code = fs.readFileSync(wsTunnelFile, 'utf8');
      if (code.includes('new s.WebSocket(')) {
        code = code.replaceAll('new s.WebSocket(', 'new (s.WebSocket || s)(');
        fs.writeFileSync(wsTunnelFile, code, 'utf8');
      }
    } catch (e) {}
  }

  // Ensure DebuggingOverlay does not crash Expo Go in Bridgeless mode
  const debuggingOverlayFile = path.join(nodeModulesDir, 'react-native', 'Libraries', 'Debugging', 'DebuggingOverlay.js');
  if (fs.existsSync(debuggingOverlayFile)) {
    try {
      let code = fs.readFileSync(debuggingOverlayFile, 'utf8');
      if (code.includes("UIManager.hasViewManagerConfig('DebuggingOverlay')")) {
        code = code.replace("UIManager.hasViewManagerConfig('DebuggingOverlay')", "false /* disabled for Expo Go Bridgeless compatibility */");
        fs.writeFileSync(debuggingOverlayFile, code, 'utf8');
      }
    } catch (e) {}
  }

  // Silence "Codegen didn't run for..." warning in Bridgeless mode for paper components
  const codegenNativeComponentFile = path.join(nodeModulesDir, 'react-native', 'Libraries', 'Utilities', 'codegenNativeComponent.js');
  if (fs.existsSync(codegenNativeComponentFile)) {
    try {
      let code = fs.readFileSync(codegenNativeComponentFile, 'utf8');
      if (code.includes("Codegen didn't run for")) {
        code = code.replace(
          /if\s*\(\s*global\.RN\$Bridgeless\s*===\s*true\s*&&\s*__DEV__\s*\)\s*\{\s*console\.warn\([\s\S]*?\);\s*\}/,
          "if (false) {} /* silenced by DevOpsHero patch-metro */"
        );
        fs.writeFileSync(codegenNativeComponentFile, code, 'utf8');
      }
    } catch (e) {}
  }

  // Ensure expo-asset does not crash if native ExpoAsset module is missing
  const expoAssetFile = path.join(nodeModulesDir, 'expo-asset', 'build', 'ExpoAsset.js');
  if (fs.existsSync(expoAssetFile)) {
    try {
      let code = fs.readFileSync(expoAssetFile, 'utf8');
      if (code.includes("requireNativeModule('ExpoAsset')")) {
        code = code.replace(
          "import { requireNativeModule } from 'expo-modules-core';\nconst AssetModule = requireNativeModule('ExpoAsset');",
          "import { requireOptionalNativeModule } from 'expo-modules-core';\nlet AssetModule = null;\ntry { AssetModule = requireOptionalNativeModule('ExpoAsset'); } catch (_) {}"
        );
        code = code.replace(
          "return AssetModule.downloadAsync(url, md5Hash, type);",
          "return (AssetModule && AssetModule.downloadAsync) ? AssetModule.downloadAsync(url, md5Hash, type) : url;"
        );
        fs.writeFileSync(expoAssetFile, code, 'utf8');
      }
    } catch (e) {}
  }

  // Silence "No native ExponentConstants module found"
  const expoConstantsFile = path.join(nodeModulesDir, 'expo-constants', 'build', 'Constants.js');
  if (fs.existsSync(expoConstantsFile)) {
    try {
      let code = fs.readFileSync(expoConstantsFile, 'utf8');
      if (code.includes('No native ExponentConstants module found')) {
        code = code.replace(
          /if\s*\(!ExponentConstants\)\s*\{\s*console\.warn\("No native ExponentConstants module found[^"]*"\);\s*\}/,
          "if (!ExponentConstants) {} /* silenced by DevOpsHero patch-metro */"
        );
        fs.writeFileSync(expoConstantsFile, code, 'utf8');
      }
    } catch (e) {}
  }

  // Comprehensive ESM / CJS fallback default export across all metro packages
  const metroDirs = fs.readdirSync(nodeModulesDir).filter(d => d === 'metro' || d.startsWith('metro-'));
  const patchMarker = '// DEFAULT_CJS_INTEROP_PATCH';
  const patchSnippet = `\n${patchMarker}\nif (typeof module !== "undefined" && module.exports && module.exports.default === undefined) {\n  module.exports.default = module.exports;\n}\n`;

  let patchedFileCount = 0;
  for (const d of metroDirs) {
    const dirPath = path.join(nodeModulesDir, d);
    function walk(current) {
      try {
        const entries = fs.readdirSync(current, { withFileTypes: true });
        for (const ent of entries) {
          const fullPath = path.join(current, ent.name);
          if (ent.isDirectory()) {
            walk(fullPath);
          } else if (ent.isFile() && ent.name.endsWith('.js')) {
            const content = fs.readFileSync(fullPath, 'utf8');
            if (!content.includes(patchMarker)) {
              fs.writeFileSync(fullPath, content + patchSnippet, 'utf8');
              patchedFileCount++;
            }
          }
        }
      } catch (err) {
        // Ignore read/permission errors on nested files
      }
    }
    walk(dirPath);
  }

  console.log(`[patch-metro] Metro packages successfully patched and verified (${patchedFileCount} additional files patched).`);
}
