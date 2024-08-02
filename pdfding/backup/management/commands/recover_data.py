import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

minio_client = Minio(
    endpoint=settings.BACKUP_ENDPOINT,
    secure=settings.BACKUP_SECURE,
    access_key=settings.BACKUP_ACCESS_KEY,
    secret_key=settings.BACKUP_SECRET_KEY,
)

logger = logging.getLogger('recover_data')


class Command(BaseCommand):
    help = "Recover data from S3 backup"

    def handle(self, *args, **kwargs):
        logger.info('----------------------------------------------------')
        logger.info('Are you sure you want to proceed with the data recovery?')
        logger.info('If you are using a sqlite DB, this operation will overwrite your local DB!')
        logger.info('Type "y" to confirm')
        user_input = input()

        if user_input == 'y':
            logger.info('')
            logger.info('Starting data recovery')

            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
                logger.info('Recovering database')
                minio_client.fget_object(
                    settings.BACKUP_BUCKET_NAME,
                    settings.DATABASES['default']['BACKUP_NAME'].name,
                    settings.DATABASES['default']['NAME'],
                )

            logger.info('Recovering PDF files')
            objects = minio_client.list_objects(settings.BACKUP_BUCKET_NAME, recursive=True)
            for obj in objects:
                obj_name = obj.object_name
                if obj_name != settings.DATABASES['default']['BACKUP_NAME'].name:
                    minio_client.fget_object(settings.BACKUP_BUCKET_NAME, obj_name, settings.MEDIA_ROOT / obj_name)

            logger.info('Data recovery completed successfully.')
            logger.info('----------------------------------------------------')
        else:  # pragma: no cover
            logger.info('Aborting data recovery.')
            logger.info('----------------------------------------------------')
