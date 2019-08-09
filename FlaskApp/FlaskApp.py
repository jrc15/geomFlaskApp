#Import Python modules
import os
import zipfile
import io
import pathlib
import shutil
import sys

#Import Flask dependent modules and decorators
from flask import Flask, render_template, request, send_file, after_this_request, redirect, url_for, flash, session
from werkzeug import secure_filename

#Import Custom Scripts
from HydroAnalysis import StreamDelineation
from HydroHAND import HAND
from HydroTWI import TWI
from HydroContamination import ContaminationFlow
from HydroClean import tidyFiles, sortFiles


# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'GEOM Cookie Monster'


# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['tif', 'shp', 'dbf', 'cpg', 'prj', 'qpj', 'shx', 'csv'])
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # Upload file sizes cannot exceed 100mb

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    if request.form['password'] == 'admin' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return index()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()
'''
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html', error=error)
'''
# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    print('\n','Uploading...', '\n')
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist("file[]")
    for file in uploaded_files:
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            print('ALLOWED:', file)
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file form the temporal folder to the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            print('NOT ALLOWED:', file)
    flash('Files have been uploaded successfully!')
    return redirect('/')

@app.route('/Stream', methods=['GET'])
def Stream():
    # Check to see if input files have been uploaded
    inFiles = ['DEM.tif', 'Outlet.shp', 'Basin.shp']
    upDir = './static/uploads/'
    for file in inFiles:
        joinPath = os.path.join(upDir, file)
        exists = os.path.isfile(joinPath)
        if exists:
            print('File Exists')
        else:
            flash('ERROR: Input files for Stream Delineation are required, {0} has not been uploaded'.format(file))
            return redirect('/')
    StreamDelineation()
    flash('Stream Delineation Complete!')
    return redirect('/')

@app.route('/Hand', methods=['GET'])
def Hand():
    HAND()
    flash('HAND Complete!')
    return redirect('/')

@app.route('/Twi', methods=['GET'])
def Twi():
    TWI()
    flash('TWI Complete!')
    return redirect('/')

@app.route('/Contamination', methods=['GET'])
def Contamination():
    file = 'Source.shp'
    upDir = './static/uploads/'
    joinPath = os.path.join(upDir, file)
    exists = os.path.isfile(joinPath)
    if exists:
        print('File Exists')
    else:
        flash('ERROR: Input files for Contamination Flow are required, {0} has not been uploaded'.format(file))
        return redirect('/')
    ContaminationFlow()
    flash('Contamination Flow Complete!')
    return redirect('/')

@app.route('/Tidy', methods=['GET'])
def Tidy():
    tidyFiles()
    flash('Unneeded files have been removed!')
    return redirect('/')

@app.route('/Sort', methods=['GET'])
def Sort():
    sortFiles()
    flash('Files have been sorted!')
    return redirect('/')

@app.route('/download', methods=['GET'])
def download():
    # Compress file list
    base_path = pathlib.Path('./static/uploads/')
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for root, sub, file in os.walk(base_path):
            for f_name in file:
                f_path = os.path.join(root, f_name)
                z.write(f_path)
    data.seek(0)
    @after_this_request
    # add another function after the function above has been executed
    def remove_file(response):
        print('\n','Downloading...', '\n')
        for root, sub, file in os.walk(base_path):
            print('File:', file)
            try:
                #Check if path is a file path, if yes remove file, if no provide error message
                for label in sub:
                    sub_path = os.path.join(root, label)
                    if os.path.isdir(sub_path):
                        shutil.rmtree(sub_path)
                for name in file:
                    file_path = os.path.join(root, name)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response
        flash('Files have been Downloaded!')
    return send_file(
                     data,
                     mimetype='application/zip',
                     as_attachment=True,
                     attachment_filename='data'
                     )

@app.route('/reset')
def reset():
    print('\n','Deleting all Files...', '\n')
    base_path = pathlib.Path('./static/uploads/')
    for root, sub, file in os.walk(base_path):
            for label in sub:
                sub_path = os.path.join(root, label)
                if os.path.isdir(sub_path):
                    shutil.rmtree(sub_path)
            for name in file:
                file_path = os.path.join(root, name)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
    flash('The Web App as been Reset!!')
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
