APP_IMAGE = "jiangmingshang/hrv"
PROJECT_DIR = $(shell pwd )

build:
	docker build -t $(APP_IMAGE) .
	docker push $(APP_IMAGE)

run:
	mkdir $(PROJECT_DIR)/data
	docker run --rm \
		-p 8080:8080 \
		-v $(PROJECT_DIR)/data:/data \
		$(APP_IMAGE) 
