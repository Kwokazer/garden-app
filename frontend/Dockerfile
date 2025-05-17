# Этап сборки
FROM node:18-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Убедитесь, что команда сборки в вашем package.json называется 'build'
RUN npm run build

# Этап запуска
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Использование нашей конфигурации Nginx для корректной работы Vue Router
COPY nginx.conf /etc/nginx/conf.d/default.conf 
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]