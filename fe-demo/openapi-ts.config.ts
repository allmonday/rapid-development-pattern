import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8001/openapi.json', // sign up at app.heyapi.dev
  output: {
    fileName: {
      suffix: '.gen',
    },
    path: 'src/sdk',
    header: ['// @ts-nocheck'],
  },
  plugins: [
    '@hey-api/client-fetch',
    '@hey-api/typescript',
    {
      name: '@hey-api/sdk',
      asClass: true,
    },
  ],
});
