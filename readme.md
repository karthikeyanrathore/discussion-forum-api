## discussion forum

## UML
![image info](./static/dbdiagram_UML.png)


## How to spin up service?

```bash
1. remove old orphans
docker-compose down -v --remove-orphans; docker-compose -f  docker-compose-offline.yml down -v --remove-orphans;

2. build all services
docker-compose -f docker-compose-offline.yml build

3. run services
docker-compose -f docker-compose-offline.yml up
```