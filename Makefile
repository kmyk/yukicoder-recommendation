.PHONY: build

env_variables := $(shell ruby -r yaml -e 'YAML.load(STDIN)["env_variables"].each { |k, v| puts "\#{k}=\#{v}" }' < frontend/secret.yaml )

preview:
	env ${env_variables} python3 frontend/server.py
scrape/favorite:
	env ${env_variables} python3 backend/main.py favorite
scrape/submission:
	env ${env_variables} python3 backend/main.py submission
scrape/problem:
	env ${env_variables} python3 backend/main.py problem
