# syntax = docker/dockerfile:1

# Adjust NODE_VERSION as desired
ARG NODE_VERSION=20.18.0
FROM node:${NODE_VERSION}-slim as base

WORKDIR /app

# --- Build stage ---
FROM base as build

# Accept build arguments
ARG VITE_SERVER_URL
ARG VITE_RECIPIENT_URL

# Set environment variables from build args
ENV VITE_SERVER_URL=$VITE_SERVER_URL
ENV VITE_RECIPIENT_URL=$VITE_RECIPIENT_URL

# Install dependencies including devDependencies
COPY ["package.json", "package-lock.json*", "./"]
# Install all dependencies (including devDependencies) for building
RUN npm install --include=dev

# Copy source
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM base

# Install serve globally
RUN npm install -g serve

# Copy built files from build stage
COPY --from=build /app/dist /app/dist

# Create serve.json config for SPA routing
RUN echo '{"public": "dist", "rewrites": [{"source": "**", "destination": "/index.html"}]}' > /app/serve.json

WORKDIR /app

# Expose port 8080
EXPOSE 8080

# Start the server with config file
CMD ["serve", "-c", "serve.json", "-l", "8080"]
