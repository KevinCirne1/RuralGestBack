pipeline {
    agent {
        docker { 
            image 'python:3.9-slim' 
            // CONEXÃO DE REDE: O container de teste entra na rede da infra
            // para conseguir falar com o container 'ruralgest_redis'
            args '-u root --network ruralgest-net'
        }
    }

    environment {
        // Agora apontamos para o nome do serviço definido no docker-compose
        DATABASE_URL = "sqlite:///:memory:" // Mantemos SQLite para o teste não apagar seu banco real
        SECRET_KEY = "chave-secreta-de-teste"
        
        // CONFIGURAÇÃO DO REDIS REAL
        REDIS_HOST = "ruralgest_redis" 
        REDIS_PORT = "6379"
        CACHE_TYPE = "RedisCache"
    }

    stages {
        stage('Ambiente e Dependências') {
            steps {
                script {
                    sh 'apt-get update && apt-get install -y gcc libpq-dev'
                    sh 'python3 -m venv venv'
                    sh 'venv/bin/pip install --upgrade pip'
                    sh 'venv/bin/pip install -r requirements.txt'
                    sh 'venv/bin/pip install pytest redis' // Instalamos a lib redis para o teste
                }
            }
        }

        stage('Verificação de Conexão Redis') {
            steps {
                script {
                    echo "Testando conexão com o Redis em: ${env.REDIS_HOST}"
                    // Pequeno script python para validar se o Redis está acessível antes de seguir
                    sh """
                    venv/bin/python -c "
                    import redis
                    import sys
                    try:
                        r = redis.Redis(host='${env.REDIS_HOST}', port=6379)
                        if r.ping():
                            print('Conexão com Redis OK!')
                    except Exception as e:
                        print(f'Falha ao conectar no Redis: {e}')
                        sys.exit(1)
                    "
                    """
                }
            }
        }

        stage('Testes Automatizados') {
            steps {
                script {
                    sh 'venv/bin/python --version'
                    echo 'Executando lógica com RedisCache ativo...'
                    // O Flask aqui usará o Redis real do container ruralgest_redis
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}