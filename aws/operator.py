import time

from boto3 import Session


class AWSOperater(object):

    def __init__(self, access_key_id, secret_access_key, region):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region

        self.session = Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region)

    def create_instance(self, template_id, version):
        """
        Use template create instance
        http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.ServiceResource.create_instances
        """
        client = self.session.resource('ec2')
        instance = client.create_instances(
            LaunchTemplate={'LaunchTemplateId': template_id, 'Version': version},
            MaxCount=1,
            MinCount=1)
        return instance[0].id

    def get_instance_ip(self, instance_id):
        """
        """
        client = self.session.resource('ec2')
        return client.Instance(instance_id).public_ip_address

    def terminate_instance(self, instance_id):
        client = self.session.resource('ec2')
        return client.Instance(instance_id).terminate()

    def instance_status_checker(self, instance_id):
        client = self.session.client('ec2')
        waiter = client.get_waiter('instance_status_ok')
        status = waiter.wait(
                            Filters=[
                                {
                                    'Name': 'system-status.status',
                                    'Values': [
                                        'ok',
                                    ]
                                },
                            ],
                            InstanceIds=[
                                instance_id,
                            ],
                    )
        if status is None:
            return True
        else:
            return False

    def create_record_set(self, host_zone_id, name, ip):
        client = self.session.client('route53')
        response = client.change_resource_record_sets(
            HostedZoneId=host_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': 'A',
                            'TTL': 60,
                            'ResourceRecords': [
                                {
                                    'Value': ip
                                },
                            ],
                        }
                    },
                ]
            }
        )
        return response

    def delete_record_set(self, host_zone_id, name, ip):
        client = self.session.client('route53')
        response = client.change_resource_record_sets(
            HostedZoneId=host_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': 'A',
                            'TTL': 60,
                            'ResourceRecords': [
                                {
                                    'Value': ip
                                },
                            ],
                        }
                    },
                ]
            }
        )
        return response