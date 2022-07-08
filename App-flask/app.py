from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)

def test_job():
    print('I am working...')

@app.route('/')
def route():
    return 'flask'

scheduler = BackgroundScheduler()
job = scheduler.add_job(test_job, 'interval', seconds=3)
scheduler.start()

if __name__ == '__main__':
    app.run()




    // create scheduler using a subclass of BaseScheduler
scheduler = BackgroundScheduler()
scheduler.configure(timezone='utc')

// cron would look like 1,31 * * * 1-5

scheduler.add_job(function_name, 'cron', day_of_week='1-5', hour='*', minute='1,31')

scheduler.add_job(function_name, 'cron', day_of_week ='mon-sun', hour=16, minute=00)

scheduler.add_job(func=function_name, trigger=CronTrigger.from_crontab("0 16 * * *"))


scheduler.start()