Phase 11 — AWS Deployment: What You Did Step by Step
Step 1 — AWS Setup
You created an AWS account, set up MFA security, installed AWS CLI on your Mac via Homebrew, created new Access Keys, and ran aws configure to connect your Mac to AWS.
Step 2 — ECR (Elastic Container Registry)
You created a repository on AWS called sentinelledger to store your Docker image. Think of ECR like GitHub but for Docker images.
Step 3 — Docker Build & Push
You built your Docker image on your Mac and pushed it to ECR. First attempt failed because your Mac M1 is ARM64 but EC2 is AMD64 — so you rebuilt using --platform linux/amd64 to make it compatible.
Step 4 — EC2 Server Setup
You launched a real Ubuntu server in London (eu-west-2) using t3.micro (free tier). You created a security group (firewall) and opened ports 22 (SSH) and 8000 (your app). You created a .pem key file to securely access the server.
Step 5 — SSH into Server
You connected to your live AWS server using ssh -i sentinelledger-key.pem ubuntu@18.130.226.110. This is a real Ubuntu server running in an AWS data centre in London.
Step 6 — Install Docker on Server
You installed Docker and AWS CLI on the EC2 server, added your user to the Docker group, and logged into ECR from the server.
Step 7 — Run Containers on Server
You ran three Docker containers on the server: PostgreSQL (database), Redis (caching), and SentinelLedger (your app). You fixed a connection issue by using 172.17.0.1 (Docker gateway IP) instead of localhost for both database and Redis hosts.
Step 8 — S3 Frontend Hosting
You created an S3 bucket called sentinelledger-frontend, enabled static website hosting, made it public, and uploaded your HTML/CSS/JS files. You updated script.js to point to the EC2 IP instead of localhost.
Step 9 — CORS Fix
You fixed a CORS error that was blocking login — the browser was blocking requests from S3 to EC2. Fixed by updating main.py with the correct origins and setting allow_credentials=False.
Step 10 — Redis Fix
You fixed Redis connection by adding REDIS_HOST environment variable in routers/users.py so it uses 172.17.0.1 instead of localhost inside Docker.
Step 11 — Billing Alert
You set up a Zero Spend Budget alert in AWS Billing — AWS will email you the moment any charge above $0.01 appears.

What's Now Live:

Backend API → http://18.130.226.110:8000
API Docs → http://18.130.226.110:8000/docs
Frontend → http://sentinelledger-frontend.s3-website.eu-west-2.amazonaws.com


