#!/bin/bash

set -e

# Variable definitions
AWS_REGION="ap-northeast-2"
AWS_ACCOUNT_ID="383033713164"
ECR_REPO="snapsapi-ecsdeploy"
ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest"
IMAGE_NAME="snapsapi-ecsdeploy:latest"
COMPOSE_FILE="docker-compose.prod.yml"

# 1. ECR login
echo "Logging in to AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Build the Docker image using docker-compose (no-cache, platform amd64)
echo "Building Docker image with compose..."
docker compose -f $COMPOSE_FILE build --no-cache

# 3. Tag the image for ECR
echo "Tagging image for ECR..."
docker tag $IMAGE_NAME $ECR_URL

# 4. Push the image to ECR
echo "Pushing image to ECR..."
docker push $ECR_URL

echo "✅ Done! Image pushed to $ECR_URL"
