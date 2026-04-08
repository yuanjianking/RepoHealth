# RepoHealth Frontend

A modern, interactive dashboard for monitoring GitHub repository health and development metrics.

## Overview

RepoHealth Frontend is a React-based dashboard application that provides real-time insights into GitHub repository health, code quality, team collaboration, milestone tracking, and risk analysis. It connects to a backend API to fetch and visualize repository metrics in an intuitive interface.

## Features

- **📊 Health Overview**: Overall project health score with key metrics visualization
- **💻 Code Health Analysis**: Code quality metrics including unmerged PRs, commit frequency, and code distribution
- **👥 Team Collaboration**: Team member contributions, task balance, and delay rate analysis
- **📅 Milestone Tracking**: Plan vs. actual progress tracking with timeline visualization
- **⚠️ Risk Analysis**: Risk identification and severity assessment
- **🔄 Real-time Updates**: Automatic data refresh and synchronization
- **🎨 Responsive Design**: Fully responsive UI that works on desktop and mobile
- **🌓 Modern UI**: Clean, intuitive interface built with Ant Design

## Tech Stack

- **Frontend Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **UI Library**: Ant Design 5
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Testing**: Vitest, React Testing Library
- **Code Quality**: ESLint, Prettier, Husky
- **Styling**: CSS Modules

## Getting Started

### Prerequisites

- Node.js 18+ (20.19+ recommended for Vite)
- npm 9+ or yarn 1.22+
- Backend API service running (see backend setup)

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd repohealth/frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Configure environment variables:

   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your API endpoint
   ```

4. Start the development server:

   ```bash
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:5173`

### Environment Variables

Create a `.env.local` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
# Add other environment variables as needed
```

## Project Structure

```
src/
├── components/           # React components
│   ├── layout/          # Layout components (Header, etc.)
│   ├── overview/        # Health overview components
│   ├── code/            # Code health components
│   ├── team/            # Team work components
│   ├── risk/            # Risk analysis components
│   └── index.ts         # Component exports
├── pages/               # Page components
├── services/            # API services
├── stores/              # Zustand state management
├── utils/               # Utility functions
├── test/                # Test setup files
├── App.tsx              # Main App component
└── main.tsx             # Application entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting

## Testing

The project uses Vitest and React Testing Library for comprehensive testing:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

## Code Quality

- **ESLint**: Code linting with TypeScript support
- **Prettier**: Code formatting
- **Husky**: Git hooks for pre-commit linting
- **lint-staged**: Run linters on staged files

Pre-commit hooks automatically run linting and formatting checks.

## API Integration

The frontend communicates with the RepoHealth backend API. Key API endpoints include:

- `GET /repo/health/{owner}/{repo}` - Repository health overview
- `GET /repo/code-health/{owner}/{repo}` - Code health metrics
- `GET /repo/team-work/{owner}/{repo}` - Team collaboration data
- `GET /repo/risk-analysis/{owner}/{repo}` - Risk analysis

See the [API documentation](backend-api-docs-url) for complete details.

## Development

### Adding New Components

1. Create component in appropriate directory under `src/components/`
2. Export component in `src/components/index.ts`
3. Add TypeScript interfaces for props
4. Write tests in `[component].test.tsx`
5. Add CSS styles in `[component].css`

### State Management

The project uses Zustand for state management:

- **Dashboard Store** (`src/stores/dashboardStore.ts`): Manages dashboard state, repository selection, and API data fetching
- Stores are persisted to localStorage for user preferences

### Styling

- Use CSS Modules for component-specific styles
- Ant Design components for consistent UI
- Custom CSS for layout and custom components

## Deployment

### Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory, ready for deployment to any static hosting service.

### Deployment Options

- **Vercel**: Automatic deployments from Git
- **Netlify**: Static site hosting
- **GitHub Pages**: Free hosting for open source projects
- **Docker**: Containerized deployment (see Dockerfile)

### Docker Deployment

Build the Docker image:

```bash
docker build -t repohealth-frontend .
```

Run the container:

```bash
docker run -p 3000:80 repohealth-frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

1. Run tests before committing: `npm test`
2. Ensure code passes linting: `npm run lint`
3. Format code: `npm run format`
4. Update tests for new functionality
5. Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, questions, or feature requests:

- Open an issue on GitHub
- Check the [documentation](docs-url)
- Contact the development team

## Acknowledgments

- Built with [Vite](https://vitejs.dev/)
- UI components from [Ant Design](https://ant.design/)
- Charts by [Recharts](https://recharts.org/)
- State management with [Zustand](https://zustand-demo.pmnd.rs/)
- Testing with [Vitest](https://vitest.dev/)
