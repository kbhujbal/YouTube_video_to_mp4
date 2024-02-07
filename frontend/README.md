# YouTube Downloader Frontend

Next.js frontend for YouTube video downloading service.

## Setup

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Run development server:
```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build for Production

```bash
npm run build
npm start
```

## Configuration

The backend API URL is configured in `app/page.tsx`:
```typescript
const API_BASE_URL = 'http://localhost:8000'
```

Change this if your backend is running on a different port or domain.
