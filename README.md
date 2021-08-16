## Local testing

Create .env in root with data:

```
DJANGO_DEBUG=True
TELEGRAM_TOKEN=<YOUR TOKEN>
DATABASE_URL=sqlite:///db.sqlite3
```

Run locally: 

``` bash
python run_pooling.py
```