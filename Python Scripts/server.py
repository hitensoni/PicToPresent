import flask
import werkzeug
import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)
import numpy as np
import tensorflow as tf
import keras
from mtcnn.mtcnn import MTCNN
from PIL import Image
from sklearn.preprocessing import LabelEncoder

app = flask.Flask(__name__)
model = tf.keras.models.load_model('my_model.h5', compile=False)
facenet_model = tf.keras.models.load_model('facenet_keras.h5')

def extract_face(filename, required_size=(160, 160)):
#     print(filename)
    image = Image.open(filename)
    image = image.convert('RGB')
    pixels = np.asarray(image)
    detector = MTCNN()
    faces = detector.detect_faces(pixels)
    face_list = []
    i=0
    if len(faces)==0:
        print('No faces were detected in the image {}'.format(filename))
        return
    for face in faces:
        x1, y1, width, height = faces[i]['box']
        i=i+1
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        face = pixels[y1:y2, x1:x2]
        image = Image.fromarray(face)
        image = image.resize(required_size)
        face_array = np.asarray(image)
        face_list.append(face_array)
    return face_list

def get_embedding(pixels):
    pixels = pixels.astype('float32')
    mean, std = pixels.mean(), pixels.std()
    pixels = (pixels-mean)/std
    samples = np.expand_dims(pixels, 0)
    yhat = facenet_model.predict(samples)
    return yhat[0]

def get_out_encoder():
    try:
        data = np.load('DATA/face_data_embedded.npz')
    except:
        sys.exit('There was a problem while importing embedded dataset. Make sure you have specified the correct path.')
        
    trainX, trainy, testX, testy = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']
    
    out_encoder = LabelEncoder()
    out_encoder.fit(trainy)
    return out_encoder

@app.route('/', methods=['GET', 'POST'])
def test():
    imagefile = flask.request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
    print("\nReceived image File name : " + imagefile.filename)
    imagefile.save(filename)
    
    out_encoder = get_out_encoder()
    faces = extract_face(filename)
    names = []
    accuracyList = []
    embs = []
    
    for i in range(len(faces)):
        embedding = get_embedding(faces[i])
        embs.append(embedding)
        
    for emb in embs:
        test = np.expand_dims(emb, axis=0)
        predict_class = np.argmax(model.predict(test), axis=-1)
        predict_prob = model.predict(test)
        class_index = predict_class[0]
        accuracy = predict_prob[0, class_index]
        accuracy = accuracy*100
        accuracyList.append(accuracy)
        name = out_encoder.inverse_transform(predict_class)
        names.append(name)
        print('name type: ', type(name.tolist()))
        print('accuracylist type: ', type(accuracyList))
    
    print('accuracyList: ')
    for i in range(len(accuracyList)):
        print(accuracyList[i])
    print('name:')
    for i in range(len(names)):
        print(names[i])
#     return "Image Uploaded Successfully"
    return flask.jsonify(predictions=name.tolist(), probabilities=accuracyList)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)