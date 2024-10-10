resource "google_storage_bucket" "test_bucket" {
  name     = "mega2mini-tf-repo-test-bucket"
  location = "europe-west2"
}