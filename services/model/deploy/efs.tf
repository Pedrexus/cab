# get all available availability zones

data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "subnets" {
  vpc_id = data.aws_vpc.default.id
}

data "aws_security_groups" "security_groups" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# EFS File System

resource "aws_efs_file_system" "efs" {
  creation_token = "serverless-bert"
}

# Access Point

resource "aws_efs_access_point" "access_point" {
  file_system_id = aws_efs_file_system.efs.id
}

# Mount Targets

resource "aws_efs_mount_target" "efs_targets" {
  for_each = data.aws_subnet_ids.subnets.ids
  subnet_id      = each.value
  file_system_id = aws_efs_file_system.efs.id
}

# SSM Parameter for serverless

resource "aws_ssm_parameter" "efs_access_point" {
  name      = "/efs/accessPoint/id"
  type      = "String"
  value     = aws_efs_access_point.access_point.id
  overwrite = true
}

output "efs_filesystem_id" {
  value = aws_efs_file_system.efs.id
}

output "subnet_id" {
  value = data.aws_subnet_ids.subnets.id
}