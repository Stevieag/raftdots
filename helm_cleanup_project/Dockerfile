FROM google/cloud-sdk:latest

RUN apt-get update && apt-get install -y python3 python3-pip

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

COPY helm_cleanup.py /app/helm_cleanup.py

CMD ["python3", "/app/helm_cleanup.py"]
