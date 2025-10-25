# Demperm - Social

## Create development environment
```bash
uv venv .venv
source .venv/bin/activate
uv sync --dev
```

### Launch social server
```bash
python ./social_api/manage.py runserver 8000
```

You can now access to the API specification on the [Swagger page](http://127.0.0.1:8000/api/v1/swagger/).
