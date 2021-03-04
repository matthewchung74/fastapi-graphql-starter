docker run \
    --network="host" \
    --mount source=fastapi-ariadne,target=/app \
    -p 8000:8000 \
    -it backend_base /bin/bash \
