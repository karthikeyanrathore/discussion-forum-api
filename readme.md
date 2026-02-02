# Discussion Forum API

A production‑ready **RESTful backend service** for powering community discussion platforms. It supports user authentication, threaded discussions, replies, reactions, tags, and social interactions such as following users. The API is designed to be **modular**, **scalable**, and easy to integrate with any frontend.


## Architecture Overview

The system follows a clean separation of concerns between authentication, discussion management, and social interactions. Below is the high‑level database and domain model:

![Database UML](./static/dbdiagram_UML.png)


## Features

- User registration and authentication
- Create, read, update, and delete discussion posts
- Threaded comments and nested replies
- Like / react to posts
- Tag‑based post discovery and search
- Follow other users
- Dockerized setup for local and offline development

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Run the service locally

If you face any issues, feel free to contact: **karthikerathore@gmail.com**

```bash
1. Remove old containers and volumes
docker-compose down -v --remove-orphans
docker-compose -f docker-compose-offline.yml down -v --remove-orphans

2. Build all services
docker-compose -f docker-compose-offline.yml build

3. Run services
docker-compose -f docker-compose-offline.yml up
```

## API Usage Examples

Below are example API interactions demonstrating common user flows.

### 1. Register user

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/86157e6b-a3d8-422e-b3b8-9b23bd0f2ee1)


### 2. Login user

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/9f71084f-8d1e-4b8e-8e42-b3223c2c6343)


### 3. Create a discussion post with tags

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/ce752d19-14d7-439a-87f7-cafc6d6f7c77)


### 4. Add a comment to a post
   
![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/537ebc34-555f-4797-b518-0b0f7c12a07a)


### 5. Like a post

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/0ab8a6f1-e52b-4609-9f59-96198dc45f7b)


### 6. Reply to a comment

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/49a3bf62-321d-4dd4-9893-eebf3dc7aef4)

### 7. Get details about a post

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/2544fbf4-c56b-4577-8cfc-f77ca621e2e2)


### 8. Search for posts via tags

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/494155d9-4d2e-4093-8b20-84b36c34c0d4)


### 9. Follow other users

---

## Notes

- This repository focuses on the **backend API** only.
- It can be paired with any web or mobile frontend.
- Designed to be extended with moderation, notifications, and analytics features.

![image](https://github.com/karthikeyanrathore/discussion-forum/assets/53295316/ca37f42a-5995-4fa7-a57d-a5324c8c8b58)
