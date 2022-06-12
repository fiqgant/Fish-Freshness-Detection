#library
import streamlit as st
import streamlit_authenticator as stauth
import numpy as np
import pandas as pd
import pyrebase
import pickle
import random
from streamlit_option_menu import option_menu
from skimage.io import imread
from skimage.transform import resize
from PIL import Image
from datetime import datetime

# Configuration Key
firebaseConfig = {
    'apiKey': "AIzaSyBreWv9-b-gyoPLJHqPMLud8SuK_ItW6-U",
    'authDomain': "svmikan-9a49a.firebaseapp.com",
    'projectId': "svmikan-9a49a",
    'databaseURL': "https://svmikan-9a49a-default-rtdb.asia-southeast1.firebasedatabase.app",
    'storageBucket': "svmikan-9a49a.appspot.com",
    'messagingSenderId': "968860536004",
    'appId': "1:968860536004:web:064f46784a03d0e5480d91",
    'measurementId': "G-M69TR9Z56Z"
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()
st.sidebar.title("Silahkan Login")

# Authentication
choice = st.sidebar.selectbox('Login', ['Admin','User'])

#Path
path_ikan_jpg = r"./Img/ket_ikan.jpg"
path_model = r"./150.p"

# App 

# Login Block

if choice == 'Admin':
    # Obtain User Input for email and password
    email = st.sidebar.text_input('Please enter your email address')
    password = st.sidebar.text_input('Please enter your password',type = 'password')
    login = st.sidebar.checkbox('Login')
    st.title("Sistem Identifikasi Kesegaran Ikan Berdasarkan Citra Mata Menggunakan SVM")
    if login:
        user = auth.sign_in_with_email_and_password(email,password)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        bio = st.radio('Menu',['Tentang','Unggah','Kamera', 'Pengaturan', 'Dataset'])
        
        
# Pengaturan PAGE 
        if bio == 'Pengaturan':  
            # CHECK FOR IMAGE
            nImage = db.child(user['localId']).child("Image").get().val()    
            # IMAGE FOUND     
            if nImage is not None:
                # We plan to store all our image under the child image
                Image = db.child(user['localId']).child("Image").get()
                for img in Image.each():
                    img_choice = img.val()
                    #st.write(img_choice)
                st.image(img_choice)
                exp = st.expander('Change Bio and Image')  
                # User plan to change profile picture  
                with exp:
                    newImgPath = st.text_input('Enter full path of your profile imgae')
                    upload_new = st.button('Upload')
                    if upload_new:
                        uid = user['localId']
                        fireb_upload = storage.child(uid).put(newImgPath,user['idToken'])
                        a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                        db.child(user['localId']).child("Image").push(a_imgdata_url)
                        st.success('Success!')           
            # IF THERE IS NO IMAGE
            else:    
                st.info("No profile picture yet")
                newImgPath = st.text_input('Enter full path of your profile image')
                upload_new = st.button('Upload')
                if upload_new:
                    uid = user['localId']
                    # Stored Initated Bucket in Firebase
                    fireb_upload = storage.child(uid).put(newImgPath,user['idToken'])
                    # Get the url for easy access
                    a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                    # Put it in our real time database
                    db.child(user['localId']).child("Image").push(a_imgdata_url)
 # Beranda PAGE
        elif bio == 'Unggah':
            nImage = db.child(user['localId']).child("Image").get().val()         
            if nImage is not None:
                val = db.child(user['localId']).child("Image").get()
                for img in val.each():
                    img_choice = img.val()
                st.image(img_choice)
            else:
                st.info("No profile picture yet. Go to Edit Profile and choose one!")
                
            st.set_option('deprecation.showfileUploaderEncoding', False)
        
            st.text('Unggah Gambar')
                
            model = pickle.load(open(path_model, 'rb'))

            uploaded_file = st.file_uploader("Pilih gambar...", type='jpg')
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                st.image(img,caption='Gambar yang di unggah')
                    
            if st.button('PREDIKSI'):
                CATEGORIES = ['kurang segar','segar','tidak segar']
                st.write('Hasil...')
                flat_data=[]
                img = np.array(img)
                img_resized = resize(img, (150,150,3))
                flat_data.append(img_resized.flatten())
                flat_data = np.array(flat_data)
                y_out = model.predict(flat_data)
                y_out = CATEGORIES[y_out[0]]
                st.title(f' Prediksi: {y_out}')
                q = model.predict_proba(flat_data)
                for index, item in enumerate(CATEGORIES):
                    st.write(f'{item} : {q[0][index]*100}%')

                    
        elif bio == 'Kamera':
            nImage = db.child(user['localId']).child("Image").get().val()         
            if nImage is not None:
                val = db.child(user['localId']).child("Image").get()
                for img in val.each():
                    img_choice = img.val()
                st.image(img_choice)
            else:
                st.info("No profile picture yet. Go to Edit Profile and choose one!")
                
            st.set_option('deprecation.showfileUploaderEncoding', False)
        
            st.text('Unggah Gambar')
                
            model = pickle.load(open(path_model, 'rb'))

            picture = st.camera_input("Take a picture")
            if picture is not None:
                img= Image.open(picture)
                st.image(img,caption='Gambar yang di ambil')
                    
            if st.button('PREDIKSI'):
                CATEGORIES = ['kurang segar','segar','tidak segar']
                st.write('Hasil...')
                flat_data=[]
                img = np.array(img)
                img_resized = resize(img, (150,150,3))
                flat_data.append(img_resized.flatten())
                flat_data = np.array(flat_data)
                y_out = model.predict(flat_data)
                y_out = CATEGORIES[y_out[0]]
                st.title(f' Prediksi: {y_out}')
                q = model.predict_proba(flat_data)
                for index, item in enumerate(CATEGORIES):
                    st.write(f'{item} : {q[0][index]*100}%')

   # WORKPLACE FEED PAGE
        elif bio == 'Tentang' :
            st.markdown("<h1 style='text-align: center; color: white;'>Kenali Ciri Ikan Segar menurut SNI</h1>", unsafe_allow_html=True)
            imagefeed = Image.open(path_ikan_jpg)
            st.image(imagefeed, caption='Ciri Ikan Segar menurut SNI')
            st.markdown('Ikan merupakan salah satu sumber protein yang popular dan terbukti baik bagi kesehatan tubuh. Selain memiliki kandungan protein yang tinggi dan rendah lemak, beberapa kandungan nutrisi daging ikan yang bermanfaat bagi tubuh, diantaranya adalah omega 3 yang bermanfaat bagi pertumbuhan otak, kalsium dan fosfor untuk pembentukan tulang dan gigi, serta vitamin d yang membuat tulang, gigi dan otot selalu dalam kondisi prima. Dibalik kandungan nutrisinya yang begitu banyak, ikan ternyata juga salah satu bahan makanan yang sangat mudah mengalami kerusakan. Ikan yang telah rusak tentunya akan mengalami penurunan nilai nutrisi yang dikandungnya, dan bahkan dapat menjadi berbahaya bagi konsumen apabila ikan sudah mengalami pembusukan. Maka dari itu, kita perlu mengetahui dan dapat membedakan ikan seperti apa yang termasuk ke dalam kategori baik untuk dikonsumsi. Pemerintah Indonesia sendiri telah menentukan standar ciri ikan segar yang dituangkan dalam SNI  2729:2013 tentang Ikan segar yang dikeluarkan oleh Badan Standarisasi Nasional (BSN)')
            st.markdown('1. Mata')
            st.markdown('Ikan yang segar memiliki bola mata yang cembung, kornea dan pupil jernih, mengkilap, dan memiliki warna yang spesifik sesuai dengan jenis ikan masing – masing. Sementara ikan yang tidak segar memiliki ciri berupa bola mata yang sangat cekung, kornea sangat keruh, pupil abu-abu dan tidak mengkilap')
            st.markdown('2. Insang')
            st.markdown('Ikan segar memiliki warna insang merah tua atau coklat kemerahan, cemerlang dengan sedikit sekali lapisan lendir transparan. Sementara ikan yang tidak segar memiliki warna insang abu- abu, atau coklat keabuabuan dengan lendir coklat bergumpal')
            st.markdown('3. Lendir Permukaan Badan')
            st.markdown('Ikan segar memiliki lapisan lendir jernih, transparan, mengkilap cerah di seluruh badannya, sementara ikan yang tidak segar memiliki lapiran lendir tebal menggumpal, dan telah berubah warna')
            st.markdown('4. Daging')
            st.markdown('Ikan yang segar memiliki sayatan daging sangat cemerlang, spesifik jenis, jaringan daging sangat kuat. Sementara ikan yang tidak segar memiliki sayatan daging sangat kusam, jaringan daging Rusak')
            st.markdown('5. Bau')
            st.markdown('Ikan yang segar memiliki bau yang sangat segar yang spesifik sesuai dengan jenis ikan masing – masing. Sementara ikan yang tidak segar memiliki  bau busuk yang kuat.')
            st.markdown('6. Tekstur')
            st.markdown('Ikan segar memiliki tekstur daging sangat padat, kompak, dan sangat elastis ketika disentuh. Sementara ikan tidak segar memiliki tekstur daging yang sangat lunak, dan bekas jari tidak hilang apabila ikan disentuh.')
        
        elif bio == 'Dataset':
            st.write("Unggah Dataset disini [link](https://drive.google.com/drive/folders/1smK_ecrefcRLapbbLEy_49egn5HCtE2M?usp=sharing)")
            
##USERRRR

if choice == 'User':
    st.title("Sistem Identifikasi Kesegaran Ikan Berdasarkan Citra Mata Menggunakan SVM")
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    bio2 = st.radio('Menu',['U_Tentang','U_Unggah','U_Kamera', 'U_Dataset'])   

# Beranda PAGE 
    if bio2 == 'U_Unggah':
        nImage = ()
        if nImage is not None:
            val = db.child()
        else:    
            st.set_option('deprecation.showfileUploaderEncoding', False)
            st.text('Unggah Gambar')       
    
        model = pickle.load(open(path_model, 'rb'))

        uploaded_file = st.file_uploader("Pilih gambar...", type='jpg')
        if uploaded_file is not None:
                img = Image.open(uploaded_file)
                st.image(img,caption='Gambar yang di unggah')
                    
        if st.button('PREDIKSI'):
                CATEGORIES = ['kurang segar','segar','tidak segar']
                st.write('Hasil...')
                flat_data=[]
                img = np.array(img)
                img_resized = resize(img, (150,150,3))
                flat_data.append(img_resized.flatten())
                flat_data = np.array(flat_data)
                y_out = model.predict(flat_data)
                y_out = CATEGORIES[y_out[0]]
                st.title(f' Prediksi: {y_out}')
                q = model.predict_proba(flat_data)
                for index, item in enumerate(CATEGORIES):
                    st.write(f'{item} : {q[0][index]*100}%')
                    
    elif bio2 == 'U_Kamera':
                
        model = pickle.load(open(path_model, 'rb'))

        picture = st.camera_input("Take a picture")
        if picture is not None:
            img= Image.open(picture)
            st.image(img,caption='Gambar yang di ambil')
                
        if st.button('PREDIKSI'):
            CATEGORIES = ['kurang segar','segar','tidak segar']
            st.write('Hasil...')
            flat_data=[]
            img = np.array(img)
            img_resized = resize(img, (150,150,3))
            flat_data.append(img_resized.flatten())
            flat_data = np.array(flat_data)
            y_out = model.predict(flat_data)
            y_out = CATEGORIES[y_out[0]]
            st.title(f' Prediksi: {y_out}')
            q = model.predict_proba(flat_data)
            for index, item in enumerate(CATEGORIES):
                st.write(f'{item} : {q[0][index]*100}%')

# WORKPLACE FEED PAGE
    elif bio2 == 'U_Tentang':
            st.markdown("<h1 style='text-align: center; color: white;'>Kenali Ciri Ikan Segar menurut SNI</h1>", unsafe_allow_html=True)
            imagefeed = Image.open(path_ikan_jpg)
            st.image(imagefeed, caption='Ciri Ikan Segar menurut SNI')
            st.markdown('Ikan merupakan salah satu sumber protein yang popular dan terbukti baik bagi kesehatan tubuh. Selain memiliki kandungan protein yang tinggi dan rendah lemak, beberapa kandungan nutrisi daging ikan yang bermanfaat bagi tubuh, diantaranya adalah omega 3 yang bermanfaat bagi pertumbuhan otak, kalsium dan fosfor untuk pembentukan tulang dan gigi, serta vitamin d yang membuat tulang, gigi dan otot selalu dalam kondisi prima. Dibalik kandungan nutrisinya yang begitu banyak, ikan ternyata juga salah satu bahan makanan yang sangat mudah mengalami kerusakan. Ikan yang telah rusak tentunya akan mengalami penurunan nilai nutrisi yang dikandungnya, dan bahkan dapat menjadi berbahaya bagi konsumen apabila ikan sudah mengalami pembusukan. Maka dari itu, kita perlu mengetahui dan dapat membedakan ikan seperti apa yang termasuk ke dalam kategori baik untuk dikonsumsi. Pemerintah Indonesia sendiri telah menentukan standar ciri ikan segar yang dituangkan dalam SNI  2729:2013 tentang Ikan segar yang dikeluarkan oleh Badan Standarisasi Nasional (BSN)')
            st.markdown('1. Mata')
            st.markdown('Ikan yang segar memiliki bola mata yang cembung, kornea dan pupil jernih, mengkilap, dan memiliki warna yang spesifik sesuai dengan jenis ikan masing – masing. Sementara ikan yang tidak segar memiliki ciri berupa bola mata yang sangat cekung, kornea sangat keruh, pupil abu-abu dan tidak mengkilap')
            st.markdown('2. Insang')
            st.markdown('Ikan segar memiliki warna insang merah tua atau coklat kemerahan, cemerlang dengan sedikit sekali lapisan lendir transparan. Sementara ikan yang tidak segar memiliki warna insang abu- abu, atau coklat keabuabuan dengan lendir coklat bergumpal')
            st.markdown('3. Lendir Permukaan Badan')
            st.markdown('Ikan segar memiliki lapisan lendir jernih, transparan, mengkilap cerah di seluruh badannya, sementara ikan yang tidak segar memiliki lapiran lendir tebal menggumpal, dan telah berubah warna')
            st.markdown('4. Daging')
            st.markdown('Ikan yang segar memiliki sayatan daging sangat cemerlang, spesifik jenis, jaringan daging sangat kuat. Sementara ikan yang tidak segar memiliki sayatan daging sangat kusam, jaringan daging Rusak')
            st.markdown('5. Bau')
            st.markdown('Ikan yang segar memiliki bau yang sangat segar yang spesifik sesuai dengan jenis ikan masing – masing. Sementara ikan yang tidak segar memiliki  bau busuk yang kuat.')
            st.markdown('6. Tekstur')
            
            st.markdown('Ikan segar memiliki tekstur daging sangat padat, kompak, dan sangat elastis ketika disentuh. Sementara ikan tidak segar memiliki tekstur daging yang sangat lunak, dan bekas jari tidak hilang apabila ikan disentuh.')
    elif bio2 == 'U_Dataset':
            st.write("Unggah Dataset disini [link](https://drive.google.com/drive/folders/1smK_ecrefcRLapbbLEy_49egn5HCtE2M?usp=sharing)")
