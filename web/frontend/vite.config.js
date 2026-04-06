import fs from 'node:fs/promises';
import path from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const listHtmlFiles = async (htmlTaskDir) =>
  fs
    .readdir(htmlTaskDir)
    .then((fileNames) =>
      fileNames
        .filter((fileName) => fileName.toLowerCase().endsWith('.html'))
        .sort((firstFile, secondFile) => firstFile.localeCompare(secondFile, 'ru'))
    )
    .catch(() => []);

const isSafeHtmlTaskPath = (htmlTaskDir, requestedPath) => {
  const resolvedPath = path.resolve(htmlTaskDir, requestedPath);
  const relativePath = path.relative(htmlTaskDir, resolvedPath);

  return (
    relativePath &&
    !relativePath.startsWith('..') &&
    !path.isAbsolute(relativePath) &&
    resolvedPath.toLowerCase().endsWith('.html')
  );
};

const htmlTaskPlugin = () => {
  let rootDir = '';
  let buildOutDir = '';

  return {
    name: 'html-task-plugin',
    configResolved(config) {
      rootDir = config.root;
      buildOutDir = path.resolve(rootDir, config.build.outDir);
    },
    configureServer(server) {
      const htmlTaskDir = path.resolve(rootDir, 'html_task');
      const reloadClients = () => {
        server.ws.send({ type: 'full-reload', path: '*' });
      };

      server.watcher.add(htmlTaskDir);
      server.watcher.on('add', (filePath) => {
        if (filePath.startsWith(htmlTaskDir) && filePath.toLowerCase().endsWith('.html')) {
          reloadClients();
        }
      });
      server.watcher.on('unlink', (filePath) => {
        if (filePath.startsWith(htmlTaskDir) && filePath.toLowerCase().endsWith('.html')) {
          reloadClients();
        }
      });
      server.watcher.on('change', (filePath) => {
        if (filePath.startsWith(htmlTaskDir) && filePath.toLowerCase().endsWith('.html')) {
          reloadClients();
        }
      });

      server.middlewares.use('/html_task', async (req, res, next) => {
        try {
          const requestedPath = decodeURIComponent((req.url || '/').split('?')[0]).replace(/^\/+/, '');

          if (!requestedPath || !isSafeHtmlTaskPath(htmlTaskDir, requestedPath)) {
            return next();
          }

          const filePath = path.resolve(htmlTaskDir, requestedPath);
          const htmlBuffer = await fs.readFile(filePath);

          res.statusCode = 200;
          res.setHeader('Content-Type', 'text/html');
          res.end(htmlBuffer);
        } catch (error) {
          if (error?.code === 'ENOENT') {
            return next();
          }

          return next(error);
        }
      });
    },
    async writeBundle() {
      const htmlTaskDir = path.resolve(rootDir, 'html_task');
      const outputHtmlTaskDir = path.resolve(buildOutDir, 'html_task');

      await fs.rm(outputHtmlTaskDir, { recursive: true, force: true });
      await fs.mkdir(outputHtmlTaskDir, { recursive: true });
      const htmlFiles = await listHtmlFiles(htmlTaskDir);

      await Promise.all(
        htmlFiles.map((fileName) =>
          fs.copyFile(
            path.resolve(htmlTaskDir, fileName),
            path.resolve(outputHtmlTaskDir, fileName)
          )
        )
      );
    },
  };
};

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), htmlTaskPlugin()],
  server: {
    port: 3002,
    proxy: {
      '/api': {
        target: 'http://localhost:8002', //'http://backend:8002',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
  },
});

