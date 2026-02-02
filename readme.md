# Discussion Forum API

## Architecture

The service leverages a clean separation of concerns across its core components: authentication, discussion management, and social interactions. The high-level domain and database model is illustrated below:

![Database UML](./static/dbdiagram_UML.png)

## Running Locally

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

