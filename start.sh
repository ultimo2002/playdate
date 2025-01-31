#TODO change dev to main
#!/bin/bash

# Navigate to the project directory
cd /DATA/AppData/API-repo/DevOps

# Pull the latest changes from the dev branch
git pull origin dev

# Stop the currently running container
docker stop fastapi

# Remove the old image
docker rmi fastapi

# Rebuild the Docker image
docker build -t fastapi .

# Run the updated container
docker run -d --restart unless-stopped --name fastapi --rm -it -p 8000:8000 fastapi
