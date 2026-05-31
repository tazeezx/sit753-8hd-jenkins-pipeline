pipeline {
    agent any

    environment {
        IMAGE_NAME    = "movie-app"
        SONAR_PROJECT = "movie-crud-flask"
    }

    stages {

        stage('Build') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest ."
                echo "Built image: ${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }

        stage('Test') {
            steps {
                sh """
                    docker run --rm \
                        -v \${WORKSPACE}:/app \
                        -w /app \
                        ${IMAGE_NAME}:${BUILD_NUMBER} \
                        sh -c "pytest tests/ --junitxml=test-results.xml --cov=. --cov-report=xml:coverage.xml -v"
                """
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Code Quality') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        docker run --rm \
                            --network jenkins-net \
                            -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                            -e SONAR_TOKEN="$SONAR_AUTH_TOKEN" \
                            -v "$WORKSPACE":/usr/src \
                            sonarsource/sonar-scanner-cli \
                            -Dsonar.projectKey=movie-crud-flask \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3.11 \
                            -Dsonar.exclusions="tests/**,**/*.html,**/*.css" \
                            -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }

        stage('Security') {
            steps {
                sh """
                    docker run --rm \
                        -v \${WORKSPACE}:/app \
                        -w /app \
                        ${IMAGE_NAME}:${BUILD_NUMBER} \
                        sh -c "pip install bandit pip-audit --quiet && \
                               bandit -r . --exclude ./tests -f txt -o bandit-report.txt || true && \
                               pip-audit -r requirements.txt -f json -o pip-audit-report.json || true"
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.txt,pip-audit-report.json',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                sh 'docker stop movie-staging || true'
                sh 'docker rm   movie-staging || true'
                sh "docker run -d --name movie-staging -p 5001:5000 ${IMAGE_NAME}:${BUILD_NUMBER}"
                sh 'sleep 5'
                sh 'curl -f http://host.docker.internal:5001/health'
                echo 'Staging deployed at http://localhost:5001'
            }
        }

        stage('Release to Production') {
            steps {
                input message: 'Staging verified. Promote to Production?', ok: 'Deploy Now'
                sh 'docker stop movie-prod || true'
                sh 'docker rm   movie-prod || true'
                sh "docker tag  ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:prod-${BUILD_NUMBER}"
                sh "docker run -d --name movie-prod -p 5000:5000 ${IMAGE_NAME}:prod-${BUILD_NUMBER}"
                sh 'sleep 5'
                sh 'curl -f http://host.docker.internal:5000/health'
                echo "Production deployed: ${IMAGE_NAME}:prod-${BUILD_NUMBER} at http://localhost:5000"
            }
        }

        stage('Monitoring') {
            steps {
                sh 'curl -f http://host.docker.internal:5000/health'
                sh 'curl -sf http://host.docker.internal:5000/metrics | head -10'
                echo 'App metrics available at http://localhost:5000/metrics'
                echo 'Prometheus at http://localhost:9090'
                echo 'Grafana at http://localhost:3000'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully. All 7 stages passed.'
        }
        failure {
            echo 'Pipeline failed. Check console output for details.'
        }
    }
}