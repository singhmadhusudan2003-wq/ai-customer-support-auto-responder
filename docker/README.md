# docker/ — Container Assets

The actual `Dockerfile`s live next to the code they build (`backend/Dockerfile`,
`frontend/Dockerfile`), and the orchestration file is `docker-compose.yml` at
the project root — this is the Docker convention (build context needs to be
near the source) and is what `docker-compose up` (run from the project root)
uses automatically.

This folder holds optional extra deployment assets:

- `docker-compose.override.yml.example` — sample override for local dev
  (hot-reload volumes, etc.)

## Quick reference

```bash
# From the project root:
docker-compose up --build          # build + start backend (8000) and frontend (3000)
docker-compose up -d                # same, detached
docker-compose down                 # stop and remove containers
docker-compose logs -f backend      # tail backend logs
```
