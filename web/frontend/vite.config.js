import fs from 'node:fs/promises';
import path from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const extractCharset = (htmlBuffer) => {
  const headChunk = htmlBuffer.subarray(0, 4096).toString('latin1');
  const directCharset = headChunk.match(/<meta[^>]+charset=["']?\s*([^"'>\s/]+)/i)?.[1];
  const httpEquivCharset = headChunk.match(/charset=([^"'>\s;]+)/i)?.[1];

  return (directCharset || httpEquivCharset || 'utf-8').toLowerCase();
};

const decodeHtml = (htmlBuffer) => {
  try {
    return new TextDecoder(extractCharset(htmlBuffer)).decode(htmlBuffer);
  } catch {
    return new TextDecoder('utf-8').decode(htmlBuffer);
  }
};

const extractTitle = (htmlContent, fileName) => {
  const title = htmlContent.match(/<title>([\s\S]*?)<\/title>/i)?.[1];
  const normalizedTitle = title?.replace(/\s+/g, ' ').trim();

  return normalizedTitle || fileName.replace(/\.html$/i, '');
};

const extractMetaContent = (htmlContent, metaName) => {
  const escapedMetaName = metaName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const nameFirstPattern = new RegExp(
    `<meta[^>]*name=["']${escapedMetaName}["'][^>]*content=["']([^"']*)["'][^>]*>`,
    'i'
  );
  const contentFirstPattern = new RegExp(
    `<meta[^>]*content=["']([^"']*)["'][^>]*name=["']${escapedMetaName}["'][^>]*>`,
    'i'
  );

  return (
    htmlContent.match(nameFirstPattern)?.[1]?.trim() ||
    htmlContent.match(contentFirstPattern)?.[1]?.trim() ||
    null
  );
};

const readHtmlTaskManifest = async (rootDir) => {
  const htmlTaskDir = path.resolve(rootDir, 'html_task');
  const htmlFiles = await fs
    .readdir(htmlTaskDir)
    .then((fileNames) =>
      fileNames
        .filter((fileName) => fileName.toLowerCase().endsWith('.html'))
        .sort((firstFile, secondFile) => firstFile.localeCompare(secondFile, 'ru'))
    )
    .catch(() => []);

  return Promise.all(
    htmlFiles.map(async (fileName) => {
      const filePath = path.resolve(htmlTaskDir, fileName);
      const htmlBuffer = await fs.readFile(filePath);
      const htmlContent = decodeHtml(htmlBuffer);

      return {
        id: fileName.replace(/\.html$/i, ''),
        fileName,
        title: extractTitle(htmlContent, fileName),
        author: extractMetaContent(htmlContent, 'development-author'),
      };
    })
  );
};

const writeHtmlTaskManifest = async (targetDir, manifest) => {
  await fs.mkdir(targetDir, { recursive: true });
  await fs.writeFile(
    path.resolve(targetDir, 'manifest.json'),
    JSON.stringify(manifest, null, 2),
    'utf-8'
  );
};

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

      server.middlewares.use('/html_task/manifest.json', async (_req, res, next) => {
        try {
          const manifest = await readHtmlTaskManifest(rootDir);

          res.statusCode = 200;
          res.setHeader('Content-Type', 'application/json; charset=utf-8');
          res.setHeader('Cache-Control', 'no-store');
          res.end(JSON.stringify(manifest));
        } catch (error) {
          return next(error);
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
      const manifest = await readHtmlTaskManifest(rootDir);

      await fs.rm(outputHtmlTaskDir, { recursive: true, force: true });
      await fs.mkdir(outputHtmlTaskDir, { recursive: true });
      await writeHtmlTaskManifest(outputHtmlTaskDir, manifest);

      const htmlFiles = await fs
        .readdir(htmlTaskDir)
        .then((fileNames) => fileNames.filter((fileName) => fileName.toLowerCase().endsWith('.html')))
        .catch(() => []);

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

