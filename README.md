# Хранилища и Базы данных - Лабораторная 1

## Полезные ссылки
[Задание](./docs/Заданька.pdf)

### Как запустить?
1. `cd docker`
2. `docker-compose up`
3. PostgreSQL, MongoDB автоматически запустит скрипты, для заполнения БД.
4. Входим в airflow по адресу `localhost:8080` логин/пароль: `airflow`/`airflow`.
5. Заходим во вкладку DAGs и смотрим как они работают.

### Данные для подключения
#### PostgreSQL
+ Login: `postgres`
+ Password: `postgres`
+ DataBase: `postgres`
+ Port: `5432`

#### MongoDB
+ Login: `root`
+ Password: `root`
+ DataBase: `mydatabase`
+ Port: `27017`

#### AirFlow
+ Login: `airflow`
+ Password: `airflow`
+ URL: http://localhost:8080