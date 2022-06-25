# library
import streamlit as st
import numpy as np
import pandas as pd
import pickle
import random
from streamlit_option_menu import option_menu
from skimage.io import imread
from skimage.transform import resize
from PIL import Image
from datetime import datetime
from streamlit_cropper import st_cropper
import streamlit.components.v1 as html
from st_aggrid import AgGrid
import plotly.express as px
import io
import sqlite3

st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_page_config(page_title="Devina SVM", page_icon="./favicon.ico", layout="centered", initial_sidebar_state="auto", menu_items={
    'Get Help': 'https://www.extremelycoolapp.com/help',
    'Report a bug': "https://www.extremelycoolapp.com/bug",
    'About': "# This is a header. This is an *extremely* cool app!"
})
# Configuration Key

conn = sqlite3.connect("data.db")
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS usertable(username TEXT, password TEXT)')

def add_userdata(username, password):
    c.execute('INSERT INTO usertable(username, password) VALUES (?,?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM usertable WHERE username =? AND password =?', (username, password))
    data = c.fetchall()
    return data

def view_all_users():
    c.execute('SELECT * FROM usertable')
    data = c.fetchall()
    return data

st.sidebar.title("Silahkan Login")

# Authentication
choice = st.sidebar.selectbox('Login', ['Admin', 'User'])

# Path
path_ikan_jpg = r"./Img/ket_ikan.jpg"
path_model = r"./150.p"


# App

# Login Block


if choice == 'Admin':
    # Obtain User Input for email and password
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password", type= "password")
    if st.sidebar.checkbox("Login"):
        create_usertable()
        result = login_user(username, password)
        if result:
            st.success("Masuk sebagai {}".format(username))
            choose = option_menu("Menu", ["Tentang", "Unggah", "Kamera", "Pengaturan", "Dataset"],
                    icons=['info-circle', 'upload','camera', 'gear', 'file-arrow-up'],
                    menu_icon="app-indicator", 
                    default_index=0, 
                    orientation="horizontal",
                    styles={
                            "container": {"padding": "5!important", "background-color": "#040404"},
                            "icon": {"color": "orange", "font-size": "15px"},
                            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                            "nav-link-selected": {"background-color": "#02ab21"},
                    }
            )


# Beranda PAGE
            if choose == 'Pengaturan':
                st.header(
                "Sistem Identifikasi Kesegaran Ikan Berdasarkan Citra Mata Menggunakan SVM", anchor=None)
                

            elif choose == 'Unggah':
                st.set_option('deprecation.showfileUploaderEncoding', False)
                st.text('Unggah Gambar')

                model = pickle.load(open(path_model, 'rb'))

                uploaded_file = st.file_uploader("Pilih gambar...", type='jpg')
                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    realtime_update = st.sidebar.checkbox(
                        label="Update in Real Time", value=True)
                    box_color = st.sidebar.color_picker(
                        label="Box Color", value='#0000FF')
                    aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=[
                                                    "1:1", "16:9", "4:3", "2:3", "Free"])
                    aspect_dict = {
                        "1:1": (1, 1),
                        "16:9": (16, 9),
                        "4:3": (4, 3),
                        "2:3": (2, 3),
                        "Free": None
                    }
                    aspect_ratio = aspect_dict[aspect_choice]

                if uploaded_file:
                    img = Image.open(uploaded_file)
                    if not realtime_update:
                        st.write("Double click to save crop")
                    # Get a cropped image from the frontend
                    st.write("Crop gambar")
                    cropped_img = st_cropper(
                        img, realtime_update=realtime_update, box_color=box_color, aspect_ratio=aspect_ratio)

                    # Manipulate cropped image at will
                    st.write("Preview")
                    _ = cropped_img.thumbnail((150, 150))
                    st.image(cropped_img)

                if st.button('PREDIKSI'):
                    CATEGORIES = ['kurang segar', 'segar', 'tidak segar']
                    st.write('Hasil...')
                    flat_data = []
                    img = np.array(cropped_img)
                    img_resized = resize(img, (150, 150, 3))
                    flat_data.append(img_resized.flatten())
                    flat_data = np.array(flat_data)
                    y_out = model.predict(flat_data)
                    y_out = CATEGORIES[y_out[0]]
                    st.title(f' Prediksi: {y_out}')
                    q = model.predict_proba(flat_data)
                    for index, item in enumerate(CATEGORIES):
                        st.write(f'{item} : {q[0][index]*100}%')

            elif choose == 'Kamera':
                st.set_option('deprecation.showfileUploaderEncoding', False)
                model = pickle.load(open(path_model, 'rb'))

                picture = st.camera_input("Take a picture")
                if picture is not None:
                    img = Image.open(picture)
                    realtime_update = st.sidebar.checkbox(
                        label="Update in Real Time", value=True)
                    box_color = st.sidebar.color_picker(
                        label="Box Color", value='#0000FF')
                    aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=[
                                                    "1:1", "16:9", "4:3", "2:3", "Free"])
                    aspect_dict = {
                        "1:1": (1, 1),
                        "16:9": (16, 9),
                        "4:3": (4, 3),
                        "2:3": (2, 3),
                        "Free": None
                    }
                    aspect_ratio = aspect_dict[aspect_choice]

                if picture:
                    img = Image.open(picture)
                    if not realtime_update:
                        st.write("Double click to save crop")
                    # Get a cropped image from the frontend
                    st.write("Crop gambar")
                    cropped_img = st_cropper(
                        img, realtime_update=realtime_update, box_color=box_color, aspect_ratio=aspect_ratio)

                    # Manipulate cropped image at will
                    st.write("Preview")
                    _ = cropped_img.thumbnail((150, 150))
                    st.image(cropped_img)

                if st.button('PREDIKSI'):
                    CATEGORIES = ['kurang segar', 'segar', 'tidak segar']
                    st.write('Hasil...')
                    flat_data = []
                    img = np.array(cropped_img)
                    img_resized = resize(img, (150, 150, 3))
                    flat_data.append(img_resized.flatten())
                    flat_data = np.array(flat_data)
                    y_out = model.predict(flat_data)
                    y_out = CATEGORIES[y_out[0]]
                    st.title(f' Prediksi: {y_out}')
                    q = model.predict_proba(flat_data)
                    for index, item in enumerate(CATEGORIES):
                        st.write(f'{item} : {q[0][index]*100}%')

            # WORKPLACE FEED PAGE
            elif choose == 'Tentang':
                st.markdown(
                    "<h1 style='text-align: center; color: white;'>Kenali Ciri Ikan Segar menurut SNI</h1>", unsafe_allow_html=True)
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
            elif choose == 'Dataset':
                st.write(
                    "Unggah Dataset disini")
                if st.button("Unggah"):
                    "[klik disini](https://drive.google.com/drive/folders/1smK_ecrefcRLapbbLEy_49egn5HCtE2M?usp=sharing)"

if choice == 'User':
    choose2 = option_menu("Menu", ["Tentang", "Unggah", "Kamera", "Dataset"],
                          icons=['info-circle', 'upload',
                                 'camera', 'file-arrow-up'],
                          menu_icon="app-indicator", default_index=0, orientation="horizontal",
                          styles={
        "container": {"padding": "5!important", "background-color": "#040404"},
        "icon": {"color": "orange", "font-size": "15px"},
        "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#02ab21"},
    }
    )
    st.header(
        "Sistem Identifikasi Kesegaran Ikan Berdasarkan Citra Mata Menggunakan SVM", anchor=None)
    st.write(
        '<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

# Beranda PAGE
    if choose2 == 'Unggah':
        model = pickle.load(open(path_model, 'rb'))

        uploaded_file = st.file_uploader("Pilih gambar...", type='jpg')
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            realtime_update = st.sidebar.checkbox(
                label="Update in Real Time", value=True)
            box_color = st.sidebar.color_picker(
                label="Box Color", value='#0000FF')
            aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=[
                                             "1:1", "16:9", "4:3", "2:3", "Free"])
            aspect_dict = {
                "1:1": (1, 1),
                "16:9": (16, 9),
                "4:3": (4, 3),
                "2:3": (2, 3),
                "Free": None
            }
            aspect_ratio = aspect_dict[aspect_choice]

        if uploaded_file:
            img = Image.open(uploaded_file)
            if not realtime_update:
                st.write("Double click to save crop")
            # Get a cropped image from the frontend
            st.write("Crop gambar")
            cropped_img = st_cropper(
                img, realtime_update=realtime_update, box_color=box_color, aspect_ratio=aspect_ratio)

            # Manipulate cropped image at will
            st.write("Preview")
            _ = cropped_img.thumbnail((150, 150))
            st.image(cropped_img)
            # crp_img = cropped_img
            # im = Image.open(crp_img)
            # pal = getPalletteInRgb(im)

        if st.button('PREDIKSI'):
            CATEGORIES = ['kurang segar', 'segar', 'tidak segar']
            st.write('Hasil...')
            flat_data = []
            img = np.array(cropped_img)
            img_resized = resize(img, (150, 150, 3))
            flat_data.append(img_resized.flatten())
            flat_data = np.array(flat_data)
            y_out = model.predict(flat_data)
            y_out = CATEGORIES[y_out[0]]
            st.title(f' Prediksi: {y_out}')
            q = model.predict_proba(flat_data)
            for index, item in enumerate(CATEGORIES):
                st.write(f'{item} : {q[0][index]*100}%')

    elif choose2 == 'Kamera':

        model = pickle.load(open(path_model, 'rb'))

        picture = st.camera_input("Take a picture")
        if picture is not None:
            img = Image.open(picture)
            realtime_update = st.sidebar.checkbox(
                label="Update in Real Time", value=True)
            box_color = st.sidebar.color_picker(
                label="Box Color", value='#0000FF')
            aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=[
                                             "1:1", "16:9", "4:3", "2:3", "Free"])
            aspect_dict = {
                "1:1": (1, 1),
                "16:9": (16, 9),
                "4:3": (4, 3),
                "2:3": (2, 3),
                "Free": None
            }
            aspect_ratio = aspect_dict[aspect_choice]

        if picture:
            img = Image.open(picture)
            if not realtime_update:
                st.write("Double click to save crop")
            # Get a cropped image from the frontend
            st.write("Crop gambar")
            cropped_img = st_cropper(
                img, realtime_update=realtime_update, box_color=box_color, aspect_ratio=aspect_ratio)

            # Manipulate cropped image at will
            st.write("Preview")
            _ = cropped_img.thumbnail((150, 150))
            st.image(cropped_img)
            # img_rgb = cropped_img.convert("RGB")
            # # rgb_pixel_value = img_rgb.getpixel((10, 10))
            # # st.write(f' Nilai RGB: {rgb_pixel_value}')
            # pix = img_rgb.load()
            # # For loop to extract and print all pixels
            # st.write(f'Nilai RGB:')
            # for x in range(img_rgb.width):
            #     for y in range(img_rgb.width):
            #         # getting pixel value using getpixel() method
            #         bb = (img_rgb.getpixel((x, y)))
            #         st.write(f'{bb}')

        if st.button('PREDIKSI'):
            CATEGORIES = ['kurang segar', 'segar', 'tidak segar']
            st.write('Hasil...')
            flat_data = []
            img = np.array(cropped_img)
            img_resized = resize(img, (150, 150, 3))
            flat_data.append(img_resized.flatten())
            flat_data = np.array(flat_data)
            y_out = model.predict(flat_data)
            y_out = CATEGORIES[y_out[0]]
            st.title(f' Prediksi: {y_out}')
            q = model.predict_proba(flat_data)
            for index, item in enumerate(CATEGORIES):
                st.write(f'{item} : {q[0][index]*100}%')

# WORKPLACE FEED PAGE
    elif choose2 == 'Tentang':
        st.markdown(
            "<h1 style='text-align: center; color: white;'>Kenali Ciri Ikan Segar menurut SNI</h1>", unsafe_allow_html=True)
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
    elif choose2 == 'Dataset':
        st.write(
            "Unggah Dataset disini")
        if st.button("Unggah"):
            "[klik disini](https://drive.google.com/drive/folders/1smK_ecrefcRLapbbLEy_49egn5HCtE2M?usp=sharing)"
