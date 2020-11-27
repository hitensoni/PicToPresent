# Import statements.
try:
    import sys
    import numpy as np
    import tensorflow as tf
    
    from keras.models import load_model
    from mtcnn.mtcnn import MTCNN
    from PIL import Image
    from sklearn.preprocessing import LabelEncoder
    from sklearn.preprocessing import Normalizer
except ImportError:
    print("There was a problem in importing one or more modules.")

# This function returns a neural network which is further used for classification.
def getModel():
    model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation=tf.nn.relu),
    tf.keras.layers.Dense(13, activation=tf.nn.softmax)
    ])
    model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
    return model

# Main Method.
def main():
    
    model = getModel()
    
    try:
        data = np.load('DATA/face_data_embedded.npz')
    except:
        sys.exit('There was a problem while importing embedded dataset. Make sure you have specified the correct path.')
        
    trainX, trainy, testX, testy = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']
    
#     Encode the embedded data
    in_encoder = Normalizer('l2')
    trainX = in_encoder.transform(trainX)
    testX = in_encoder.transform(testX)
    
#     Encode the labels
    out_encoder = LabelEncoder()
    out_encoder.fit(trainy)
    trainy = out_encoder.transform(trainy)
    testy = out_encoder.transform(testy)
    
#     Train the model
    model.fit(trainX, trainy, epochs = 100)
    test_loss, test_acc = model.evaluate(testX, testy)
    print('The test data lost and accuracy of your dataset is : '.format(test_loss, test_acc))
    model.save('my_model.h5')
    print('Converting the model into tflite...\n')
    
#     Saving the model as a tflite file.	
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    open("tflite_model.tflite", "wb").write(tflite_model)
    print('TFLite model has been saved successfully with the name tflite_model.tflite.')
    print('*******end*******')
    
if __name__=="__main__":
    main()
