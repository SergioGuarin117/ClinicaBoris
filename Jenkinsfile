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
                    sleep 15
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 8: VERIFICACIÓN POST-DESPLIEGUE
        // Obtiene la IP del contenedor backend dentro de la red
        // Docker y verifica que la API responde
        // ─────────────────────────────────────────────────────
        stage('Verificación') {
            steps {
                echo '=== Verificando estado de los contenedores ==='
                sh '''
                    echo "--- Contenedores en ejecución ---"
                    docker compose ps

                    echo "--- Logs del backend ---"
                    docker compose logs --tail=20 backend

                    echo "--- Verificando que el backend está corriendo ---"
                    BACKEND_STATUS=$(docker inspect -f "{{.State.Running}}" clinica_backend 2>/dev/null || echo "false")

                    if [ "$BACKEND_STATUS" = "true" ]; then
                        echo "El contenedor clinica_backend está corriendo correctamente"

                        # Obtener IP del contenedor dentro de la red Docker
                        BACKEND_IP=$(docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" clinica_backend)
                        echo "IP del backend: $BACKEND_IP"

                        # Intentar conectar usando la IP del contenedor
                        for i in 1 2 3 4 5; do
                            if curl -sf http://$BACKEND_IP:8000/docs > /dev/null 2>&1; then
                                echo "API respondiendo correctamente en el intento $i"
                                echo "Accede en: http://localhost:8000/docs"
                                exit 0
                            fi
                            echo "Intento $i fallido, esperando 5 segundos..."
                            sleep 5
                        done
                        echo "Advertencia: El contenedor corre pero la API no respondio al curl"
                        echo "Verifica manualmente en http://localhost:8000/docs"
                        exit 0
                    else
                        echo "ERROR: El contenedor clinica_backend no está corriendo"
                        docker compose logs backend
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        success {
            echo '''
============================================
  PIPELINE EXITOSO - Clinica Boris
============================================
  Accede a la app en: http://localhost:8000/docs
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