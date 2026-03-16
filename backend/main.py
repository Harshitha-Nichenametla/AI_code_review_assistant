from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from analyzer import analyze_code

app = FastAPI(title="AI Code Review API", version="1.0.0")

# Allow browser frontends (including file:// and localhost) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten to specific origins in production
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class CodeInput(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def code_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("code must not be empty")
        return v


@app.get("/health")
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}


@app.post("/review")
def review_code(data: CodeInput):
    """
    Analyze the submitted Python code and return a quality score with issues.
    """
    try:
        result = analyze_code(data.code)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}")
