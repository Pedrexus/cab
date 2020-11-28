resource "aws_s3_bucket" "static_files" {
  bucket = "cab-static-files"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = merge(var.tags, {
    name = "cab-bucket"
  })
}



data "aws_iam_policy_document" "s3_bucket_policy_document" {
  // denies all s3 access without ssl
  // complies with s3-bucket-ssl-requests-only rule
  statement {
    effect = "Deny"
    actions = [
      "s3:*"
    ]
    resources = ["arn:aws:s3:::${aws_s3_bucket.static_files.bucket}/*"]

    # anonymous user
    principals {
      identifiers = [
        "*"
      ]
      type = "*"
    }

    condition {
      test = "Bool"
      values = [
        false
      ]
      variable = "aws:SecureTransport"
    }
  }
}

resource "aws_s3_bucket_policy" "static_files_policy" {
  bucket = aws_s3_bucket.static_files.bucket
  policy = data.aws_iam_policy_document.s3_bucket_policy_document.json
}