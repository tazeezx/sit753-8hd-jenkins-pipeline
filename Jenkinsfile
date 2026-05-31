pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Code checked out successfully'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t movie-app:${BUILD_NUMBER} .'
                echo "Built image movie-app:${BUILD_NUMBER}"
            }
        }
    }
}