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
        // Nombre de la imagen Docker del backend
        IMAGE_NAME = "clinica-boris-backend"
        IMAGE_TAG  = "latest"

        // Puerto donde corre la app
        APP_PORT = "8000"

        // Directorio de trabajo dentro del contenedor
        WORKDIR = "/app"

        // Credenciales de base de datos (configurar en Jenkins > Credentials)
        POSTGRES_USER     = credentials('clinica-postgres-user')
        POSTGRES_PASSWORD = credentials('clinica-postgres-password')
        POSTGRES_DB       = "clinica"
    }

    // Disparadores automáticos: ejecuta el pipeline en cada push a 'main'
    triggers {
        githubPush()
    }

    stages {

        // ─────────────────────────────────────────────────────
        // STAGE 1: CHECKOUT
        // Clona el repositorio desde GitHub
        // ─────────────────────────────────────────────────────
        stage('📥 Checkout') {
            steps {
                echo '=== Obteniendo código fuente desde GitHub ==='
                checkout scm
                sh 'echo "Rama: $(git branch --show-current)"'
                sh 'echo "Último commit: $(git log -1 --pretty=format:"%h - %s (%an)")"'
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 2: VERIFICAR ENTORNO
        // Confirma que Docker y Python están disponibles
        // ─────────────────────────────────────────────────────
        stage('🔍 Verificar Entorno') {
            steps {
                echo '=== Verificando herramientas disponibles ==='
                sh 'docker --version'
                sh 'docker compose version'
                sh 'python3 --version || python --version'
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 3: INSTALAR DEPENDENCIAS
        // Instala las librerías Python del proyecto en un entorno virtual
        // ─────────────────────────────────────────────────────
        stage('📦 Instalar Dependencias') {
            steps {
                echo '=== Instalando dependencias Python ==='
                sh '''
                    python3 -m venv venv || python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r app/requirements.txt
                    pip install pytest httpx pytest-asyncio  # para pruebas
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 4: ANÁLISIS DE CALIDAD DE CÓDIGO
        // Revisa el estilo y posibles errores con flake8
        // ─────────────────────────────────────────────────────
        stage('🔎 Análisis de Calidad (Linting)') {
            steps {
                echo '=== Análisis de calidad del código Python ==='
                sh '''
                    . venv/bin/activate
                    pip install flake8
                    # Analiza el código pero no falla el pipeline por advertencias de estilo
                    flake8 app/ --max-line-length=120 --exclude=venv --statistics || true
                    echo "Análisis de calidad completado"
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 5: PRUEBAS UNITARIAS
        // Ejecuta los tests con pytest
        // ─────────────────────────────────────────────────────
        stage('🧪 Ejecutar Pruebas') {
            steps {
                echo '=== Ejecutando pruebas unitarias ==='
                sh '''
                    . venv/bin/activate
                    # Busca tests en la carpeta app/tests si existe
                    if [ -d "app/tests" ]; then
                        pytest app/tests/ -v --tb=short
                    else
                        echo "⚠️  No se encontró carpeta de tests en app/tests/"
                        echo "   Crea app/tests/test_main.py para agregar pruebas"
                    fi
                '''
            }
            post {
                always {
                    echo 'Stage de pruebas finalizado'
                }
                failure {
                    echo '❌ Las pruebas fallaron. Revisa los logs arriba.'
                }
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 6: BUILD DOCKER IMAGE
        // Construye la imagen Docker del backend
        // ─────────────────────────────────────────────────────
        stage('🐳 Build Docker Image') {
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
        // Detiene contenedores anteriores y levanta los nuevos
        // ─────────────────────────────────────────────────────
        stage('🚀 Despliegue con Docker Compose') {
            steps {
                echo '=== Desplegando la aplicación con Docker Compose ==='
                sh '''
                    # Detener y eliminar contenedores anteriores si existen
                    docker compose down --remove-orphans || true

                    # Levantar todos los servicios (db + backend)
                    docker compose up -d --build

                    echo "Esperando a que los servicios inicien..."
                    sleep 10
                '''
            }
        }

        // ─────────────────────────────────────────────────────
        // STAGE 8: VERIFICACIÓN POST-DESPLIEGUE
        // Comprueba que la API está respondiendo correctamente
        // ─────────────────────────────────────────────────────
        stage('✅ Verificación del Despliegue') {
            steps {
                echo '=== Verificando que la API responde ==='
                sh """
                    # Intenta conectar a la API hasta 5 veces
                    for i in 1 2 3 4 5; do
                        if curl -sf http://localhost:${APP_PORT}/docs > /dev/null 2>&1; then
                            echo "✅ API respondiendo correctamente en el intento \$i"
                            exit 0
                        fi
                        echo "Intento \$i fallido, esperando 5 segundos..."
                        sleep 5
                    done
                    echo "❌ La API no respondió después de 5 intentos"
                    docker compose logs backend
                    exit 1
                """
            }
        }
    }

    // ─────────────────────────────────────────────────────────
    // POST: Acciones después del pipeline (éxito, fallo, siempre)
    // ─────────────────────────────────────────────────────────
    post {
        success {
            echo '''
            ============================================
            ✅  PIPELINE EXITOSO - Clínica Boris
            ============================================
            La aplicación fue desplegada correctamente.
            Accede en: http://localhost:8000/docs
            ============================================
            '''
        }
        failure {
            echo '''
            ============================================
            ❌  PIPELINE FALLIDO - Clínica Boris
            ============================================
            Revisa los logs de cada stage para
            identificar el error.
            ============================================
            '''
            // Opcional: limpia contenedores si hay fallo
            sh 'docker compose down || true'
        }
        always {
            echo '=== Pipeline finalizado. Limpiando entorno virtual ==='
            sh 'rm -rf venv || true'
        }
    }
}