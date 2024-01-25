# Run python docker container to install dependencies and run scrapper and update publications.json

build:
	docker build -t publications-scrapper .

update:
	rm -f publications.json
	docker run --rm -v $(PWD):/app publications-scrapper python3 /app/scrapper.py