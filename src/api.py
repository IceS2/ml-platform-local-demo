import logging
from typing import List
from fastapi import FastAPI, UploadFile
from src.classifier import BirdClassifier, BirdData
from src.logger import configure_logger

logger = logging.getLogger(__name__)

app = FastAPI()
model = BirdClassifier()

configure_logger(logger, app)


@app.get("/")
async def ping() -> dict:
    """Ping endpoint for testing purposes.
    """
    return {"status": "OK"}


@app.post("/predict")
async def predict(image: UploadFile) -> List[BirdData]:
    """Predict endpoint. Returns the top three results from the model output.
    Args
    ----
        image (UploadFile): Image to feed the model.
    Returns
    -------
        list with 3 dictionaries like '{"name": <NAME>, "score": <SCORE>}',
        ordered from highest to lowest score.
    """
    image_content = await image.read()
    prediction = model.predict(image_content)
    logger.info(f"Prediction: {prediction}")
    return prediction



