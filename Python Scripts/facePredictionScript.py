# develop a classifier for the 5 Celebrity Faces Dataset
try:
    import sys
	from numpy import load
    from keras.models import load_model
    from mtcnn.mtcnn import MTCNN
    from PIL import Image
    from numpy import asarray
    from numpy import expand_dims
    from sklearn.preprocessing import LabelEncoder
    from sklearn.preprocessing import Normalizer
    from sklearn.svm import SVC
    from matplotlib import pyplot
except ImportError:
    print("There was a problem in importing one or more modules.")
        

############ GLOBAL SCOPE ##############

#loading face embeddings
data = load('my-dataset-embeddings.npz')
trainX, trainy, testX, testy = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']

# normalize input vectors
in_encoder = Normalizer(norm='l2')
trainX = in_encoder.transform(trainX)
testX = in_encoder.transform(testX)

#label encode targets
out_encoder = LabelEncoder()
out_encoder.fit(trainy)
trainy = out_encoder.transform(trainy)
testy = out_encoder.transform(testy)

# loading SVC model
model =  SVC(kernel='linear', probability=True)
model.fit(trainX, trainy)
print('svc loaded')

#loading keras model
keras_model = load_model('facenet_keras.h5')
print('Loaded facenet Model')

############ END OF GLOBAL SCOPE ############


# function to get_embedding
def get_embedding(face_pixels):
    
    face_pixels = face_pixels.astype('float32')
   
    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    
    # transform face into one sample
    samples = expand_dims(face_pixels, axis=0)
    
    # make prediction to get embedding
    yhat = keras_model.predict(samples)
    return yhat[0]


# function draw_faces to draw each face separately
def draw_faces(filename, result_list, required_size=(160, 160)):
    
    if (len(result_list)==0):
       print('no face detected')
       return []
       
    # load the image
    data = pyplot.imread(filename)
    myList = list()
    for i in range(len(result_list)):
        # get coordinates
        x1, y1, width, height = result_list[i]['box']
        x2, y2 = x1 + width, y1 + height
        #get face
        face = data[y1:y2, x1:x2]
        image = Image.fromarray(face)
        image = image.resize(required_size)
        face_array = asarray(image)
        myList.append(face_array)
        # define subplot
        pyplot.subplot(1, len(result_list), i+1)
        pyplot.axis('off')
        # plot face
        pyplot.imshow(face_array)
    print('detected faces: ')
    pyplot.show()
    return myList
        
        
def detect_faces(filename):
    #reading image
    pixels = pyplot.imread(filename)
    # to detect faces
    detector = MTCNN()
    #faces detected
    faces = detector.detect_faces(pixels)
    #detecting faces
    return draw_faces(filename, faces)



#function to predict faces
def prediction(myList):
    
    for test_face in myList:
        #embedding for each face to compare and predict
        embedding = get_embedding(test_face)
        samples = expand_dims(embedding, axis=0)
        yhat_class = model.predict(samples)
        yhat_prob = model.predict_proba(samples)

        # get name and probability
        class_index = yhat_class[0]
        class_probability = yhat_prob[0,class_index] * 100

        predict_names = out_encoder.inverse_transform(yhat_class)
#         print('predict_name: ', predict_names)
        print('Predicted: %s (%.3f)' % (predict_names[0], class_probability))

        # plot for fun
        pyplot.imshow(test_face)
        title = '%s (%.3f)' % (predict_names[0], class_probability)
        pyplot.title(title)
        pyplot.show()
    
    

def main():
    
    #list to store array of detected_faces
    filename = 'specialTest02.jpg'
    faceList = detect_faces(filename)
    if(len(faceList)==0):
       sys.exit('no face to predict...aborting')
    faceList = asarray(faceList)
    print('shape of list containing detected faces: ', faceList.shape)
      
    #predicting faces
    prediction(faceList)

    
if __name__=="__main__":
    main()
    print('done')