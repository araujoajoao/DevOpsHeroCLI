// Filter out React Native Bridgeless / Fabric Codegen runtime warnings
const _origWarn = console.warn;
console.warn = (...args: any[]) => {
  const msg = args[0];
  if (
    typeof msg === 'string' &&
    (msg.includes("Codegen didn't run for") ||
      msg.includes('Cannot record touch') ||
      msg.includes('View config not found for component') ||
      msg.includes('No native ExponentConstants module found'))
  ) {
    return;
  }
  _origWarn.apply(console, args);
};

import React from 'react';
import { registerRootComponent } from 'expo';

import App from './App';
import { ErrorBoundary } from './src/components/ErrorBoundary';

function Root() {
  return React.createElement(ErrorBoundary, null, React.createElement(App));
}

registerRootComponent(Root);
