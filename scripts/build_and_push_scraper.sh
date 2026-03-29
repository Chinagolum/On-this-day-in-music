#!/bin/bash

# Build and push
docker buildx build \
  --platform linux/amd64 \
  -f docker/Dockerfile \
  -t 846693397697.dkr.ecr.eu-north-1.amazonaws.com/pitchfork-scraper:latest \
  --push \
  .

# Run task
aws ecs run-task \
  --cluster pitchfork-scraper-cluster \
  --task-definition pitchfork-scraper \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-0f874925280d7ab87,subnet-07b175f417cde11fe,subnet-0def9191edb50a5b4],securityGroups=[sg-084414d119bb32825],assignPublicIp=ENABLED}"   