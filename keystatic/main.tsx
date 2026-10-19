import React from 'react';
import ReactDOM from 'react-dom/client';
import { Keystatic } from '@keystatic/core/ui';
import config from '../keystatic.config';

// Keystatic's internal client router strictly splits `pathname` by '/' and checks
// exact match without trailing slash (e.g. `params.join('/') === 'cloud/oauth/callback'`).
// If a trailing slash exists (due to browser caches or web server rewrites), strip it
// immediately via replaceState before Keystatic initializes.
if (
  window.location.pathname.length > 1 &&
  window.location.pathname.endsWith('/') &&
  window.location.pathname.startsWith('/keystatic/')
) {
  const cleanPath = window.location.pathname.replace(/\/+$/, '');
  const newUrl = cleanPath + window.location.search + window.location.hash;
  window.history.replaceState(null, '', newUrl);
}

const root = document.getElementById('root');
if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <Keystatic config={config} />
    </React.StrictMode>
  );
}

