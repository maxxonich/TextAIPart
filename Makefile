DOCKER_COMPOSE=docker compose

send-message-to-broker:
	$(DOCKER_COMPOSE) exec worker python -m rabbit.test
