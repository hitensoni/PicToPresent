# Import statements.
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

try:
    import os
    import sys
    import shutil
    import numpy as np
    import cv2
    import mtcnn
    from PIL import Image
except ImportError:
    sys.exit("There was a problem in importing one or more modules.")

# Custom class to handle exceptions while detecting face.
class DetectionError(Exception):
    pass

# Utility function to check if a folder already exixts for given student. If it does, we give a choice to delete the existing folder and click fresh images.
def imagePath(roll):
    try:
        path = 'DATA/Images/Dataset/Train/' + roll
        os.makedirs(path)
    except:
        print('There was an error creating a directory with your inputs.')
        choice = str(input('Do you want to delete the current directory belonging to this profile?'))
        if choice=='y':
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            return 'end'
    return 'ok', path

# Utility function to detect and return face found in live frames as numpy array.
def detect_face(img):
    pixels = np.asarray(img)
    detector = mtcnn.MTCNN()
    faces = detector.detect_faces(pixels)
    try:
        if(len(faces)!=1):
            raise DetectionError
    except DetectionError:
        print("Either no or multiple faces were found in the captured image.")
        pass
    x1, y1, width, height = faces[0]['box']
    x2 = x1 + width
    y2 = y1 + height
    face = pixels[y1:y2, x1:x2]
    return face

# Main function which accepts user input and saves photos at appropriate locations.
def main():
    ch = 'y'
    detector = mtcnn.MTCNN()
    while(ch=='y' or ch=='Y'):
        try:
            cap = cv2.VideoCapture(0)
        except:
            sys.exit('An error occured while initializing the camera.')
        i=0
        
        name = input('Enter name : ')
        roll = input('Enter roll no. : ')
        year = input('Enter graduation year : ')
        branch = input('Enter branch : ')
        
        isImageDirPresent, path = imagePath(roll)
        if isImageDirPresent=='end':
            continue
        print('Directory created successfully.')
        print('Alright. Good to go. Say cheese...')
        
#       To capture an image, press 'c'. To end capturing, press (or long press) 'q'.
        while(True):
            try:
                mydir = path
                ret, frame = cap.read()
                frame = cv2.flip(frame, 1)
                cv2.imshow('Capturing', frame)
                if cv2.waitKey(1) & 0xff==ord('c'):
                    face = detectFace(frame)
                    filename = os.path.join(path, str(i) + '.jpg')
    #                 print(filename)
                    cv2.imwrite(filename, frame)
                    i = i+1
                elif cv2.waitKey(1) & 0xff==ord('q'):
                    break
            except:
                print("Something went wrong")
        cap.release()
        cv2.destroyAllWindows()
        print('Saved {} images of {}.'.format(i, name))
        print('')
        ch = input('Run again ? (y/n) : ')
        
    print('*******end*******')
    
if __name__=="__main__":
    main()