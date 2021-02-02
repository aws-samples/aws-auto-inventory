.PHONY: init
init:
	python3 -m venv .venv
	@( \
       source .venv/bin/activate; \
	   pip install --upgrade pip ; \
	   pip install --upgrade pyinstaller ; \
       pip install -r requirements.txt; \
    )

.PHONY: clean
clean:
	@rm -rf build/ dist/ *.spec log/ output/ build.txt __pycache__/ aai/__pycache__/ 

.PHONY: dist
dist: clean
	@( \
       source .venv/bin/activate; \
	   pyinstaller --name aws-auto-inventory --clean --onefile --hidden-import cmath --log-level=DEBUG cli.py 2> build.txt; \
    )

# Build the Docker image, create a container, extract the binary and copy it under dist/, stop and delete the container
.PHONY: docker/build/ubuntu
docker/build/ubuntu:
	@docker build -f Dockerfile.Ubuntu.Bionic -t aws-auto-inventory:bionic . ;\
	docker create -ti --name aws-auto-inventory aws-auto-inventory:bionic bash ;\
	mkdir -p dist && docker cp aws-auto-inventory:/opt/aws-auto-inventory/dist/aws-auto-inventory-linux-amd64 dist/aws-auto-inventory-linux-amd64  ;\
	docker container stop aws-auto-inventory ;\
	docker container rm aws-auto-inventory ;\

.PHONY: docker/run/ubuntu
docker/run/ubuntu:
	docker container run -it "aws-auto-inventory:bionic" /bin/bash

# TODO: assume virtual environment when executing container, and push container to ECR

.PHONY: docker/push/ubuntu
docker/push/ubuntu:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 875835244221.dkr.ecr.us-east-1.amazonaws.com ;\
	docker tag aws-auto-inventory:bionic 875835244221.dkr.ecr.us-east-1.amazonaws.com/aws-auto-inventory:bionic ;\
	docker push 875835244221.dkr.ecr.us-east-1.amazonaws.com/aws-auto-inventory:bionic ;\


.PHONY: run/it
run/it:
	docker container run -it "lambda-layer:latest" /bin/bash