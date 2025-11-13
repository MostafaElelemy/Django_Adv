from celery import shared_task
import time



@shared_task
def generate_report_task(user_id):
    
    print(f"Task: [generate_report]... Starting for user {user_id}")
    time.sleep(10) 
    print("Task: [generate_report]... COMPLETED")
    return "Report Generated Successfully (10 seconds)"




@shared_task
def send_welcome_email_task(user_email, message):
   
    print(f"Task: [send_email]... Sending to {user_email}")
    time.sleep(5) 
    print("Task: [send_email]... COMPLETED")
    return f"Email sent to {user_email} (5 seconds)"