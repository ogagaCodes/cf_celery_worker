def generate_userdata_script(sqs_queue_url):
    userdata_script = f"""#!/bin/bash
    yum update -y
    yum install -y python3
    pip3 install celery boto3
    celery -A your_project worker --loglevel=info -Q {sqs_queue_url}
    """
    return userdata_script
