# FastAPI Celery Worker Deployment via AWS CloudFormation

This project is a FastAPI application that dynamically generates and deploys an AWS CloudFormation stack to spin up N Celery workers. The workers are configured to connect to an AWS SQS queue as their broker. The application provides an API endpoint to trigger the deployment of the workers, and it also integrates with GitHub Actions to automate deployment on pushes to the main branch.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [GitHub Actions](#github-actions)
8. [Contributing](#contributing)
9. [License](#license)

## Features

- Deploy N Celery workers on AWS using CloudFormation.
- Uses AWS SQS as the message broker for Celery workers.
- Expose a FastAPI endpoint (`/deploy-workers/`) to dynamically trigger the deployment.
- Auto Scaling Group ensures the required number of workers is always maintained.
- Integration with GitHub Actions for automated deployment on code pushes.

## Prerequisites

Before you can use this project, ensure you have the following installed:

- Python 3.8+
- AWS Account with appropriate permissions (IAM, EC2, SQS, CloudFormation).
- AWS CLI configured with your credentials.
- `boto3`, `troposphere`, `FastAPI`, and other Python dependencies (detailed in `requirements.txt`).

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/fastapi-celery-cloudformation.git
    cd fastapi-celery-cloudformation
    ```

2. **Set up a virtual environment:**

    ```bash
    python -m venv env
    source env/bin/activate  # For macOS/Linux
    # .\env\Scripts\activate  # For Windows
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **Set up AWS credentials:**

    Ensure your AWS credentials are configured either via `aws configure` or by adding them to a `.env` file. This project uses the `python-dotenv` package to load environment variables.

2. **Create a `.env` file** in the root of your project and configure the following variables:

    ```ini
    AWS_ACCESS_KEY_ID=your_aws_access_key_id
    AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
    AWS_REGION=us-east-1
    VPC_ID=vpc-xxxxx
    SUBNET_ID=subnet-xxxxx
    AMI_ID=ami-xxxxx  # Your AMI ID for EC2 instances
    KEY_PAIR_NAME=your-key-pair  # Optional: Remove if not using SSH access
    ```

3. **Set your desired AWS region, VPC, Subnet, AMI, and Key Pair values.**

## Running the Application

1. **Run the FastAPI application using Uvicorn:**

    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

2. **Access the FastAPI documentation:**

    Navigate to `http://localhost:8000/docs` to interact with the API using FastAPI's interactive Swagger UI.

3. **Trigger worker deployment:**

    You can POST to the `/deploy-workers/` endpoint to deploy Celery workers, specifying the `worker_count` in the request body. For example:

    ```bash
    curl -X POST "http://localhost:8000/deploy-workers/" \
    -H "Content-Type: application/json" \
    -d '{"worker_count": 3}'
    ```

    This will deploy 3 Celery workers via CloudFormation.

## Testing

The project uses `pytest` for unit testing. The CloudFormation and Boto3 interactions are mocked to ensure isolated testing.

1. **Install `pytest`:**

    ```bash
    pip install pytest
    ```

2. **Run the tests:**

    ```bash
    pytest tests/
    ```

3. **Test Coverage:**
   - The test suite includes unit tests for the `create_cloudformation_template` and `create_and_deploy_cloudformation` functions.
   - All tests are located in the `tests/` directory.

## GitHub Actions

This project includes a GitHub Actions workflow to automatically trigger the FastAPI API and deploy Celery workers when code is pushed to the main branch.

1. **Configure GitHub Secrets:**

   Set up the following GitHub repository secrets:

   - `FASTAPI_DEPLOY_URL`: The URL of the deployed FastAPI application.

2. **Workflow Trigger:**

   The workflow in `.github/workflows/deploy.yaml` will automatically trigger when you push to the `main` branch. The workflow sends a POST request to the FastAPI API endpoint to deploy Celery workers.

## Contributing

We welcome contributions to improve this project! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
