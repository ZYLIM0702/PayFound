import {existsSync} from 'node:fs';
import {fileURLToPath,URL} from 'node:url';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import {defineConfig} from 'vite';

// Same rule as the API (apps/api/app/config.py): inside the development workspace, read the one shared .env.
// Vite only exposes VITE_ values to the browser, so the server keys in that file never reach the bundle.
const workspace=fileURLToPath(new URL('../../..',import.meta.url));

export default defineConfig({
 envDir:existsSync(workspace+'/opencode.json')?workspace:undefined,
 plugins:[react(),tailwindcss()],
 resolve:{alias:{'@':fileURLToPath(new URL('./src',import.meta.url))}},
 server:{host:'127.0.0.1',port:5173,proxy:{'/api':'http://127.0.0.1:8000'}},
 optimizeDeps:{include:['@bryntum/calendar','@bryntum/calendar-react']}
});
