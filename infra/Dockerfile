FROM jenkins/jenkins:lts-jdk21

USER root

# OTIMIZAÇÃO: Um único comando RUN para instalar tudo de uma vez.
# Isso reduz camadas e limpa o lixo do apt-get logo em seguida.
RUN apt-get update && apt-get install -y \
    lsb-release \
    python3-pip \
    curl \
    gnupg \
    git \
    libpq-dev \
    gcc \
    && curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc https://download.docker.com/linux/debian/gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.asc] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y docker-ce-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala plugins
USER jenkins
RUN jenkins-plugin-cli --plugins \
    blueocean \
    docker-workflow \
    git \
    workflow-aggregator \
    pipeline-stage-view