// Temporary module declarations to satisfy TypeScript while dependencies are not installed
// Install proper react/react-dom packages and their types to remove these.

declare module 'react';
declare module 'react/jsx-runtime';

// minimal JSX namespace to avoid intrinsic element errors
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
