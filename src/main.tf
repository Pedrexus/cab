terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  profile = "default"
  region = "us-east-1"
}

module "backend" {
  source = "./services/backend/deploy"
  tags = var.tags
}

module "model" {
  source = "./services/model/deploy"
  tags = var.tags
}

