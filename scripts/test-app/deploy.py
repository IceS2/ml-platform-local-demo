import sys
import subprocess
import tempfile
from model_registry import insert_dummy_data, get_model_info

DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {model_name}
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      model: {model_name}
  template:
    metadata:
      labels:
        model: {model_name}
      annotations:
        isModel: "true"
        model: "{model_name}"
        modelVersion: "{model_version}"
        modelId: "{model_id}"
    spec:
      containers:
      - name: {model_name}
        image: {model_image}:{model_version}
        imagePullPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: {model_name}-service
  namespace: default
spec:
  type: ClusterIP
  selector:
    model: {model_name}
  ports:
  - port: 8000
    targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {model_name}-ingress
spec:
  rules:
    - host: localhost
      http:
        paths:
          - pathType: ImplementationSpecific
            path: "/"
            backend:
              service:
                name: {model_name}-service
                port:
                  number: 8000
"""

def insert_model_data(model_name: str, image: str, version: str):
    insert_dummy_data(model_name, image, version)

def deploy_model_from_registry(model_name: str, version: str):
    model_id, image = get_model_info(model_name, version)
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/deployment.yaml", "w") as tmpfile:
        # with tempfile.TemporaryFile() as tmpfile:
            tmpfile.write(
                    DEPLOYMENT.format(
                        model_name=model_name,
                        model_version=version,
                        model_image=image,
                        model_id=model_id
                    ),
            )
        subprocess.run(["kubectl", "config", "use-context", "kind-default"])
        subprocess.run(["kubectl", "apply", "-f", f"{tmpdir}/deployment.yaml"])

if __name__ == "__main__":
    if len(sys.argv) == 2:
        model_name = sys.argv[1]
        image = "ices2/bird-model-endpoint"
        version = "1"
    if len(sys.argv) == 4:
        model_name = sys.argv[1]
        image = sys.argv[2]
        version = sys.argv[3]
    else:
        raise ValueError("This Script only accepts either one or three arguments")

    insert_model_data(model_name, image, version)
    deploy_model_from_registry(model_name, version)

