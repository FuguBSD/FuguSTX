output "pipeline_application_id" {
  value = scaleway_iam_application.pipeline.id
}

output "operator_application_id" {
  value = scaleway_iam_application.operator.id
}

output "train_application_id" {
  value = scaleway_iam_application.train.id
}

output "bucket_names" {
  value = [
    scaleway_object_bucket.corpus.name,
    scaleway_object_bucket.evalcorpus.name,
    scaleway_object_bucket.checkpoints.name,
    scaleway_object_bucket.artifacts.name,
  ]
}
