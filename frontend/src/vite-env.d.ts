/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_ERROR_REPORT_EMAIL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

