# Discussion Forum API

A production-ready **RESTful backend service** designed for powering community discussion platforms. This API supports user authentication, threaded discussions, reactions, and social features such as following users. Its modular and scalable design ensures easy integration with any web or mobile frontend.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [API Design](#api-design)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Notes](#notes)

## Overview

The Discussion Forum API provides a robust and secure backend for community-driven platforms. Designed with industry best practices in mind, it leverages a resource-oriented REST API to deliver efficient and predictable operations.

## Features

- **User Management:** Registration, authentication, and user profiles.
- **Discussion Management:** Create, read, update, and delete discussion posts.
- **Threaded Conversations:** Support for comments and nested replies.
- **Reactions:** Ability to like and react to posts.
- **Tagging:** Tag-based filtering and search.
- **Social Interactions:** Follow other users.
- **Containerized Deployment:** Dockerized setup for local and offline development.

## API Design

The API is constructed with clarity and consistency in mind:

- **Resource-Oriented Structure:** Predictable endpoints for users, posts, comments, tags, and reactions.
- **Authentication:** Token-based authentication via HTTP headers (e.g., `Authorization: Bearer <token>`).
- **Scalability:** Built-in pagination and filtering options for handling large datasets.
- **Client-Agnostic:** Easily documented or extended using OpenAPI/Swagger.

## Architecture

The service leverages a clean separation of concerns across its core components: authentication, discussion management, and social interactions. The high-level domain and database model is illustrated below:

![Database UML](./static/dbdiagram_UML.png)

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running Locally

To launch the service locally, execute the following commands:

```bash
# Remove old containers and volumes
docker-compose down -v --remove-orphans
docker-compose -f docker-compose-offline.yml down -v --remove-orphans

# Build the services
docker-compose -f docker-compose-offline.yml build

# Start the services
docker-compose -f docker-compose-offline.yml up
```

For any issues, please contact [karthikerathore@gmail.com](mailto:karthikerathore@gmail.com).

## Notes

- This repository focuses exclusively on the backend API.
- It is designed to be paired seamlessly with any web or mobile frontend.
- The platform can be extended with additional modules such as moderation, notifications, and analytics.
