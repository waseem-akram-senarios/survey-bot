# syntax = docker/dockerfile:1

# Adjust NODE_VERSION as desired
ARG NODE_VERSION=20.18.0
FROM node:${NODE_VERSION}-slim as base

WORKDIR /app
ENV NODE_ENV="production"

# --- Build stage ---
FROM base as build

# Accept build arguments
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Install required build tools
RUN apt-get update -qq && \
    apt-get install -y build-essential pkg-config python-is-python3

# Install deps
COPY ["package.json", "pnpm-lock.yaml*", "package-lock.json*", "yarn.lock*", "./"]
RUN npm install -g pnpm
RUN pnpm install

# Copy source
COPY . .

# Build Next.js app
RUN pnpm build

# --- Production stage ---
FROM base

# Only copy necessary files from build
COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json

EXPOSE 3000

# Start production server
CMD ["npm", "start"]

