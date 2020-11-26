variable "tags" {
  description = "Tags to apply to all resources created by the modules"
  type = map(string)
  default = {
    "project" = "cab"
  }
}