from datetime import datetime

with open("data/update_log.txt", "a") as f:
    f.write(f"Updated at {datetime.now()}\n")
