pipeline {
    agent any

    /*
    =========================================================
      CLÍNICA BORIS - Pipeline CI/CD con Jenkins
      Proyecto: Sistema de Gestión de Pacientes
      Stack: Python + FastAPI + PostgreSQL + Docker
    =========================================================
    */

    environment {
        IMAGE_NAME = "clinica-boris-backend"
        IMAGE_TAG  = "latest"
        APP_PORT   = "8000"
    }

    stages {

        // ─────────────────────────────────────────────────────
        // STAGE 1: CHECKOUT
        // ─────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '=== Obteniendo código fuente desde GitHub ==='
                checkout scm
                sh 'echo "Último commit: $(git log -1 --pretty=format:"%h - %s (%an)")"'
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 2: VERIFICAR ENTORNO
        // ─────────────────────────────────────────────────────
        stage('Verificar Entorno') {
            steps {
                echo '=== Verificando herramientas disponibles ==='
                sh 'docker --version || echo "Docker no disponible"'
                sh 'docker compose version || echo "Docker Compose no disponible"'
                sh 'python3 --version || python --version || echo "Python no disponible"'
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 3: INSTALAR DEPENDENCIAS
        // ─────────────────────────────────────────────────────
        stage('Instalar Dependencias') {
            steps {
                echo '=== Instalando dependencias Python ==='
                sh '''
                    python3 -m venv venv || python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r app/requirements.txt
                    pip install pytest httpx pytest-asyncio
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 4: ANÁLISIS DE CALIDAD
        // ─────────────────────────────────────────────────────
        stage('Análisis de Calidad') {
            steps {
                echo '=== Análisis de calidad del código Python ==='
                sh '''
                    . venv/bin/activate
                    pip install flake8
                    flake8 app/ --max-line-length=120 --exclude=venv --statistics || true
                    echo "Análisis de calidad completado"
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 5: PRUEBAS UNITARIAS
        // ─────────────────────────────────────────────────────
        stage('Ejecutar Pruebas') {
            steps {
                echo '=== Ejecutando pruebas unitarias ==='
                sh '''
                    . venv/bin/activate
                    if [ -d "app/tests" ]; then
                        pytest app/tests/ -v --tb=short
                    else
                        echo "No se encontró carpeta app/tests/ - omitiendo pruebas"
                    fi
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 6: BUILD DOCKER IMAGE
        // ─────────────────────────────────────────────────────
        stage('Build Docker Image') {
            steps {
                echo '=== Construyendo imagen Docker del backend ==='
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker image ls ${IMAGE_NAME}
                """
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 7: DESPLIEGUE CON DOCKER COMPOSE
        // ─────────────────────────────────────────────────────
        stage('Despliegue') {
            steps {
                echo '=== Desplegando la aplicación con Docker Compose ==='
                sh '''
                    docker compose down --remove-orphans || true
                    docker compose up -d --build
                    echo "Esperando a que los servicios inicien..."
                    sleep 10
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 8: VERIFICACIÓN POST-DESPLIEGUE
        // ─────────────────────────────────────────────────────
        stage('Verificación') {
            steps {
                echo '=== Verificando que la API responde ==='
                sh """
                    for i in 1 2 3 4 5; do
                        if curl -sf http://localhost:${APP_PORT}/docs > /dev/null 2>&1; then
                            echo "API respondiendo correctamente en el intento \$i"
                            exit 0
                        fi
                        echo "Intento \$i fallido, esperando 5 segundos..."
                        sleep 5
                    done
                    echo "La API no respondió después de 5 intentos"
                    docker compose logs backend
                    exit 1
                """
            }
        }
    }

    // ─────────────────────────────────────────────────────────
    // POST: solo echo, sin sh, para evitar MissingContextVariableException
    // ─────────────────────────────────────────────────────────
    post {
        success {
            echo '''
============================================
  PIPELINE EXITOSO - Clinica Boris
============================================
  La aplicacion fue desplegada correctamente.
  Accede en: http://localhost:8000/docs
============================================
            '''
        }
        failure {
            echo '''
============================================
  PIPELINE FALLIDO - Clinica Boris
============================================
  Revisa los logs de cada stage para
  identificar el error.
============================================
            '''
        }
        always {
            echo '=== Pipeline finalizado ==='
        }
    }
}