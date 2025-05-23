from flask import Flask, render_template,send_file, request
from io import BytesIO
import qrcode,os
from werkzeug.utils import secure_filename
from zxing import BarCodeReader

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/generate')
def generate():
    return render_template('generate.html')

@app.route('/generate', methods=['GET', 'POST'])
def gen():
    if request.method == 'POST':
        data = request.form.get('data')
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_code_io = BytesIO()
        img.save(qr_code_io)

        qr_code_io.seek(0)

        return send_file(
            qr_code_io,
            mimetype="image/png",
            as_attachment=True,
            download_name="qrcode.png",
        )
    return render_template('generate.html')

@app.route('/detect')
def detect():
    return render_template('detect.html')

@app.route('/detect', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        # Save the uploaded file to the upload folder
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Use BarCodeReader to decode the QR code
        reader = BarCodeReader()
        barcode = reader.decode(filepath)

        # Check if a QR code was found
        if barcode:
            return f"QR Code content: {barcode.parsed}"
        else:
            return "No QR Code found in the image"
        
if __name__ == '__main__':
    app.run(debug=True)
