test:
	docker exec kitespots-backend-1 pytest -s -v

freeze:
	poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev

