### All commands should be ran AFTER the main DRF application is running

First you should start redis process
```
docker run --name redis -p 6379:6379 -d redis
```
celery for this bot on windows shall be ran via the next command
```
celery -A config worker -l INFO --pool=threads
```
since --pool=solo and without pool (which is fine for unix) doesn't work in this setup

so in the first terminal you shall run the command above, in another one the following command
```
celery -A config beat -l INFO
```

And finally run the following command to start telegram bot itself:
```
python.exe .\manage.py run_bot
```
