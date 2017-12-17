gunicorn app:app -w 4 -b 0.0.0.0:5000 --log-level DEBUG --log-file test.log --reload
# mongoimport -d hpctf -c user db/user.json --jsonArray
# mongoimport -d hpctf -c freeze db/freeze.json --jsonArray
# mongoimport -d hpctf -c task db/task.json --jsonArray
