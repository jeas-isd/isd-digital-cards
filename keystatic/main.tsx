import React from 'react';
import ReactDOM from 'react-dom/client';
import { Keystatic } from '@keystatic/core/ui';
import config from '../keystatic.config';

const root = document.getElementById('root');
if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <Keystatic config={config} />
    </React.StrictMode>
  );
}
