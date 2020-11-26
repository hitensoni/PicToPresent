import flask
import werkzeug
import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)
import numpy as np
from mtcnn.mtcnn import MTCNN
from PIL import Image
import tensorflow as tf

from keras.models import load_model
app = flask.Flask(__name__)
model = load_model('my_model.h5')
facenet_model = load_model('facenet_keras.h5')

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


@app.route('/', methods=['GET', 'POST'])
def test():
    imagefile = flask.request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
    print("\nReceived image File name : " + imagefile.filename)
    imagefile.save(filename)
    faces = extract_face(filename)
    names = []
    accuracyList = []
    embs = []
    for i in range(len(faces)):
        embedding = get_embedding(faces[i])
        embs.append(embedding)
    for emb in embs:
        test = np.expand_dims(emb, axis=0)
    #     predict_class = model.predict_classes(test)
        predict_class = np.argmax(model.predict(test), axis=-1)
    #     print('size predict_class = ', predict_class.size)
    #     print('predict_class: ',predict_class)
        predict_prob = model.predict(test)
    #     print('size predict_prob = ', predict_prob.size)
    #     print('predict_prob: ', predict_prob)
        class_index = predict_class[0]
    #     print('class_index: ', class_index)
    #     print()
    #     print('accuracy[0]: ',predict_prob[0])
    #     print()
        accuracy = predict_prob[0, class_index]
    #     print('accuracy: ',accuracy)
        accuracy = accuracy*100
        accuracyList.append(accuracy)
        name = out_encoder.inverse_transform(predict_class)
    #     print('name: ',name)
        names.append(name)
    
    

    return "Image Uploaded Successfully"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)