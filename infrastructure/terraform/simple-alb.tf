# Simple ALB configuration using existing VPC
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  
  filter {
    name   = "map-public-ip-on-launch"
    values = ["true"]
  }
}

# Security group for ALB
resource "aws_security_group" "simple_alb" {
  name_prefix = "ultimatesystems-alb-"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ultimatesystems-alb-sg"
  }
}

# Simple ALB
resource "aws_lb" "simple" {
  name               = "ultimatesystems-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.simple_alb.id]
  subnets            = data.aws_subnets.public.ids

  enable_deletion_protection = false

  tags = {
    Name = "ultimatesystems-alb"
  }
}

# Target group
resource "aws_lb_target_group" "simple" {
  name     = "ultimatesystems-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "ultimatesystems-tg"
  }
}

# HTTP listener
resource "aws_lb_listener" "simple_http" {
  load_balancer_arn = aws_lb.simple.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.simple.arn
  }
}

# Output ALB DNS name
output "simple_alb_dns_name" {
  value = aws_lb.simple.dns_name
}

output "simple_alb_zone_id" {
  value = aws_lb.simple.zone_id
}

output "simple_target_group_arn" {
  value = aws_lb_target_group.simple.arn
}

