import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from poller import poll_once

if __name__ == "__main__":
    poll_once()
