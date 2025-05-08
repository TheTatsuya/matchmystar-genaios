# GenAi Frontend

A React-based frontend application built with Vite, TypeScript, and Material-UI.

## Tech Stack

- React 18
- TypeScript
- Vite
- Material-UI (MUI)
- TailwindCSS
- React Router
- React Flow

## Prerequisites

- [Node.js](https://nodejs.org/en/download/) (LTS version recommended)
- npm (comes with Node.js)

## Environment Variables

The following environment variables are required for the application:

- `VITE_API_URL`: The base URL for the API endpoints
- `VITE_WS_URL`: WebSocket URL for real-time features

Create a `.env` file in the root directory with these variables:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```
More details check here - [Vite Env Variables and Modes](https://vite.dev/guide/env-and-mode)

## Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Production

### Building

To build the application for production:

```bash
npm run build
```

The build output will be in the `dist` directory.

### Running in Production

1. Using npm:
   ```bash
   npm run prod
   ```

2. Using Docker:
   ```bash
   docker build -t magic-patterns-frontend .
   docker run -p 5173:5173 magic-patterns-frontend
   ```

## Testing

Run the test suite:

```bash
npm test
```

## Available Scripts

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
- `npm run prod`: Build and preview production build
- `npm run lint`: Run ESLint
- `npm test`: Run Jest tests

## Project Structure

- `src/`: Source code directory
  - `components/`: Reusable React components
  - `pages/`: Page components
  - `services/`: API and service functions
  - `types/`: TypeScript type definitions
  - `utils/`: Utility functions
  - `App.tsx`: Main application component
  - `main.tsx`: Application entry point

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests and linting
4. Submit a pull request
