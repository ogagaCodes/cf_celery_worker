import boto3
from troposphere import Template, Ref, Parameter, Output, Base64, Join, GetAtt
import troposphere.ec2 as ec2
import troposphere.autoscaling as autoscaling
import troposphere.sqs as sqs
import troposphere.iam as iam
from app.config import settings
from app.utils import generate_userdata_script

def create_cloudformation_template(worker_count: int) -> str:
    # Create a CloudFormation template
    template = Template()
    template.set_description("CloudFormation template to spin up Celery workers connected to SQS.")

    # Parameters
    worker_count_param = template.add_parameter(
        Parameter(
            "WorkerCount",
            Type="Number",
            Default=str(worker_count),
            Description="Number of Celery Workers to spin up"
        )
    )

    # Security Group
    security_group = template.add_resource(
        ec2.SecurityGroup(
            "CelerySecurityGroup",
            GroupDescription="Security group for Celery worker instances",
            VpcId=settings.vpc_id,
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(IpProtocol="tcp", FromPort="22", ToPort="22", CidrIp="0.0.0.0/0"),  # SSH access
            ],
        )
    )

    # IAM Role and Instance Profile for EC2
    iam_role = template.add_resource(
        iam.Role(
            "EC2Role",
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": ["ec2.amazonaws.com"]},
                        "Action": ["sts:AssumeRole"]
                    }
                ]
            },
            Policies=[
                iam.Policy(
                    PolicyName="CeleryWorkerPolicy",
                    PolicyDocument={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": ["sqs:*"],
                                "Resource": "*"
                            }
                        ]
                    }
                )
            ]
        )
    )

    instance_profile = template.add_resource(
        iam.InstanceProfile(
            "InstanceProfile",
            Roles=[Ref(iam_role)]
        )
    )

    # SQS Queue
    sqs_queue = template.add_resource(
        sqs.Queue(
            "CelerySQSQueue",
            QueueName="celery-worker-queue"
        )
    )

    # Launch Configuration
    launch_config = template.add_resource(
        autoscaling.LaunchConfiguration(
            "CeleryWorkerLaunchConfiguration",
            ImageId=settings.ami_id,
            InstanceType="t2.micro",
            SecurityGroups=[Ref(security_group)],
            IamInstanceProfile=Ref(instance_profile),
            KeyName=settings.key_pair_name,  # Optional: Remove this line if not using a key pair
            UserData=Base64(
                Join(
                    "\n",
                    [
                        "#!/bin/bash",
                        "yum update -y",
                        "yum install -y python3",
                        "pip3 install celery boto3",
                        generate_userdata_script(Ref(sqs_queue))
                    ]
                )
            )
        )
    )

    # Auto Scaling Group
    auto_scaling_group = template.add_resource(
        autoscaling.AutoScalingGroup(
            "CeleryWorkerAutoScalingGroup",
            DesiredCapacity=Ref(worker_count_param),
            MinSize="1",
            MaxSize=Ref(worker_count_param),
            LaunchConfigurationName=Ref(launch_config),
            VPCZoneIdentifier=[settings.subnet_id],  # Replace with your Subnet ID
            Tags=[autoscaling.Tag("Name", "CeleryWorker", True)]
        )
    )

    # Outputs
    template.add_output([
        Output(
            "SQSQueueURL",
            Description="URL of the SQS Queue for Celery",
            Value=Ref(sqs_queue)
        ),
        Output(
            "AutoScalingGroupName",
            Description="Name of the Auto Scaling Group",
            Value=Ref(auto_scaling_group)
        ),
    ])

    return template.to_json()

def deploy_cloudformation(template_body: str, worker_count: int):
    # Create a CloudFormation client
    client = boto3.client(
        'cloudformation',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )

    # Deploy the CloudFormation stack
    response = client.create_stack(
        StackName="CeleryWorkerStack",
        TemplateBody=template_body,
        Parameters=[
            {
                'ParameterKey': 'WorkerCount',
                'ParameterValue': str(worker_count)
            }
        ],
        Capabilities=['CAPABILITY_NAMED_IAM'],  # Needed for creating IAM roles and policies
        OnFailure='ROLLBACK'  # Automatically roll back if stack creation fails
    )

    return response

def create_and_deploy_cloudformation(worker_count: int):
    # Generate the CloudFormation template
    template_body = create_cloudformation_template(worker_count)
    
    # Deploy the CloudFormation stack with worker_count
    response = deploy_cloudformation(template_body, worker_count)
    
    return response
