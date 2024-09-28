#!/bin/bash

# Source environment variables
source .env
# Start socat and Docker service
socat TCP-LISTEN:2376,reuseaddr,fork,bind=127.0.0.1 UNIX-CLIENT:/var/run/docker.sock &

# Make iectl executable
chmod +x ./iectl

# Verify docker engine
./iectl publisher docker-engine verify --url $DOCKER_HOST

# Add configuration
./iectl config add iem --url "$IE_URL" --user "$IE_USER" --password "$IE_PASS" --name "$IE_CONFIG_NAME"

# Create workspace
mkdir -p ie_workspace
cd ./ie_workspace || { echo "Failed to enter workspace directory"; exit 1; }

# Initialize workspace
../iectl publisher workspace init
# Create standalone app
../iectl publisher standalone-app create --appname "$APP_NAME" --reponame "$APP_REPO_NAME" --appdescription "$APP_DESCRIPTION" --iconpath "/root/../usr/src/volume/generated-apps/Ex1/Hello_World_App_Icon.png"

# Create standalone app version
../iectl publisher standalone-app version create -a "$APP_NAME" -v "$VERSION_NUMBER" -y "$DOCKER_COMPOSE_PATH" --redirectsection web --redirecturl "$REDIRECT_URL" --redirecttype FromBoxSpecificPort

# Add publisher configuration
../iectl config add publisher --dockerurl "$DOCKER_URL" --workspace . --name "$IE_CONFIG_NAME"

# Upload project
../iectl publisher app upload project --applicationname "$APP_NAME" --versionnumber "$VERSION_NUMBER" \
    --projectid "$PROJECT_ID" --categoryid "$CATEGORY_ID" --webaddress "$WEBADDRESS"

# Final confirmation message
echo "Script executed successfully!"
