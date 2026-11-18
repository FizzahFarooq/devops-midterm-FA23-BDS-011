pipeline {
  agent any
  options { timeout(time: 15, unit: 'MINUTES') }

  environment {
    STUDENT_ID = 'FA23-BDS-011'
    SENDER     = 'fizzahfarooq1064@gmail.com'
    EC2_IP     = '16.192.96.208'
    IMAGE      = 'midterm-api'
    CONTAINER  = 'midterm-api'
  }

  stages {
    stage('Fetch Latest Code and Data') {
      steps {
        checkout scm
        sh 'git log -1 --oneline'
        sh 'wc -l dataset/train.csv'
      }
    }

    stage('Setup Python') {
      steps {
        sh '''
          python3 -m venv venv
          . venv/bin/activate
          pip install --quiet -r requirements.txt pytest httpx
        '''
      }
    }

    stage('Train Model') {
      steps {
        sh '''
          . venv/bin/activate
          export GIT_COMMIT=$(git rev-parse HEAD)
          python train.py
        '''
      }
    }

    stage('Run Tests') {
      steps {
        sh '. venv/bin/activate && python -m pytest -q'
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .'
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker tag ${IMAGE}:latest $DH_USER/midterm-fa23-bds-011:latest
            docker tag ${IMAGE}:latest $DH_USER/midterm-fa23-bds-011:${BUILD_NUMBER}
            docker push $DH_USER/midterm-fa23-bds-011:latest
            docker push $DH_USER/midterm-fa23-bds-011:${BUILD_NUMBER}
          '''
        }
      }
    }

    stage('Deploy on EC2') {
      steps {
        sh '''
          docker rm -f ${CONTAINER} || true
          docker run -d --name ${CONTAINER} --restart unless-stopped -p 8000:8000 ${IMAGE}:latest
          for i in 1 2 3 4 5 6 7 8 9 10; do
            curl -sf http://localhost:8000/metrics && break
            sleep 3
          done
          curl -f http://localhost:8000/metrics
        '''
      }
    }
  }

  post {
    always {
      emailext(
        from: "${env.SENDER}",
        to: 'fizzahfarooq1064@gmail.com',
        subject: "${env.STUDENT_ID} - MIDTERM-${env.STUDENT_ID} - Build #${env.BUILD_NUMBER} ${currentBuild.currentResult}",
        body: """Student Reg No: ${env.STUDENT_ID}
Result: ${currentBuild.currentResult}
Build: ${env.BUILD_URL}
Commit: ${env.GIT_COMMIT}
Metrics: http://${env.EC2_IP}:8000/metrics"""
      )
    }
  }
}
