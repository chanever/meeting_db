import boto3
from dotenv import load_dotenv
import os

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

txt_file = 'test.txt'
txt_object = 'txt_files/test.txt'
s3.upload_file(txt_file, bucket_name, txt_object)
print(f"{txt_file} 업로드 완료!")

wav_file = 'test.wav'
wav_object = 'wav_files/test.wav'
s3.upload_file(wav_file, bucket_name, wav_object)
print(f"{wav_file} 업로드 완료!")