FROM jenkins/jenkins:lts-jdk21

USER root

# 1. Instala utilitários básicos e transporte HTTPS
RUN apt-get update && apt-get install -y \
    lsb-release \
    python3-pip \
    curl \
    gnupg \
    git \
    libpq-dev \
    gcc

# 2. Adiciona a chave GPG oficial do Docker
RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
  https://download.docker.com/linux/debian/gpg

# 3. Adiciona o repositório oficial do Docker
RUN echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

# 4. Instala o Docker CLI (Cliente)
RUN apt-get update && apt-get install -y docker-ce-cli

# 5. Instala plugins essenciais do Jenkins automaticamente
# Blue Ocean é ótimo para visualizar pipelines no TCC
USER jenkins
RUN jenkins-plugin-cli --plugins \
    blueocean \
    docker-workflow \
    git \
    workflow-aggregator \
    pipeline-stage-view