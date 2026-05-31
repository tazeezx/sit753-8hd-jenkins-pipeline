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
                    docker rm -f test-${BUILD_NUMBER} || true
                    docker run --name test-${BUILD_NUMBER} ${IMAGE_NAME}:${BUILD_NUMBER} \
                        sh -c "pytest tests/ --junitxml=test-results.xml --cov=. --cov-report=xml:coverage.xml -v"
                    docker cp test-${BUILD_NUMBER}:/app/test-results.xml .
                    docker cp test-${BUILD_NUMBER}:/app/coverage.xml .
                    docker rm test-${BUILD_NUMBER}
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
                        docker rm -f sonar-${BUILD_NUMBER} || true
                        docker run --name sonar-${BUILD_NUMBER} \
                            --network jenkins-net \
                            -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                            -e SONAR_TOKEN="$SONAR_AUTH_TOKEN" \
                            --entrypoint sh \
                            sonarsource/sonar-scanner-cli \
                            -c "mkdir -p /usr/src && cd /usr/src && echo placeholder" || true
                        docker rm -f sonar-${BUILD_NUMBER} || true

                        docker create --name sonar-${BUILD_NUMBER} \
                            --network jenkins-net \
                            -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                            -e SONAR_TOKEN="$SONAR_AUTH_TOKEN" \
                            -w /usr/src \
                            sonarsource/sonar-scanner-cli \
                            -Dsonar.projectKey=movie-crud-flask \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3.11 \
                            -Dsonar.exclusions=tests/**,**/*.html,**/*.css \
                            -Dsonar.python.coverage.reportPaths=coverage.xml

                        docker cp movie.py sonar-${BUILD_NUMBER}:/usr/src/
                        docker cp requirements.txt sonar-${BUILD_NUMBER}:/usr/src/
                        docker cp templates sonar-${BUILD_NUMBER}:/usr/src/
                        docker cp static sonar-${BUILD_NUMBER}:/usr/src/
                        docker cp tests sonar-${BUILD_NUMBER}:/usr/src/
                        docker cp sonar-project.properties sonar-${BUILD_NUMBER}:/usr/src/
                        docker cp coverage.xml sonar-${BUILD_NUMBER}:/usr/src/ || true

                        docker start -a sonar-${BUILD_NUMBER}
                        docker rm sonar-${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Security') {
            steps {
                sh """
                    docker rm -f sec-${BUILD_NUMBER} || true
                    docker run --name sec-${BUILD_NUMBER} ${IMAGE_NAME}:${BUILD_NUMBER} \
                        sh -c "pip install bandit pip-audit --quiet && \
                            bandit -r . --exclude ./tests -f txt -o bandit-report.txt || true && \
                            pip-audit -r requirements.txt -f json -o pip-audit-report.json || true"
                    docker cp sec-${BUILD_NUMBER}:/app/bandit-report.txt . || true
                    docker cp sec-${BUILD_NUMBER}:/app/pip-audit-report.json . || true
                    docker rm sec-${BUILD_NUMBER}
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