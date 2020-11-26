resource "aws_dynamodb_table" "input_dynamodb_table" {
  name             = "cab"
  billing_mode     = "PROVISIONED"
  stream_view_type = "KEYS_ONLY"
  stream_enabled   = true
  read_capacity    = 5
  write_capacity   = 5
  hash_key         = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = merge(var.tags, {
    name = "cab-dynamodb-table"
  })
}