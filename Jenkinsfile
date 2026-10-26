pipeline {
    agent any

    environment {
        BOOK_IMAGE  = "bookstore/book-service:${BUILD_NUMBER}"
        ORDER_IMAGE = "bookstore/order-service:${BUILD_NUMBER}"
        PIP         = "/opt/pyenv/bin/pip"
        PYTEST      = "/opt/pyenv/bin/pytest"
    }

    stages {

        // ── Step 1: Install dependencies ───────────────────────────────────
        stage('Install') {
            parallel {
                stage('Install Book Service') {
                    steps {
                        dir('book_service') {
                            sh '${PIP} install -e ".[dev]" -q'
                        }
                    }
                }
                stage('Install Order Service') {
                    steps {
                        dir('order_service') {
                            sh '${PIP} install -e ".[dev]" -q'
                        }
                    }
                }
            }
        }

        // ── Step 2: Run pytest ─────────────────────────────────────────────
        stage('Test') {
            parallel {
                stage('Test Book Service') {
                    steps {
                        dir('book_service') {
                            sh '${PYTEST} tests/ -v --tb=short'
                        }
                    }
                }
                stage('Test Order Service') {
                    steps {
                        dir('order_service') {
                            sh '${PYTEST} tests/ -v --tb=short'
                        }
                    }
                }
            }
        }

        // ── Step 3: Build Docker images ────────────────────────────────────
        stage('Build Docker Images') {
            parallel {
                stage('Build Book Service') {
                    steps {
                        dir('book_service') {
                            sh "docker build -t ${BOOK_IMAGE} ."
                        }
                    }
                }
                stage('Build Order Service') {
                    steps {
                        dir('order_service') {
                            sh "docker build -t ${ORDER_IMAGE} ."
                        }
                    }
                }
            }
        }
    }

    post {
        success { echo "Pipeline passed. Images: ${BOOK_IMAGE} | ${ORDER_IMAGE}" }
        failure { echo "Pipeline failed. Check the logs above." }
    }
}
