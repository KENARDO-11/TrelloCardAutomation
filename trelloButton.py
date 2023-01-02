import os
from dotenv import load_dotenv
from apiScheduler import *

load_dotenv()
TASK = os.environ.get("TASK", default="No Task Found")

# Main function
def main():
    taskFile = f'{sys.path[0]}{os.sep}Tasks{os.sep}'
    taskFile += TASK
    print(f"Starting Task")
    readLists()
    readLabels()
    readTask(taskFile)

if __name__ == '__main__':
    main()