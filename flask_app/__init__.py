from flask import Flask, session
app = Flask(__name__)
app.secret_key = 'I could be anyone... anything... anywhere...'