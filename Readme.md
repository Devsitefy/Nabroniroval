docker network create myNetwork

docker run --name booking_db \
    -p 6432:5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=12hjkdfvsjkhjksdhkjfghsbm34 \
    -e POSTGRES_DB=booking \
    --network=myNetwork \
    --volume pg-booking-data:/var/lib/postgresql/data \
    -d postgres:17 



docker run --name booking_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis:latest 


docker run --name booking_back \
    -p 7777:8000 \
    --network=myNetwork \
    -v "$(pwd)/src/static/images:/app/src/static/images" \
    booking_image

docker run --name booking_celery \
    --network=myNetwork \
    -v "$(pwd)/src/static/images:/app/src/static/images" \
    booking_image \
    celery -A src.tasks.celery_app:celery_instance worker --loglevel=info

docker run --name booking_beat \
    --network=myNetwork \
    booking_image \
    celery -A src.tasks.celery_app:celery_instance worker --loglevel=info -B


docker build -t booking_image .





git config user.name "alexandr konoplev"
git config user.email "viloni34@gmail.com"

git remote add gitlab git@gitlab.com:none8643745/booking.git



docker run --name booking_nginx \
    -v ./nginx.conf:/etc/nginx/nginx.conf \
    --network=myNetwork \
    --rm -p 80:80 nginx
