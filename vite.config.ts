import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],base:process.env.VITE_BASE_PATH || './',build:{chunkSizeWarningLimit:700,rollupOptions:{output:{manualChunks:{charts:['echarts'],react:['react','react-dom']}}}}});
