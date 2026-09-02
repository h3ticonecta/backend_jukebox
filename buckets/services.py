import boto3
from botocore.config import Config

from buckets.exceptions import BucketServiceError, handle_boto_error


class S3BucketService:
    def __init__(self, bucket_config):
        self.bucket_config = bucket_config
        self.client = boto3.client(
            's3',
            endpoint_url=bucket_config.endpoint_url,
            aws_access_key_id=bucket_config.access_key_id,
            aws_secret_access_key=bucket_config.secret_access_key,
            region_name=bucket_config.region_name or 'auto',
            config=Config(signature_version='s3v4'),
        )
        self.bucket_name = bucket_config.bucket_name

    def test_connection(self):
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return {'connected': True, 'bucket': self.bucket_name}
        except Exception as exc:
            raise handle_boto_error(exc) from exc

    def list_objects(self, prefix='', continuation_token=None, max_keys=100):
        try:
            params = {
                'Bucket': self.bucket_name,
                'Prefix': prefix,
                'MaxKeys': max_keys,
                'Delimiter': '/',
            }
            if continuation_token:
                params['ContinuationToken'] = continuation_token

            response = self.client.list_objects_v2(**params)

            objects = [
                {
                    'key': item['Key'],
                    'size': item['Size'],
                    'last_modified': item['LastModified'].isoformat(),
                    'etag': item['ETag'].strip('"'),
                    'public_url': self.bucket_config.get_public_url(item['Key']),
                }
                for item in response.get('Contents', [])
            ]

            prefixes = [
                item['Prefix']
                for item in response.get('CommonPrefixes', [])
            ]

            return {
                'prefix': prefix,
                'objects': objects,
                'folders': prefixes,
                'is_truncated': response.get('IsTruncated', False),
                'next_continuation_token': response.get('NextContinuationToken'),
                'key_count': response.get('KeyCount', len(objects)),
            }
        except Exception as exc:
            raise handle_boto_error(exc) from exc

    def list_all_objects(self, prefix=''):
        try:
            objects = []
            continuation_token = None

            while True:
                params = {
                    'Bucket': self.bucket_name,
                    'Prefix': prefix,
                    'MaxKeys': 1000,
                }
                if continuation_token:
                    params['ContinuationToken'] = continuation_token

                response = self.client.list_objects_v2(**params)
                for item in response.get('Contents', []):
                    objects.append({
                        'key': item['Key'],
                        'size': item['Size'],
                        'last_modified': item['LastModified'].isoformat(),
                        'etag': item['ETag'].strip('"'),
                        'public_url': self.bucket_config.get_public_url(item['Key']),
                    })

                if not response.get('IsTruncated'):
                    break
                continuation_token = response.get('NextContinuationToken')

            return objects
        except Exception as exc:
            raise handle_boto_error(exc) from exc

    def upload_object(self, key, file_obj, content_type=None):
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            if extra_args:
                self.client.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    key,
                    ExtraArgs=extra_args,
                )
            else:
                self.client.upload_fileobj(file_obj, self.bucket_name, key)

            return {'key': key, 'bucket': self.bucket_name}
        except Exception as exc:
            raise handle_boto_error(exc) from exc

    def move_object(self, source_key, destination_key):
        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource=copy_source,
                Key=destination_key,
            )
            self.client.delete_object(Bucket=self.bucket_name, Key=source_key)
            return {
                'source_key': source_key,
                'destination_key': destination_key,
                'bucket': self.bucket_name,
            }
        except Exception as exc:
            raise handle_boto_error(exc) from exc

    def delete_objects(self, keys):
        if not keys:
            raise BucketServiceError('Nenhuma chave informada para exclusão.', 'VALIDATION_ERROR')

        try:
            response = self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': [{'Key': key} for key in keys],
                    'Quiet': True,
                },
            )
            deleted = [item['Key'] for item in response.get('Deleted', [])]
            errors = response.get('Errors', [])
            return {
                'deleted': deleted,
                'errors': errors,
                'bucket': self.bucket_name,
            }
        except Exception as exc:
            raise handle_boto_error(exc) from exc
