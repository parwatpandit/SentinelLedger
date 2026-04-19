1. activate the virtual invaronment--> source venv/bin/activate

2. pip freeze > requirements.txt => for auto update the .txt fiel when install a library using pip so i know what are the library i have

3. mysqlworkbench password: Maninblack90

4. run main.py => uvicorn main:app --reload

5. pusihing in git:  

1.  git init
git add .
git commit -m "SentinelLedger v2 backend complete"

2. git add .
git commit -m "SentinelLedger v2 frontend complete"
git push


6. stop password being push to git:

note: created a file name .gitignore and pest below things

.env
venv/
__pycache__/
*.pyc


7. push everything now in my github account

git add .
git commit -m "SentinelLedger v2 Journey 1 complete"
git remote add origin https://github.com/parwatpandit/SentinelLedger.git
git push -u origin main

8. run the app in docker => docker-compose up and 
to stop => docker-compose down