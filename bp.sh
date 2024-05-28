# تثبيت Docker على جهازك
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# إنشاء Dockerfile لتشغيل مشروعك
echo '
FROM node:latest
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
CMD [ "node", "bot2.js" ]
' > Dockerfile

# بناء الصورة وتشغيل الحاوية
docker build -t my-node-app .
docker run -d -p 3000:3000 my-node-app

