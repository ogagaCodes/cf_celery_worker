from pydantic import BaseModel

class DeploymentRequest(BaseModel):
    worker_count: int
