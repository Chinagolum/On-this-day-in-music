# --------------------
# ECR Repository
# --------------------
resource "aws_ecr_repository" "pitchfork_scraper" {
  name = "pitchfork-scraper"
}

# --------------------
# ECS Cluster
# --------------------
resource "aws_ecs_cluster" "scraper_cluster" {
  name = "pitchfork-scraper-cluster"
}

# --------------------
# CloudWatch Logs
# --------------------
resource "aws_cloudwatch_log_group" "scraper_logs" {
  name              = "/ecs/pitchfork-scraper"
  retention_in_days = 7
}

# --------------------
# ECS Execution Role (Required for Fargate logging)
# --------------------
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecsExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy_attach" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# --------------------
# ECS Task Definition
# --------------------
resource "aws_ecs_task_definition" "scraper_task" {
  family                   = "pitchfork-scraper"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn   # <-- REQUIRED

  container_definitions = jsonencode([
    {
      name      = "pitchfork-scraper"
      image     = "${aws_ecr_repository.pitchfork_scraper.repository_url}:latest"
      essential = true
      environment = [
        { name = "AWS_ACCESS_KEY_ID", value = var.AWS_ACCESS_KEY_ID },
        { name = "AWS_SECRET_ACCESS_KEY", value = var.AWS_SECRET_ACCESS_KEY },
        { name = "AWS_REGION", value = var.AWS_REGION },
        { name = "DB_URL", value = var.DB_URL },
        { name = "OPENAI_API_KEY", value = var.OPENAI_API_KEY },
        { name = "AWS_BUCKET", value = var.AWS_BUCKET},
        
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.scraper_logs.name
          "awslogs-region"        = var.AWS_REGION
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# --------------------
# ECS Fargate Service
# --------------------
resource "aws_ecs_service" "scraper_service" {
  name            = "pitchfork-scraper-service"
  cluster         = aws_ecs_cluster.scraper_cluster.id
  task_definition = aws_ecs_task_definition.scraper_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnets          # [cite: 20, 25]
    security_groups  = [var.security_group] # [cite: 20, 25]
    assign_public_ip = true                 # [cite: 20]
  }
}