from botocore.exceptions import BotoCoreError, ClientError
from django.core.exceptions import ValidationError


class BucketServiceError(Exception):
    def __init__(self, message, code='BUCKET_ERROR'):
        self.message = message
        self.code = code
        super().__init__(message)


def handle_boto_error(exc):
    if isinstance(exc, ClientError):
        error = exc.response.get('Error', {})
        return BucketServiceError(
            message=error.get('Message', str(exc)),
            code=error.get('Code', 'CLIENT_ERROR'),
        )
    if isinstance(exc, BotoCoreError):
        return BucketServiceError(message=str(exc), code='BOTO_CORE_ERROR')
    return BucketServiceError(message=str(exc))


def get_active_bucket(bucket_config):
    if not bucket_config.is_active:
        raise ValidationError('Bucket inativo.')
    return bucket_config
