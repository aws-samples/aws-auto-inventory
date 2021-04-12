# You can change this tag to suit your needs
TAG=$(shell date +%Y%m%d)
OS=$(shell uname -s | tr A-Z a-z)
ARCH=$(shell uname -m | tr A-Z a-z)

.PHONY: init
init:
	python3 -m venv .venv
	@( \
       . .venv/bin/activate; \
	   pip install --upgrade pip ; \
	   pip install --upgrade pyinstaller ; \
       pip install -r requirements.txt; \
    )

.PHONY: clean
clean:
	@rm -rf build/ dist/ *.spec log/ output/ build.txt __pycache__/ aai/__pycache__/ 

.PHONY: build
build: clean
	@( \
       . .venv/bin/activate; \
	   pyinstaller --name aws-auto-inventory-$(OS)-$(ARCH) --clean --onefile --hidden-import cmath --log-level=DEBUG cli.py 2> build.txt; \
    )

# Build the Docker image, create a container, extract the binary and copy it under dist/, stop and delete the container
.PHONY: docker/build/ubuntu
docker/build/ubuntu:
	@docker build -f Dockerfile.Ubuntu.Bionic -t aws-auto-inventory:$(TAG) . \
	&& docker create -ti --name aws-auto-inventory aws-auto-inventory:$(TAG) bash \
	&& mkdir -p dist && docker cp aws-auto-inventory:/opt/aws-auto-inventory/dist/aws-auto-inventory-linux-amd64 dist/aws-auto-inventory-linux-amd64 \
	&& docker container stop aws-auto-inventory \
	&& docker container rm aws-auto-inventory ;\

.PHONY: docker/run/ubuntu
docker/run/ubuntu:
	@docker container run -it "aws-auto-inventory:$(TAG)" /bin/bash

# TODO: assume virtual environment when executing container, and push container to ECR

.PHONY: docker/push/ubuntu
docker/push/ubuntu:
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REPO_ID).dkr.ecr.$(AWS_REGION).amazonaws.com \
	&& docker tag aws-auto-inventory:$(TAG) $(ECR_REPO_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/aws-auto-inventory:$(TAG) \
	&& docker push $(ECR_REPO_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/aws-auto-inventory:$(TAG) ;\
