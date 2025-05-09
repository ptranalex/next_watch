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
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

***REMOVED*** Build the Next.js application
RUN pnpm build

***REMOVED*** Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

***REMOVED*** Create a non-root user for better security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

***REMOVED*** Set permissions
RUN mkdir -p /app && chown -R nextjs:nodejs /app

***REMOVED*** Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

***REMOVED*** Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

***REMOVED*** Use the non-root user
USER nextjs

***REMOVED*** Expose the port
EXPOSE 3000

***REMOVED*** Start the application
CMD ["node", "server.js"] 