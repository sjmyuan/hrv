APP_IMAGE = "jiangmingshang/hrv"
PROJECT_DIR = $(shell pwd )

build:
	docker build -t $(APP_IMAGE) .
	docker push $(APP_IMAGE)

run:
	docker run --rm \
		-p 8081:8080 \
		-v $(PROJECT_DIR):/data \
		$(APP_IMAGE) 
