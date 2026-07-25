import os


def service_name() -> str:
    return os.getenv("PROJECT_SERVICE_NAME", "demo-service")
