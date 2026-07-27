"""
Sanity check that Dockerfile and docker-compose.yml are syntactically valid.
"""
import os

import yaml


def test_dockerfile_exists():
    assert os.path.exists("Dockerfile")


def test_docker_compose_is_valid_yaml():
    with open("docker-compose.yml") as f:
        config = yaml.safe_load(f)
    assert "services" in config
    assert "web" in config["services"]
    assert "db" in config["services"]
    assert "redis" in config["services"]


def test_dockerignore_excludes_env():
    with open(".dockerignore") as f:
        content = f.read()
    assert ".env" in content