variable service {
  type = map(string)
  # service location
  default = {
    name = "model"
    description = "neural netowrk model"
    filename = "lambda_model.zip"
    local_mount_path = "/mnt/efs"
    efs_pip_path = "/lib"
  }
}

data "archive_file" "service_zip_package" {
  type = "zip"
  source_dir = "${path.module}/../src"
  output_path = var.service.filename
}

resource "aws_s3_bucket_object" "service_package_s3_object" {
  bucket = aws_s3_bucket.static_files.id
  key = data.archive_file.service_zip_package.output_path
  source = data.archive_file.service_zip_package.output_path
  etag = data.archive_file.service_zip_package.output_md5
}

resource "aws_lambda_function" "service_lambda" {
  depends_on = [
    aws_s3_bucket_object.service_package_s3_object,
    aws_iam_role_policy_attachment.lambda_policy,
    aws_efs_mount_target.efs_targets,
  ]

  # S3 bucket must exist with a packaged .zip before terraform apply
  s3_bucket = aws_s3_bucket.static_files.bucket
  s3_key = aws_s3_bucket_object.service_package_s3_object.key
  source_code_hash = aws_s3_bucket_object.service_package_s3_object.content_base64

  publish = true
  function_name = var.service.name
  description = var.service.description
  role = aws_iam_role.lambda_role.arn
  handler = "main.handler"
  memory_size = 3008
  timeout = 60
  runtime = "python3.8"

  environment {
    variables = {
      MNT_DIR = var.service.local_mount_path
      EFS_PIP_PATH = "${var.service.local_mount_path}${var.service.efs_pip_path}"
    }
  }

  file_system_config {
    arn = aws_efs_access_point.access_point.arn
    local_mount_path = var.service.local_mount_path
  }

  vpc_config {
    subnet_ids = data.aws_subnet_ids.subnets.ids
    security_group_ids = data.aws_security_groups.security_groups.ids
  }

  tracing_config {
    # disables X-Ray
    mode = "PassThrough"
  }

  tags = merge(var.tags, {
    name = var.service.name
  })
}