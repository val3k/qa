# qa
tg: https://t.me/Va1entin

qa service 

## Развертывание:
1. Создаем minio(S3)
2. Заполняем .env
3. Подкладываем исходные файлы индекса и эбеддингов для cutter на машину, где он будет развернут
4. Развертываем cutter:
`docker-compose up -f docker-compose-cutter.yml`
5. Создаем задание на "нарезку" индексов и эмбеддингов в s3 с указанием версии данных (version), например 1:
`curl localhost:6000/build?version=1`
6. Указываем версию данных в .env (IND_PATH..., CENT_PATH)
7. Собираем компоуз для индксов и gateway:
`docker-compose build`
8. Пушим в реджистри 
`docker-compose push`
9. Разворачиваем gateway и индексы
`docker stack deploy --compose-file docker-compose.yml qaservice`

## Обновление:
1. Создаем задание для cutter на "нарезку" индексов и эмбеддингов в s3 с указанием версии данных (version), например 2:
`curl localhost:6000/build?version=2`
2. Указываем новую версию данных в .env (IND_PATH..., CENT_PATH)
3. Обновляем сервис
`docker stack deploy --compose-file docker-compose.yml qaservice`

## Схема сервиса

![alt text](https://github.com/val3k/qa/blob/main/qa.jpg)
