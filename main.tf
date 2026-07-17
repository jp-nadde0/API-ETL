terraform {
  required_version = ">= 1.8.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# -------------------------
# Variables
# -------------------------
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "api-etl"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

# REMOVIDA: var.ami_id (Agora usamos Data Source dinâmico para o Ubuntu)

variable "key_name" {
  description = "Opcional: nome da key pair para SSH"
  type        = string
  default     = ""
}

variable "dynamodb_table_name" {
  type    = string
  default = "employee_costs"
}

variable "rds_database_name" {
  type    = string
  default = "appdb"
}

variable "rds_username" {
  type    = string
  default = "postgres"
}

variable "rds_password" {
  type      = string
  sensitive = true
}

variable "rds_engine_version" {
  type    = string
  default = "16.3"
}

variable "vpc_endpoint_enable" {
  type    = bool
  default = true
}

locals {
  azs = var.azs
}

variable "azs" {
  description = "Duas AZs para criar subnets (ex: [\"us-east-1a\", \"us-east-1b\"])"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# -------------------------
# Data Source: Ubuntu 22.04 AMI
# -------------------------
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# -------------------------
# VPC
# -------------------------
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_subnet" "public" {
  for_each = {
    for idx, cidr in var.public_subnet_cidrs : idx => cidr
  }

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = local.azs[tonumber(each.key)]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-${each.key}"
  }
}

resource "aws_subnet" "private" {
  for_each = {
    for idx, cidr in var.private_subnet_cidrs : idx => cidr
  }

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = local.azs[tonumber(each.key)]
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.project_name}-private-${each.key}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route" "public_default" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}

# -------------------------
# Security Groups
# -------------------------
resource "aws_security_group" "ec2_sg" {
  name        = "${var.project_name}-ec2-sg"
  description = "EC2 SG for Nginx (80/443)"
  vpc_id      = aws_vpc.this.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  dynamic "ingress" {
    for_each = var.key_name != "" ? [1] : []
    content {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ec2-sg"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "SG RDS (PostgreSQL) - acesso somente a partir do EC2 SG"
  vpc_id      = aws_vpc.this.id

  ingress {
    description     = "PostgreSQL"
    from_port       = 5432 # CORRIGIDO: Era 3306 (MySQL), agora 5432 (Postgres)
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

# -------------------------
# IAM Role for EC2 (to access DynamoDB)
# -------------------------
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "ec2_dynamo_policy" {
  name = "${var.project_name}-dynamodb-access"
  role = aws_iam_role.ec2_role.id

    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# -------------------------
# EC2 + Nginx reverse proxy + API container
# -------------------------
resource "aws_launch_template" "ec2_lt" {
  name_prefix   = "${var.project_name}-lt-"
  image_id      = data.aws_ami.ubuntu.id # CORRIGIDO: Puxando AMI dinamicamente
  instance_type = var.instance_type
  key_name      = var.key_name != "" ? var.key_name : null

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  user_data = base64encode(<<-EOT
    #!/bin/bash
    set -euxo pipefail

    export DEBIAN_FRONTEND=noninteractive

    # Install dependencies
    apt-get update -y
    apt-get install -y docker.io nginx awscli
    systemctl enable docker
    systemctl start docker
    systemctl enable nginx
    systemctl start nginx

    # Ensure docker is usable
    usermod -aG docker ubuntu || true

    # Nginx reverse proxy
    cat >/etc/nginx/sites-available/api-proxy <<'NGINX'
    server {
      listen 80;
      server_name _;

      location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_pass http://127.0.0.1:8000;
      }
    }
    NGINX

    ln -sf /etc/nginx/sites-available/api-proxy /etc/nginx/sites-enabled/api-proxy
    rm -f /etc/nginx/sites-enabled/default || true
    nginx -t
    systemctl restart nginx

    # Run API container locally
    docker pull api-etl:latest || true
    docker rm -f api-service || true

    docker run -d --name api-service \
      --restart unless-stopped \
      -e "DATABASE_URL=postgresql+psycopg2://${var.rds_username}:${var.rds_password}@${aws_db_instance.rds.address}:5432/${var.rds_database_name}" \
      -e "AWS_REGION=${var.aws_region}" \
      -e "DYNAMODB_TABLE=${var.dynamodb_table_name}" \
      -p 8000:8000 \
      api-etl:latest

    # Health check
    sleep 8
    curl -fsS http://127.0.0.1:8000/docs || true
  EOT
  )
}

resource "aws_instance" "nginx_ec2" {
  subnet_id = values(aws_subnet.public)[0].id

  # CORRIGIDO: Herdar configurações direto do Launch Template limpa o código
  launch_template {
    id      = aws_launch_template.ec2_lt.id
    version = "$Latest"
  }

  tags = {
    Name = "${var.project_name}-nginx-ec2"
  }
}

# -------------------------
# RDS (single AZ with private subnets group)
# -------------------------
resource "aws_db_subnet_group" "rds_subnets" {
  name       = "${var.project_name}-db-subnets"
  subnet_ids = [for s in aws_subnet.private : s.id]

  lifecycle {
    ignore_changes = [tags, tags_all]
  }
}

resource "aws_db_instance" "rds" {
  identifier     = "${var.project_name}-rds"
  engine         = "postgres"
  engine_version = var.rds_engine_version

  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  username = var.rds_username
  password = var.rds_password
  db_name  = var.rds_database_name

  port = 5432 # CORRIGIDO: Porta oficial do Postgres 

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.rds_subnets.name

  multi_az            = false
  publicly_accessible = false

  availability_zone = local.azs[0]

  skip_final_snapshot = true
  deletion_protection = false
}

# -------------------------
# DynamoDB Gateway Endpoint
# -------------------------
resource "aws_dynamodb_table" "employee_costs" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    app = var.project_name
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  count = var.vpc_endpoint_enable ? 1 : 0

  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [aws_route_table.private.id]

  tags = {
    Name = "${var.project_name}-dynamodb-endpoint"
  }
}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "ec2_public_ip" {
  value = aws_instance.nginx_ec2.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.rds.address
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.employee_costs.name
}

output "dynamodb_table_arn" {
  value = aws_dynamodb_table.employee_costs.arn
}