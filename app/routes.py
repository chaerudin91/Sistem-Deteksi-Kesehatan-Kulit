from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.database import get_db
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
from mysql.connector import Error, IntegrityError
from flask import jsonify
from flask import session
from werkzeug.utils import secure_filename
from PIL import Image

main = Blueprint('main', __name__)
# Muat model saat aplikasi dijalankan
model = load_model('models/trained_model.keras') 

@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # Memeriksa apakah user ditemukan dan password cocok
        if user and user['password'] == password:  # Pertimbangkan untuk hashing password
            flash('Login berhasil!', 'success')
            return redirect(url_for('main.index'))  # Redirect ke halaman utama
        else:
            flash('Login gagal. Periksa username atau password Anda.', 'danger')

    return render_template('login.html')

@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)  # Hapus session pengguna
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('main.login')) 

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        connection = None
        cursor = None
        
        try:
            connection = get_db()
            if connection is None:
                flash('Error connecting to the database.', 'error')
                return redirect(url_for('register'))

            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, password))
            connection.commit()
            flash('Register berhasil! Silakan login.', 'success')
            return redirect(url_for('main.login'))
        
        except IntegrityError as e:
            if 'email' in str(e):
                flash('Email sudah ada, masukkan yang lain.', 'error')
            else:
                flash('Username sudah ada, masukkan yang lain.', 'error')
        except Error as e:
            flash('Terjadi kesalahan: {}'.format(str(e)), 'error')
        finally:
            if cursor:
                cursor.close()  # Close cursor if it was created
            if connection:
                connection.close()  # Close connection if it was created
    
    return render_template('register.html')


@main.route('/about')
def about():
    return render_template('HOME/about.html')  

@main.route('/contact')
def contact():
    return render_template('HOME/contact.html')  

@main.route('/bahan')
def bahan():
    return render_template('HOME2/bahan.html') 

@main.route('/edukasi')
def edukasi():
    return render_template('HOME2/edukasi.html') 

@main.route('/faq')
def faq():
    return render_template('HOME/faq.html')

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Fungsi untuk memeriksa jenis file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk mempersiapkan gambar sebelum prediksi
# Route untuk halaman prediksi
@main.route('/prediksi', methods=['GET', 'POST'])
def prediksi():
    if request.method == 'POST':
        file = request.files.get('file')
        
        if file:
            filepath = os.path.join('app/static/uploads', file.filename)
            file.save(filepath)

            # Load image for prediction
            image = load_img(filepath, target_size=(224, 224))  
            image = img_to_array(image)
            image = np.expand_dims(image, axis=0)
            image = image / 255.0  # Normalisasi

            # Predict using the model
            predictions = model.predict(image)
            class_names = ['berjerawat', 'berminyak', 'kering', 'normal']  
            predicted_class = class_names[np.argmax(predictions[0])]
            
            return render_template('HOME2/result.html', prediction=predicted_class, filepath=file.filename)

    return render_template('HOME2/prediksi.html')


UPLOAD_FOLDER = 'app/static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
@main.route('/save_image', methods=['POST'])
def save_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file found"}), 400

    file = request.files['image']
    file_path = os.path.join(UPLOAD_FOLDER, 'captured_image.png')
    file.save(file_path)

    return jsonify({"message": "Image saved successfully", "file_path": file_path})

@main.route('/prediksi2', methods=['POST'])
def prediksi2():
    if request.method == 'POST':
        file = request.files.get('file')
        
        if file:
            filepath = os.path.join('app/static/uploads/captured_image.png')
            file.save(filepath)

            # Load image for prediction
            image = load_img(filepath, target_size=(224, 224))  
            image = img_to_array(image)
            image = np.expand_dims(image, axis=0)
            image = image / 255.0  # Normalisasi

            # Predict using the model
            predictions = model.predict(image)
            class_names = ['berjerawat', 'berminyak', 'kering', 'normal']  
            predicted_class = class_names[np.argmax(predictions[0])]
            
            return render_template('HOME2/result2.html', prediction=predicted_class, filepath=file.filename)

    return render_template('HOME2/prediksi.html')
    
@main.route('/result')
def result():
    prediction = request.args.get('prediction')
    filename = request.args.get('filename')
    return render_template('HOME2/result.html', prediction=prediction, filename=filename)

@main.route('/result2')
def result2():
    prediction = request.args.get('prediction')
    filename = request.args.get('filename')
    return render_template('HOME2/result2.html', prediction=prediction, filename=filename)
