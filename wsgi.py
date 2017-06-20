from flask import Flask, render_template
application = Flask(__name__)

import os, sys
REP_CONNECTHYS = os.path.abspath(os.path.dirname(__file__))
if not REP_CONNECTHYS in sys.path:
	sys.path.insert(0, REP_CONNECTHYS)

import connecthys.run

if __name__ == "__main__":
    application.run()