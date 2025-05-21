from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import boto3
from botocore.exceptions import BotoCoreError, ClientError

router = APIRouter( tags=["Face Matching"])

# Rekognition client (ensure region is correct and supported)
rekognition = boto3.client("rekognition", region_name="us-east-1")


@router.post("/match-face")
async def match_faces(
    source: UploadFile = File(...),
    target: UploadFile = File(...),
):
    try:
        source_bytes = await source.read()
        target_bytes = await target.read()

        response = rekognition.compare_faces(
            SourceImage={"Bytes": source_bytes},
            TargetImage={"Bytes": target_bytes},
            SimilarityThreshold=80,
        )

        matches = response.get("FaceMatches", [])
        if matches:
            similarity = matches[0]["Similarity"]
            return {"match": True, "similarity": similarity}
        else:
            return {"match": False, "similarity": 0}

    except (BotoCoreError, ClientError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AWS Rekognition error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
