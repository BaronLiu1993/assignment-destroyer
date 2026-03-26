from queue.file.fileIngestionQueue import celery_app
from service.context_service import process_file_from_s3_to_memory


@celery_app.task(name="queue.file.fileIngestionWorker.process_file_from_s3")
def process_file_from_s3(
	user_id,
	thread_id,
	bucket,
	object_key,
	filename,
	role="context",
	window_size=2000,
	overlap=200,
):
	return process_file_from_s3_to_memory(
		user_id=user_id,
		thread_id=thread_id,
		bucket=bucket,
		object_key=object_key,
		filename=filename,
		role=role,
		window_size=window_size,
		overlap=overlap,
	)
