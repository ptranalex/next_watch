***REMOVED*** Production Dockerfile for Next.js
***REMOVED*** Uses multi-stage build for optimized production image

ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine AS base

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

***REMOVED*** Install dependencies only when needed
FROM base AS deps
WORKDIR /app

***REMOVED*** Install additional build dependencies
RUN apk add --no-cache python3 make g++

***REMOVED*** Copy package.json, pnpm-lock.yaml and npmrc
COPY apps/web-nextjs/package.json .
COPY apps/web-nextjs/pnpm-lock.yaml .
COPY apps/web-nextjs/.npmrc .

***REMOVED*** Install dependencies
RUN pnpm install --frozen-lockfile

***REMOVED*** Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

***REMOVED*** Accept build arguments for environment variables - no default to ensure it's explicitly set
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_BFF_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_BFF_API_URL=${NEXT_PUBLIC_BFF_API_URL}

***REMOVED*** Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY apps/web-nextjs/package.json .
COPY apps/web-nextjs/pnpm-lock.yaml .
COPY apps/web-nextjs/.npmrc .

***REMOVED*** Copy app source files
COPY apps/web-nextjs/next.config.js .
COPY apps/web-nextjs/tsconfig.json .
COPY apps/web-nextjs/.eslintrc.json .
COPY apps/web-nextjs/next-env.d.ts .
COPY apps/web-nextjs/src ./src
COPY apps/web-nextjs/public ./public

***REMOVED*** Set environment variables
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

***REMOVED*** Display build information for verification
RUN echo "Building with NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}"
RUN echo "Building with NEXT_PUBLIC_BFF_API_URL=${NEXT_PUBLIC_BFF_API_URL}"

***REMOVED*** Build the Next.js application with standalone output
RUN pnpm build

***REMOVED*** Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

***REMOVED*** Install curl for health checks - before changing user
RUN apk add --no-cache curl net-tools

***REMOVED*** Create a non-root user for better security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

***REMOVED*** Set permissions
RUN mkdir -p /app && chown -R nextjs:nodejs /app

***REMOVED*** Pass the API URL to the runtime environment
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_BFF_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_BFF_API_URL=${NEXT_PUBLIC_BFF_API_URL}
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

***REMOVED*** Display runtime configuration
RUN echo "Runtime NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}"
RUN echo "Runtime NEXT_PUBLIC_BFF_API_URL=${NEXT_PUBLIC_BFF_API_URL}"

***REMOVED*** Copy built application - using standalone mode for smaller image
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

***REMOVED*** Use the non-root user
USER nextjs

***REMOVED*** Expose the port
EXPOSE 3000

***REMOVED*** Add health check configuration - use container's IP with curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD IP=$(hostname -i) && curl --fail --max-time 5 --connect-timeout 5 http://$IP:3000/ || exit 1

***REMOVED*** Start the application in standalone mode
ENV HOST=0.0.0.0
ENV PORT=3000
CMD ["node", "server.js"]