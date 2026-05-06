FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS dev
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
EXPOSE 3001
CMD ["npm", "start", "--", "--port", "3001", "--host", "0.0.0.0"]

FROM deps AS builder
COPY . .
RUN npm run build

FROM nginx:alpine AS runner
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
