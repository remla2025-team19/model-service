# Model Service

Infers sentiment of user feedback from the trained model.

## Environment variables

These can be found in the Dockerfile. The default values are:

```dockerfile
ENV MODEL_SERVICE_HOST=0.0.0.0
ENV MODEL_SERVICE_PORT=8080
ENV MODEL_VERSION=v1.0.11
ENV MODEL_CACHE_DIR=/app/models_cache
```

### MODEL_VERSION

The `MODEL_VERSION` environment variable specifies which version of the sentiment model to download and use. This is a required environment variable that must be set to a valid model version tag from the [model-training releases](https://github.com/remla2025-team19/model-training/releases).

### MODEL_CACHE_DIR

The `MODEL_CACHE_DIR` environment variable specifies where downloaded models will be stored. Inside the container, this defaults to `/app/models_cache`. When running the container, you should mount a volume at this location to persist the downloaded models between container restarts.

For the above value of host, the service can be accessed via the host machine. For other values, the service must be accessed from within the container.

## Model Caching

The service uses a volume mounted at `/app/models_cache` to cache downloaded models. This allows models to persist between container restarts and prevents unnecessary downloads.

Sample commands to build and run the service with custom host, port and model version values:

```bash
docker build -t model_service .
docker run -it --rm -p 8080:8080 \
  -e MODEL_SERVICE_HOST=0.0.0.0 \
  -e MODEL_SERVICE_PORT=8080 \
  -e MODEL_VERSION=v1.0.11 \
  -e MODEL_CACHE_DIR=/app/models_cache \
  -v ./models_cache:/app/models_cache \
  model_service
```

Now the service is running within the ccontainer. To test, make use of another container

```bash
docker exec -it <CONTAINER_ID> bash
apt update
apt install curl
curl -X POST "http://localhost:8080/predict" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"review\": \" The food is bad.\"}"
```

## Pull image from GHCR

```bash
docker pull ghcr.io/remla2025-team19/model-service:0.0.5
```

## Versioning Information (relevant to A1)

We have implemented workflows that will update timestamps for a pre-release in the format `v{MAJOR}.{MINOR}.{PATCH}-pre-{TIMESTAMP}`.
 
Pre-release tags are updated on a simple git push. For all other `git push` operations, the `auto-tag.yml` workflow will update the `pre` tags with a timestamp. When a release is made, then the corresponding version in `lib-version` is also updated.

```bash
git push
```

In order to create a release. Check the current pre-release information. This can be done using commands like 
```bash
git ls-remote --tags --sort="v:refname" origin
```
Choose the current pre-release version. Create a tag and push. This will create the a release with the versioning `v{MAJOR}.{MINOR}.{PATCH}`.

```bash
git tag v0.0.28
git push origin v0.0.28
```