from fastapi import FastAPI, HTTPException
from app.schemas import DeploymentRequest
from app.cloudformation import create_and_deploy_cloudformation

app = FastAPI()

@app.post("/deploy-workers/")
async def deploy_celery_workers(request: DeploymentRequest):
    try:
        # Call the function to create and deploy the CloudFormation template
        response = create_and_deploy_cloudformation(request.worker_count)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
