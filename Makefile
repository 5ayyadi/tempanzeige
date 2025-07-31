# Development commands for tempanzeige project

.PHONY: dev run test clean install

# Start development environment with database
dev:
	docker compose -f dev.docker-compose.yml up -d

# Stop development environment
dev-stop:
	docker compose -f dev.docker-compose.yml down

# Run the bot application
run:
	/home/lee/.cache/pypoetry/virtualenvs/kk-T7TKkND4-py3.12/bin/python main.py

# Install dependencies
install:
	pip3 install -r requirements.txt

# Clean up Docker containers and volumes
clean:
	docker compose -f dev.docker-compose.yml down -v
	docker system prune -f

# Run tests
test:
	/home/lee/.cache/pypoetry/virtualenvs/kk-T7TKkND4-py3.12/bin/python -m pytest --version || echo "No tests configured yet"

# Show logs from development database
logs:
	docker compose -f dev.docker-compose.yml logs -f

