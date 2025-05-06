# Model Service

Infers sentiment of user feedback from the trained model.

## Environment variables for host and Port
These can be found in the Dockerfile. The default values are:

```dockerfile
ENV MODEL_SERVICE_HOST=0.0.0.0
ENV MODEL_SERVICE_PORT=8080
```

For the above value of host, the service can be accessed via the host machine. For other values, the service must be accessed from within the container.
Sample commands to build and run the service with custom host and port values.

```bash
docker build -t model_service .
docker run -it --rm -p8076 -e MODEL_SERVICE_HOST=127.13.5.13 -e MODEL_SERVICE_PORT=17 model_service
```
Now the service is running within the ccontainer. To test, make use of another container
```bash
docker exec -it <CONTAINER_ID> bash
apt update
apt install curl
curl -X POST "http://127.13.5.13:17/predict" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"review\": \" The food is bad.\"}"
```
## Pull image from GHCR
```bash
docker pull ghcr.io/remla2025-team19/model-service:0.0.5
```