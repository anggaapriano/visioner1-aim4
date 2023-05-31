from flask import Flask,render_template,request,jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import gym
import pickle
import os
import tensorflow as tf
from PIL import Image
from flask_ngrok import run_with_ngrok


from process import generate_response, preparation 


# download nltk
preparation()


app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello_world():
    return render_template("index.html")

# =[Variabel Global]=============================

app = Flask(__name__, static_url_path='/static')


# Peta Default
# peta = peta_1
# pilihanPeta = 1

peta        = None
pilihanPeta = None

# Load Environment
env = gym.make("FrozenLake-v0",is_slippery=False, desc=peta)
env.reset()

robot_current_state = 0

# Load Model (Q-Table) 
Q_table_all = pickle.load(open('Q_table_Cornny_RL.model', 'rb'))

# Q_table     = None
# Q_table_all = None

n_observations = 16
n_actions      = 4

robot_current_state = 0

peta_1 = ['SFFF','FHFH','FFFH','HFFG']
peta_2 = ['SFFF','FFHF','HFFF','HFFG']
peta_3 = ['SHFF','FHFH','FFFH','HHFG']
peta_4 = ['SFFF','HHFF','FFFF','HFFG']
peta_5 = ['SFFH','FFFH','HFFH','HHFG']
peta_6 = ['SFHF','FHHF','FFFH','HFFG']


app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS']  = ['.jpg','.JPG']
app.config['UPLOAD_PATH']        = './static/img/uploads/'

# load model
model = tf.keras.models.load_model("modelcorn.h5")
# model.summary()

# define classes
corndiseases_classes = [ "Corn Common Rust", "Corn Gray Leaf Spot","Corn Healthy", "Corn Northern Leaf Blight"]

# define image size
IMG_SIZE = (299, 299)

# =[Routing]=====================================

# [Routing untuk Halaman Utama atau Home]
@app.route("/")
def beranda():
	return render_template('index.html')

# ROUTING untuk chatbot
@app.route("/get")
def get_bot_response():
    user_input = str(request.args.get('msg'))
    result = generate_response(user_input)
    return result

# [Routing untuk API]	
@app.route("/api/deteksi",methods=['POST'])
def apiDeteksi():
	# Set nilai default untuk hasil prediksi dan gambar yang diprediksi
	hasil_prediksi  = '(none)'
	gambar_prediksi = '(none)'

	# Get File Gambar yg telah diupload pengguna
	uploaded_file = request.files['file']
	filename      = secure_filename(uploaded_file.filename)
	
	# Periksa apakah ada file yg dipilih untuk diupload
	if filename != '':
	
		# Set/mendapatkan extension dan path dari file yg diupload
		file_ext        = os.path.splitext(filename)[1]
		gambar_prediksi = '/static/img/uploads/' + filename
		
		# Periksa apakah extension file yg diupload sesuai (jpg)
		if file_ext in app.config['UPLOAD_EXTENSIONS']:
			
			# Simpan Gambar
			uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
			
			# Memuat Gambar
			test_image         = Image.open('.' + gambar_prediksi).resize(IMG_SIZE)

			img_array = np.expand_dims(test_image, 0)
			

			predictions = model.predict(img_array)
			hasil_prediksi = corndiseases_classes[np.argmax(predictions[0])]

			print(hasil_prediksi)
			
			# Return hasil prediksi dengan format JSON
			return jsonify({
				"prediksi": hasil_prediksi,
				"gambar_prediksi" : gambar_prediksi
			})
		else:
			# Return hasil prediksi dengan format JSON
			gambar_prediksi = '(none)'
			return jsonify({
				"prediksi": hasil_prediksi,
				"gambar_prediksi" : gambar_prediksi
			})


# REINFORCEMENT LEARNING

# [Routing untuk API : Reset Environment]	
@app.route("/api/reset",methods=['GET'])
def apiReset():
	# Variabel Global
	global peta
	global env
	
	if request.method=='GET':
		# Reset environment
		env = gym.make("FrozenLake-v0",is_slippery=False, desc=peta)
		env.reset()
	
		# Set nilai state menjadi nilai awal
		robot_current_state = 0

		# peta_string = ""
		# if peta is not None:
		# 	peta_string = peta[0] + peta[1] + peta[2] + peta[3]
		
		# Konversi peta dari array atau list menjadi string
		peta_string = peta[0] + peta[1] + peta[2] + peta[3]
		
		# Return peta dan current state dengan format JSON
		return jsonify({
			"peta"  : peta_string,
			"state" : robot_current_state 
		})

# [Routing untuk API : Menggerakkan Si Kuning (Pemain)]
@app.route("/api/gerak",methods=['POST'])
def apiGerak():
	# Variabel Global
	global env

	gerak = None
	
	if request.method=='POST':
		# Set nilai aksi atau gerak berdasarkan input dari pengguna
		gerak = float(request.form['gerak'])
		
		# Agent melakukan aksi pada environment
		new_state, reward, done, info = env.step(gerak)
		
		# Update nilai state setelah agent melakukan aksi
		robot_current_state = new_state
		
		# Return current state dan kondisi apakah permainan berakhir 
		# dengan format JSON
		return jsonify({
			"state": robot_current_state,
			"done" : done
		})

# [Routing untuk API : Mendapatkan Peta]		
@app.route("/api/getPeta",methods=['GET'])
def apiGetPeta():
	# Variabel Global
	global peta
	
	if request.method=='GET':
		# Konversi peta dari array atau list menjadi string
		peta_string = peta[0] + peta[1] + peta[2] + peta[3]
		
		# Return peta dengan format JSON
		return jsonify({
			"peta" : peta_string
		})

# [Routing untuk API : Memilih Peta]		
@app.route("/api/setPeta",methods=['POST'])
def apiSetPeta():
	# Variabel Global
	global peta
	global env
	global pilihanPeta
	
	if request.method=='POST':
		# Set nilai pilihan peta berdasarkan input dari pengguna
		pilihanPeta = int(request.form['pilihanPeta'])
		
		# Update peta berdasarkan pilihan pengguna
		if(pilihanPeta ==1):
			peta = peta_1
		elif(pilihanPeta ==2):
			peta = peta_2
		elif(pilihanPeta ==3):
			peta = peta_3
		elif(pilihanPeta ==4):
			peta = peta_4
		elif(pilihanPeta ==5):
			peta = peta_5
		elif(pilihanPeta ==6):
			peta = peta_6
		else:
			peta = peta_1
		
		# Reset environment
		env = gym.make("FrozenLake-v0",is_slippery=False, desc=peta)
		env.reset()
		
		# Konversi peta dari array atau list menjadi string
		peta_string = peta[0] + peta[1] + peta[2] + peta[3]
		
		# Return peta dengan format JSON
		return jsonify({
			"peta" : peta_string
		})

# [Routing untuk API : Robot melakukan training/pembelajaran]		
@app.route("/api/robotBelajar",methods=['GET'])
def apiRobotBelajar():
	# Variabel Global
	global Q_table_all
	global Q_table
	
	if request.method=='GET':
		# Set Q-table sesuai peta saat ini
		Q_table = Q_table_all[pilihanPeta-1]
		
		# Return status apakah robot sudah selesai belajar
		# dengan format JSON
		return jsonify({
			"belajar" : "selesai"
		})

# [Routing untuk API : Menggerakkan Si Kuning (Robot)]		
@app.route("/api/gerakRobot",methods=['GET'])
def apiGerakRobot():
	# Variabel Global
	global env
	global robot_current_state
	global Q_table
	
	if request.method=='GET':
		# Mendapatkan aksi terbaik untuk agent pada current state		
		best_action = np.argmax(Q_table[robot_current_state])

		# Agent melakukan aksi pada environment
		new_state, reward, done, info = env.step(best_action)
		
		# Update nilai state setelah agent melakukan aksi
		robot_current_state = new_state
		
		# Return current state dan kondisi apakah permainan berakhir 
		# dengan format JSON
		return jsonify({
			"state": robot_current_state,
			"done" : done
		})


# =[Main]========================================		

if __name__ == '__main__':
    	

	# Run Flask di localhost 
	run_with_ngrok(app)
	app.run()