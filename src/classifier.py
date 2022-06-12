import os
import urllib.request
import numpy as np
import logging

import tensorflow.compat.v2 as tf
import tensorflow_hub as hub
import cv2

from typing import List, Tuple, Dict, Any

# Getting some unknown linter errors, disable everything to get this to production asap
# pylint: disable-all

logger = logging.getLogger(__name__)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable Tensorflow logging

MODEL_URL = 'https://tfhub.dev/google/aiy/vision/classifier/birds_V1/1'
LABELS_URL = 'https://www.gstatic.com/aihub/tfhub/labelmaps/aiy_birds_V1_labelmap.csv'

# Type aliases for better semantics
BirdId = int
BirdData = Dict[str, Any]
SortedLabels = List[Tuple[BirdId, BirdData]]

class BirdClassifier:
    def __init__(self, model_url: str = MODEL_URL,
                 labels_url: str = LABELS_URL) -> None:
        self.model = self._load_model(model_url)
        self.labels = self._load_and_cleanup_labels(labels_url)

    def predict(self, image: bytes, n: int = 3) -> List[BirdData]:
        """ Uses the model to predict the top N results based on the image given.

        Args
        ----
            image (bytes): Image bytes to use for prediction.
            n (int, optional, default = 3): Number of results to return.

        Returns
        -------
            List[BirdData]: Top N results with proper BirdData.
        """
        logger.info(f"Predicting top {n} results for image")
        image = self._prepare_image(image)
        # Generate tensor
        image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
        image_tensor = tf.expand_dims(image_tensor, 0)
        model_raw_output = self.model.call(image_tensor).numpy()
        sorted_labels = self._order_birds_by_result_score(model_raw_output)
        results = self._get_top_n_results(n, sorted_labels)
        logger.info(f"Prediction was successful")
        return results

    def _load_model(self, model_url: str) -> hub.KerasLayer:
        """ Loads the Model from TF Hub.

        Args
        ----
            model_url (str): TF Hub URL from which to download the model

        Returns
        -------
            KerasLayer from SavedModel.
        """
        logger.debug(f"Loading Model from {model_url}")
        model = hub.KerasLayer(model_url)
        logger.debug(f"Model loaded")
        return model

    def _load_and_cleanup_labels(self,
                                 labels_url: str) -> Dict[BirdId, BirdData]:
        """ Loads the labels from the given URL and parses it into a dict as
        '{<BIRD_ID>: {"name": <BIRD_NAME>}}'

        Args
        ----
            labels_url (str): URL from which to download the labels.

        Returns
        -------
            Dict[BirdId, BirdData]: dictionary with all the bird names,
                mapped to their IDs.
        """
        logger.debug(f"Loading labels from {labels_url}")
        bird_labels_raw = urllib.request.urlopen(labels_url)
        logger.debug(f"Labels loaded")

        logger.debug(f"Parsing labels")
        bird_labels_lines = [
            line.decode('utf-8').replace('\n', '')
            for line in bird_labels_raw.readlines()
        ]
        bird_labels_lines.pop(0)  # remove header (id, name)

        birds = {}
        for bird_line in bird_labels_lines:
            bird_id = int(bird_line.split(',')[0])
            bird_name = bird_line.split(',')[1]
            birds[bird_id] = {'name': bird_name}

        logger.debug(f"Labels parsed")
        return birds

    def _prepare_image(self, image: bytes) -> bytes:
        """ Prepares the image to feed it to the model.

        Args
        ----
            image (bytes): Image bytes to use for prediction.

        Returns
        -------
            Image (bytes): Prepared image to use for prediction.
        """
        logger.debug(f"Preparing image")
        image_array = np.fromstring(image, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (224, 224))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image / 255
        logger.debug("Image prepared")
        return image

    def _order_birds_by_result_score(self,
                                     model_raw_output: np.ndarray) -> SortedLabels:
        """ Sorts labels based on score, from highest to lowest.

        Args
        ----
            model_raw_output (np.ndarray): Model output from given image,
                converted to np.ndarray.

        Returns
        -------
            SortedLabels: List[Tuple[BirdId, BirdData]],
                ordered based on score, from highest to lowest.
        """
        logger.debug(f"Sorting labels by score based on {model_raw_output}")
        for index, value in np.ndenumerate(model_raw_output):
            bird_index = index[1]
            self.labels[bird_index]['score'] = value

        sorted_labels = sorted(
            self.labels.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        logger.debug("Labels sorted")
        return sorted_labels

    def _get_top_n_results(self, n: int,
                           sorted_labels: SortedLabels) -> List[BirdData]:
        """ Returns the Top N results from the model.

        Args
        ----
            birds_names_with_results_ordered (SortedLabels): List of tuples
                with BirdId and BirdData, ordered from highest to lowest score.

        Returns
        -------
            List[BirdData]: Top N results from the model.
        """
        logger.debug(f"Getting top {n} results.")
        results = [
            {
                "name": bird[1]["name"],
                "score": bird[1]["score"].item()
            }
            for bird in sorted_labels[:n]
        ]
        logger.debug(f"Results done")
        return results

