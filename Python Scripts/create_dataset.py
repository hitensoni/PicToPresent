# Improt statements.
try:
    import os
    import sys
    from os import listdir
    import mtcnn
    import numpy as np
    import cv2
    import tensorflow as tf
    from PIL import Image
    from keras.models import load_model
except:
    print('An error occured while importing one or more modules.')

# Custom class to handle exceptions while detecting face.
class DetectionError(Exception):
    pass

# Utility function to detect and return face found in image as numpy array.
def extract_face(filename, required_size=(160, 160)):
#     print(filename)
    image = Image.open(filename)
    image = image.convert('RGB')
    if image.width>image.height:
        image = image.rotate(270)
    pixels = np.asarray(image)
    detector = mtcnn.MTCNN()
    faces = detector.detect_faces(pixels)
    if len(faces)!=1:
        print('Either multiple or no faces were detected in the image : {} '.format(filename))
        return 'end', 'end'
    x1, y1, width, height = faces[0]['box']
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    face = pixels[y1:y2, x1:x2]
    image = Image.fromarray(face)
    image = image.resize(required_size)
    image.save(filename)
    face_array = np.asarray(image)
    return face_array, 'true'

# Utility function to loop over all the files in a folder.
def load_faces(directory):
    faces = list()
    for filename in os.listdir(directory):
        path = directory + filename
        face, stat = extract_face(path)
        if stat!='end':
            faces.append(face)
    return faces

# Utility function to load dataset into lists.
def load_dataset(directory):
    X, y = list(), list()
    for subdir in listdir(directory):
        path = directory + subdir + '/'
        if not os.path.isdir(path):
            continue
        faces = load_faces(path)
        labels = [subdir for _ in range(0, len(faces))]
        print('Found {} faces with label {}.'.format(len(faces), subdir))
        X.extend(faces)
        y.extend(labels)
    return X, y

# Utility function to create embeddings for a single image.
def get_embedding(model, pixels):
    pixels = pixels.astype('float32')
    mean, std = pixels.mean(), pixels.std()
    pixels = (pixels-mean)/std
    samples = np.expand_dims(pixels, 0)
    yhat = model.predict(samples)
    return yhat[0]

# Function which calls get_embedding for every element in the dataset.
def get_embeddings(trainX, testX):
    try:
        model = load_model('facenet_keras.h5')
    except FileNotFoundError:
        sys.exit('Unable to locate Facenet Keras model. Aborting.')
    else:
        print('Model Loaded Successfully')
        newtrainX, newtestX = list(), list()
        for face in trainX:
            embedded = get_embedding(model, face)
            newtrainX.append(embedded)
        newtrainX = np.asarray(newtrainX)
        for face in testX:
            embedded = get_embedding(model, face)
            newtestX.append(embedded)
        newtestX = np.asarray(newtestX)
        return newtrainX, newtestX

def initialize():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
# Main function.
def main():
    initialize()
    trainPath = 'DATA/Images/Dataset/train/'
    testPath = 'DATA/Images/Dataset/test/'
    try:
        print('***Working on train data***')
        trainX, trainy = load_dataset(trainPath)
        print('')
        print('***Working on test data***')
        testX, testy = load_dataset(testPath)
    except FileNotFoundError:
        print('Please check the file path you entered exists and is correct. Aborting.')
        return
    else:
        print('')
        print('Size of train data is : {}.'.format(len(trainX)))
        print('Size of test data is : {}.'.format(len(testX)))
        np.savez_compressed('DATA/face_data.npz', trainX, trainy, testX, testy)
        print('Data has been stored in numpy compressed form in the DATA folder.')
        print('')
        print('Now working on face embeddings.')
        data = np.load('DATA/face_data.npz')
        trainX, trainy, testX, testy = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']
        print('Loaded : {} {} {} {}'.format(trainX.shape, trainy.shape, testX.shape, testy.shape))
        
#       Create embedding for faces using Facenet model.
        newtrainX, newtestX = get_embeddings(trainX, testX)
        np.savez_compressed('face_data_embedded.npz', newtrainX, trainy, newtestX, testy)
        print('Embedded data has been stored in 1x128 vectors in the DATA folder.')
        print('*******end*******')
        
if __name__=="__main__":
    main()
