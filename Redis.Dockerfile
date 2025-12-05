FROM redis:8.2.3-alpine

EXPOSE 6379

CMD [ "redis-server" ]