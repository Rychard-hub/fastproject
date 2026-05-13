# Stage 1: Build React app
FROM node:22 AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve React app with Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Use default nginx config
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
