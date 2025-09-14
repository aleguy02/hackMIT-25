DOCKER_COMPOSE_TEMPLATES = {
    "flask-backend": {
        "build": {
            "context": "./backend",
            "dockerfile": "Dockerfile"
        },
        "container_name": "flask-backend",
        "restart": "always",
        "env_file": [".env"],
        "networks": ["app-network"],
    },

    "react-frontend": {
        "build": {
            "context": "./frontend",
            "dockerfile": "Dockerfile"
        },
        "container_name": "react-frontend",
        "restart": "always",
        "env_file": [".env"],
        "networks": ["app-network"],
    },
    
    "nginx": {
        "container_name": "nginx",
        "image": "jonasal/nginx-certbot",
        "restart": "always",
        "ports": ["80:80", "443:443"],
        "volumes": [
            "nginx_secrets:/etc/letsencrypt",
            "./nginx_conf:/etc/nginx/user_conf.d"
        ],
        "networks": ["app-network"],
    },
    
    "mysql": {
        "container_name": "mysql",
        "image": "mariadb:latest",
        "restart": "always",
        "env_file": [".env"],
        "volumes": ["mysql_data:/var/lib/mysql"],
        "networks": ["app-network"],
        "healthcheck": {
            "test": "mariadb-admin ping -h localhost --password=$MYSQL_ROOT_PASSWORD",
            "interval": "30s",
            "timeout": "10s",
            "retries": 5,
            "start_period": "30s"
        },
    },

    "redis": {
        "container_name": "redis",
        "image": "redis:7-alpine",
        "restart": "always",
        "volumes": ["redis_data:/data"],
        "networks": ["app-network"],
        "healthcheck": {
            "test": "redis-cli ping",
            "interval": "30s",
            "timeout": "10s",
            "retries": 5,
            "start_period": "30s"
        },
    },

    "rabbitmq": {
        "container_name": "rabbitmq",
        "image": "rabbitmq:4-management",
        "restart": "always",
        "networks": ["app-network"],
        "environment": {
            "RABBITMQ_DEFAULT_USER": "${RABBITMQ_DEFAULT_USER}",
            "RABBITMQ_DEFAULT_PASS": "${RABBITMQ_DEFAULT_PASS}"
        },
        "ports": ["15672:15672", "5672:5672"],
        "healthcheck": {
            "test": " rabbitmq-diagnostics -q ping",
            "interval": "30s",
            "timeout": "10s",
            "retries": 3,
        }
    }
}

COMPOSE_METADATA = {
    "version": "3",
    "networks": {
        "app-network": {
            "driver": "bridge"
        }
    },
    "volumes": {
        "mysql_data": None,
        "nginx_secrets": None,
        "redis_data": None
    }
}

def compose_config_factory(components) -> dict:
    """
    Generate a Docker Compose service configuration.
    Inputs: set of strings with the following possible values: react-frontend | flask-backend | nginx | mysql | redis | rabbitmq
    Outputs: json representation of compose.yaml file
    """
    components = list(components)
    compose_config = {}
    compose_config["version"] = COMPOSE_METADATA["version"]
    compose_config["networks"] = COMPOSE_METADATA["networks"]


    compose_services = {}
    
    for component in components:
        if component in DOCKER_COMPOSE_TEMPLATES:
            # Deep copy the template to avoid modifying the original
            import copy
            compose_services[component] = copy.deepcopy(DOCKER_COMPOSE_TEMPLATES[component])
    

    ## Dependencies
    backend_deps = {}
    if "mysql" in components:
        backend_deps["mysql"] = {"condition": "service_healthy"}
    if "redis" in components:
        backend_deps["redis"] = {"condition": "service_healthy"}
        if "mysql" in components:
            compose_services["redis"]["depends_on"] = {"mysql": {"condition": "service_healthy"}}
    if "rabbitmq" in components:
        backend_deps["rabbitmq"] = {"condition": "service_healthy"}

    if "flask-backend" in components and backend_deps:
        compose_services["flask-backend"]["depends_on"] = backend_deps
    
    if "nginx" not in components and "flask-backend" in components:
        compose_services["flask-backend"]["ports"] = ["5000:5000"]
    
    if "nginx" not in components and "flask-backend" in components and "react-frontend" in components:
        compose_services["flask-backend"]["ports"] = ["5000:5000"]
        compose_services["react-frontend"]["ports"] = ["3000:3000"]
        compose_services["react-frontend"]["depends_on"] = ["flask-backend"]
    
    
    ## Volumes
    compose_config["volumes"] = {}
    if "nginx" in components:
        compose_config["volumes"]["nginx_secrets"] = COMPOSE_METADATA["volumes"]["nginx_secrets"]
    if "mysql" in components:
        compose_config["volumes"]["mysql_data"] = COMPOSE_METADATA["volumes"]["mysql_data"]
    if "redis" in components:
        compose_config["volumes"]["redis_data"] = COMPOSE_METADATA["volumes"]["redis_data"]

    compose_config["services"] = compose_services    
    return compose_config
