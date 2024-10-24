docker run -d -p 6379:6379 --name redis redis
docker run -d --name mongodb -v push_mongo:/data/db -p 27017:27017 mongo
celery -A config worker --pool=solo --loglevel=debug windows