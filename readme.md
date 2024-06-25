## discussion forum

## UML
![image info](./static/dbdiagram_UML.png)


## How to spin up service?

if you face any issue write me at karthikerathore@gmail.com
```bash
1. remove old orphans
docker-compose down -v --remove-orphans; docker-compose -f  docker-compose-offline.yml down -v --remove-orphans;

2. build all services
docker-compose -f docker-compose-offline.yml build

3. run services
docker-compose -f docker-compose-offline.yml up
```

## examples

1. register user

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/86157e6b-a3d8-422e-b3b8-9b23bd0f2ee1)


2. Login user

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/9f71084f-8d1e-4b8e-8e42-b3223c2c6343)


3. create discussion post with tags :D

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/ce752d19-14d7-439a-87f7-cafc6d6f7c77)


4. add a comment to post
   
![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/537ebc34-555f-4797-b518-0b0f7c12a07a)


5. like a post

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/0ab8a6f1-e52b-4609-9f59-96198dc45f7b)


6. reply to comment

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/49a3bf62-321d-4dd4-9893-eebf3dc7aef4)

7.  get detalils about post

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/2544fbf4-c56b-4577-8cfc-f77ca621e2e2)


8. search for post via tags

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/494155d9-4d2e-4093-8b20-84b36c34c0d4)


9. follow other users

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/ca37f42a-5995-4fa7-a57d-a5324c8c8b58)

