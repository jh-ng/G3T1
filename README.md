# G3T1 Travel Planner

## Getting Started

### Frontend Setup
1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

### Backend Setup
1. Make sure Docker Desktop is running
2. From the root directory, start the backend services:
```bash
docker-compose up -d --build
```

## Integrated Application Architecture

The application consists of a Vue.js frontend and multiple microservices backend with a Kong API gateway:

- **Frontend**: Single Vue.js application with travel planning features and AI-powered itinerary generation
- **Backend Services**:
  - **AI Microservice**: Generates travel itineraries using AI
  - **Location Service**: Provides place information and recommendations
  - **User Service**: Manages user profiles and preferences
  - **Auth Service**: Handles authentication and authorization
  - **Post Service**: Manages user posts and shared itineraries
- **Kong API Gateway**: Routes API requests to appropriate microservices

### Environment Variables
The frontend uses a `.env` file containing API keys. Current environment variables include:
- `VUE_APP_GEOAPIFY_API_KEY`: API key for Geoapify location autocomplete service

### Main Application Features
- Travel itinerary planning with AI assistance
- Location search with autocomplete
- User authentication
- Sharing travel plans

## Docker Commands Guide

### Basic Commands

#### Start Services
```bash
# Start all services in detached mode (run in background)
docker-compose up -d

# Start and rebuild all services
docker-compose up -d --build

# Start specific service
docker-compose up -d post-service
```

**What is detached mode (-d)?**
- Runs containers in the background
- Terminal remains available for other commands
- Logs won't show in terminal (use docker-compose logs to view them)
- Services keep running even if you close the terminal

#### Stop Services
```bash
# Stop all services but keep data
docker-compose down

# Stop all services and delete all data
docker-compose down -v
```

#### View Logs
```bash
# View logs of all services
docker-compose logs

# View logs of specific service
docker-compose logs post-service

# Follow logs in real-time
docker-compose logs -f
```

### Data Management

#### Fresh Start (Reset Everything)
```bash
# Remove everything including databases
docker-compose down -v

# Rebuild and start fresh
docker-compose up -d --build
```

#### Update Code Without Losing Data
```bash
# Rebuild specific service
docker-compose up -d --build post-service

# Rebuild all services
docker-compose up -d --build
```

#### Development Workflow
1. First time setup:
```bash
docker-compose up -d --build
```

2. Regular development (preserve data):
```bash
# Stop services
docker-compose down

# Start services
docker-compose up -d
```

3. After code changes:
```bash
docker-compose up -d --build
```
