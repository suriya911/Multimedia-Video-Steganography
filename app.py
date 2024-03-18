from flask import Flask, render_template, send_file, session
import os
from flask_wtf import FlaskForm
from wtforms import EmailField, FileField, SelectField, SubmitField, MultipleFileField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import decoding as vd
import encoding as ve
import video as v
import zipfile
from wtforms.validators import InputRequired
import Keys as k
import Email_KEY as mail




app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['VIDEO_FOLDER'] = './Video/'
app.config['RESULT_FOLDER'] = './Results/'
app.config['FILE_FOLDER'] = './Files/'
app.config['KEY_FOLDER'] = './Keys/'

# Configure session to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

class DecryptForm(FlaskForm):
    evideo = FileField("Decrypt Video", validators=[InputRequired()], render_kw={'style': 'padding: 10px; border: 2px solid black; background-color: none; color: #333; border-radius: 5px; font-size: 16px;'})
    Private_KEY = FileField("Private Key", validators=[InputRequired()], render_kw={'style': 'padding: 10px; border: 2px solid black; background-color: none; color: #333; border-radius: 5px; font-size: 16px;'})
    submit = SubmitField("DECRYPT")

class VideoForm(FlaskForm):
    cvideo = FileField("Cover Video", validators=[InputRequired()], render_kw={'style': 'padding: 10px; border: 2px solid black; background-color: none; color: #333; border-radius: 5px; font-size: 16px;'})
    dropdown = SelectField('Select Option', choices=[('', 'Select Size'),(10, '< 1MB'), (20, '< 1.5MB'), (30, '< 2MB'),(40,'< 2.5MB'),(50,'< 3MB')], validators=[InputRequired()], render_kw={'style': 'padding: 10px; border: 2px solid black; background-color: none; color: #333; border-radius: 5px; font-size: 16px;'})
    submit = SubmitField("Get Video Information")

class EncryptForm(FlaskForm):
    files = MultipleFileField("Files to Embed", validators=[InputRequired()], render_kw={'style': 'padding: 10px; border: 2px solid black; background-color: none; color: #333; border-radius: 5px; font-size: 16px;'})   
    Public_KEY = FileField("Public Key", validators=[InputRequired()], render_kw={'style': 'padding: 10px; border: 2px solid black; background-color: none; color: #333; border-radius: 5px; font-size: 16px;'})
    submit = SubmitField("ENCRYPT")

class GenerateKeysForm(FlaskForm):
    sender = EmailField("📩",validators=[InputRequired()],render_kw={
        'class_': 'form__field',
        'style': 'font-family: sans-serif; border: 10; border-bottom: 2px solid #0d0c0c; outline: 0; font-size: 1.3rem; color: 1f1f1f; padding: 7px; background: transparent; transition: border-color 0.2s;'
    })
    submit = SubmitField("GENERATE")



def zip_folder(folder_path, output_path):
    """Zip the contents of a folder and save to a zip file."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

# Function to remove all files in a directory
def remove_files_in_directory(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

folder=['./Video','./Output','./Files','./Keys','./Results','./Decrypted_Files','./Encrypted_Files','./Retrived_Files']

# Define route for Home page
@app.route('/')
@app.route('/home')
def home():
    session.pop('video_data', None)
    for i in folder:
        if not os.path.exists(i):
            os.makedirs(i)
        remove_files_in_directory(i)
    print(session)
    session['video_form_submitted'] = False
    session['encrypt_form_submitted'] = False
    return render_template('home.html')

# Define route for Encrypt page
@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    vform = VideoForm()
    eform = EncryptForm()
    file_exists = False
    print(session)
    if eform.validate_on_submit() and eform.submit.data and session['encrypt_form_submitted']:
        files = eform.files.data
        Public_KEY = eform.Public_KEY.data
        
        Public_KEY.save(os.path.join(app.config['KEY_FOLDER'], secure_filename(Public_KEY.filename)))
        Public_KEY_path = os.path.join(app.config['KEY_FOLDER'], secure_filename(Public_KEY.filename))
        l=[]
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['FILE_FOLDER'], filename))
            l.append(filename)
        video_data = session['video_data']
        v_path = video_data['video_path']
        print(l)
        print()
        
        ve.call_encrypt(v_path,l,int(video_data['frame_count']),Public_KEY_path)
        
        print(files)
        
        session['video_form_submitted'] = True
        session['encrypt_form_submitted'] = False
        session.pop('video_data', None)  # Clear the session data
        
        folder_path = './Output'  # Path to the folder you want to zip
        zip_filename = 'folder.zip'
        zip_path = os.path.join(app.config['RESULT_FOLDER'], zip_filename)  # Save zip in instance folder
        zip_folder(folder_path, zip_path)
        if os.path.exists(zip_path):
            file_exists = True
        
        return render_template('encrypt.html', vform=vform, eform=eform, frame_number='', files_to_embed='', file_exists=file_exists)

    if vform.validate_on_submit() and vform.submit.data and not session['video_form_submitted']:
        cover = vform.cvideo.data
        filename = secure_filename(cover.filename)
        count = int(vform.dropdown.data)
        print(count)
        cover.save(os.path.join(app.config['VIDEO_FOLDER'], filename))
        video_path = os.path.join(app.config['VIDEO_FOLDER'], filename)
        frame_number, c = v.get_video_info(video_path,count)
        
        files_to_embed = ((frame_number-10)//(count+2))
        session['video_form_submitted'] = True
        session['encrypt_form_submitted'] = True
        session['video_data'] = {
            'video_path': video_path,
            'frame_number': frame_number,
            'frame_count': count,
            'files_to_embed': files_to_embed
        }
        
        return render_template('encrypt.html', vform=vform, eform=eform, frame_number=frame_number, files_to_embed=files_to_embed, file_exists=file_exists)

    if 'video_data' in session:
        video_data = session['video_data']
        return render_template('encrypt.html', vform=vform, eform=eform, frame_number=video_data['frame_number'], files_to_embed=video_data['files_to_embed'], file_exists=file_exists)
    
    return render_template('encrypt.html', vform=vform, eform=eform, frame_number='', files_to_embed='', file_exists=file_exists)




# Define route for Decrypt page
@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    dform = DecryptForm()
    file_exists = False
    
    if dform.validate_on_submit():
        video = dform.evideo.data
        Private_KEY = dform.Private_KEY.data
        
        video.save(os.path.join(app.config['VIDEO_FOLDER'], secure_filename(video.filename)))
        video_path = os.path.join(app.config['VIDEO_FOLDER'], secure_filename(video.filename))
        Private_KEY.save(os.path.join(app.config['KEY_FOLDER'], secure_filename(Private_KEY.filename)))
        RSA_KEY_path = os.path.join(app.config['KEY_FOLDER'], secure_filename(Private_KEY.filename))
        
        vd.call_decrypt(video_path, RSA_KEY_path)
        
        folder_path = './Decrypted_Files'  # Path to the folder you want to zip
        zip_filename = 'folder.zip'
        zip_path = os.path.join(app.config['RESULT_FOLDER'], zip_filename)  # Save zip in instance folder
        zip_folder(folder_path, zip_path)
        if os.path.exists(zip_path):
            file_exists = True
        
        # Return the file for download
        return render_template('decrypt.html', form=dform, file_exists=file_exists)
    
    return render_template('decrypt.html', form=dform, file_exists=file_exists)

# Define route for Downloads page
@app.route('/downloads')
def downloads():
    return send_file('./Results/folder.zip', as_attachment=True, download_name='folder.zip')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    gform = GenerateKeysForm()
    file_exists = False
    if gform.validate_on_submit():
        sender = gform.sender.data
        print(sender)
        k.generate_rsa_key()
        mail.send_email(sender)
        file_path = os.path.join(app.config['KEY_FOLDER'], "RSA_private.pem")
        if os.path.exists(file_path):
            file_exists = True
        return render_template('generate.html', form=gform, file_exists=file_exists)
    return render_template('generate.html', form=gform, file_exists=file_exists)


# Function to Download the Private Key
@app.route('/downloadkey')
def downloadkey():
    return send_file('./Keys/RSA_private.pem', as_attachment=True)


# Define route for About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# main driver function
if __name__ == '__main__':
    app.run(debug=True)
