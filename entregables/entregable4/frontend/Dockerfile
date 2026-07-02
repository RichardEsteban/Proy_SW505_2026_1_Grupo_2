FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --registry=https://registry.npmjs.org/ --no-audit --no-fund

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
