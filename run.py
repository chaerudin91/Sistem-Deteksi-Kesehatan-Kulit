from flask import Flask, request, render_template, redirect, url_for
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from app import create_app
import secrets


app = create_app()
app.secret_key = secrets.token_hex(16) 
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
