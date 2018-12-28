# Copyright 2018 Calum Loudon
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not 
# use this file except in compliance with the License. A copy of the License
# is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
# CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

# This file stores and retrieves objects from S3.  It is a simple wrapper
# around S3 with no knowledge of the schema. 
#
# We support both reading and writing in simple CRUD fashion.
#
# xxx for now, everything is public access.

import boto3, botocore

from logutilities import log_info, log_debug


def write_object(bucket_name, key_name, blob, version):
	s3 = boto3.resource('s3')

	# Check if bucket exists
	try:
		s3.meta.client.head_bucket(Bucket = bucket_name)
		log_debug("Bucket %s exists", bucket_name)
	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		if error_code == 403:
			log_error("Denied access to bucket %s", bucket_name)
		elif error_code == 404:
			log_debug("Bucket %s does not exist - creating", bucket_name)
			bucket = s3.create_bucket(ACL = 'public-read-write', Bucket = bucket_name)
		else:
			log_error("Error %d checking bucket %s", error_code, bucket_name)

	try:
		metadata = { "schema_version": version}
		s3.put_object(Bucket = bucket_name, Key = key_name, Body = blob, ACL = 'public-read-write', Metadata = metadata)
		log_debug("Written object %s to bucket %s", key_name, bucket_name)
	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		log_error("Error %d writing object %s to bucket %s", error_code, key_name, bucket_name)


def read_object(bucket_name, key_name):
	blob = b''
	version = ""
	s3 = boto3.resource('s3')

	# Check if bucket exists
	try:
		response = s3.get_object(Bucket = bucket_name, Key = key_name)

		blob = response['Body'].read()
		version = response['Metadata']['schema_version']
		log_debug("Returned %d bytes of schema version %s reading object %s from bucket %s", PyBytes_Size(blob), version, key_name, bucket_name)

	except botocore.exceptions.ClientError as e:
		error_code = int(e.response['Error']['Code'])
		log_error("Error %d reading object %s from bucket %s", error_code, key_name, bucket_name)
		
	return blob, version




	

