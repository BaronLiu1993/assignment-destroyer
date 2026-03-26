from celery import Celery

from service.tools.constants import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


celery_app = Celery(
	"file_ingestion",
	broker=CELERY_BROKER_URL,
	backend=CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
	task_serializer="json",
	accept_content=["json"],
	result_serializer="json",
	timezone="UTC",
	enable_utc=True,
)


def enqueue_file_ingestion(
	user_id,
	thread_id,
	bucket,
	object_key,
	filename,
	role="context",
	window_size=2000,
	overlap=200,
):
	return celery_app.send_task(
		"queue.file.fileIngestionWorker.process_file_from_s3",
		kwargs={
			"user_id": user_id,
			"thread_id": thread_id,
			"bucket": bucket,
			"object_key": object_key,
			"filename": filename,
			"role": role,
			"window_size": window_size,
			"overlap": overlap,
		},
	)
