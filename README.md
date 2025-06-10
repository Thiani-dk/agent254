# Agent254

**Branch: `redis-rq-version` (Redis / RQ support enabled)**

This branch uses Redis + RQ to send OTP‐emails in the background.  

**Before running locally**:
1. Make sure you have a Redis server running (e.g. `redis-server` on localhost:6379).  
2. Install Redis + RQ:
   ```bash
   pip install redis rq
3. In routes.py, you will see lines like:

    from redis import Redis
    from rq import Queue

4. Start an RQ worker in a separate terminal:


    rq worker

(It will pick up the queued queue_send_email jobs.)

If you do not wish to run Redis/RQ, switch back to the main branch, which uses synchronous SMTP‐email.