from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Literal
from julep import Julep
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Load from environment
TASK_ID = os.getenv("TASK_ID")
JULEP_API_KEY = os.getenv("JULEP_API_KEY")

# Initialize Julep
julep_client = Julep(api_key=JULEP_API_KEY)

# Input schema with validation
class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=100)
    format: Literal["summary", "bullet points", "short report"]

    @validator("topic")
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError("Topic must not be empty or whitespace.")
        return v.strip()

@app.post("/research")
async def perform_research(payload: ResearchRequest):
    try:
        task_input = {
            "topic": payload.topic,
            "output_format": payload.format
        }

        execution = julep_client.executions.create(
            task_id=TASK_ID,
            input=task_input
        )

        while True:
            result = julep_client.executions.get(execution.id)
            if result.status in ['succeeded', 'failed', 'error']:
                break
            time.sleep(5)

        if result.status == "succeeded":
            try:
                message_content = result.output["choices"][0]["message"]["content"]
                return {"response": message_content}
            except Exception:
                raise HTTPException(status_code=500, detail="Unexpected response format from agent.")
        else:
            return {
                "status": result.status,
                "error": "Task did not complete successfully.",
                "output": result.output
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
