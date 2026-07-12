terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "dynamodb_table_name" {
  type    = string
  default = "employee_costs"
}

resource "aws_dynamodb_table" "employee_costs" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    app = "api-etl"
  }
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.employee_costs.name
}

output "dynamodb_table_arn" {
  value = aws_dynamodb_table.employee_costs.arn
}

