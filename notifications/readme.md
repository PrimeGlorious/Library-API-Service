celery for this bot on windows shall be ran via the next command
```
celery -A config worker -l INFO --pool=threads
```
since --pool=solo and without pool (which is fine for unix) doesn't work in this setup