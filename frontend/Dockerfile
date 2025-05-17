FROM node:18-alpine

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем исходники
COPY . .

# Открываем порт
EXPOSE 3000

# Запускаем приложение
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]