## Indian-Sign-Language-Recognition-master/Image Preprocessing/image_processing.py



This code takes an image as input and returns a binary image. The code converts the image from RGB to HSV and then creates a mask with lower and upper boundary which is used to extract the skin from the image. Then a series of erosions and dilations are applied to the mask. The mask is then blurred and the skin is extracted from the image. The image is then converted from HSV to BGR and then to gray. Gaussian blur is applied to the image and a threshold is used to convert the image to binary.

## Indian-Sign-Language-Recognition-master/Image Preprocessing/preprocessing.py



This code is used to create two csv files, train60.csv and train40.csv, which contain the label of the images and the flattened pixel values of the images. It takes the images from the folder train, flattens them and stores the label and flattened pixel values in the two csv files. The label of the images is stored in the first column of the csv file. The images are flattened and stored in the remaining columns of the csv file. It also prints the directory names and the file names in the command prompt.

## Indian-Sign-Language-Recognition-master/Image Preprocessing/surf_image_processing.py



This code is used to detect the skin tone of a person in a given image. The code works by first converting the image from RGB to HSV and then using the inRange function to detect the skin tone of the person. After that it uses medianBlur to blur the image and then uses Canny edge detection to detect the edges of the image. Finally, it uses SURF or ORB to detect the keypoints in the image and return the descriptor.

## Indian-Sign-Language-Recognition-master/Visualization/visualize_submissions.py



This code is used to generate a confusion matrix for a given set of predictions and labels. 
The code takes two parameters, y_pred and y_test, which are the predicted labels and the true labels respectively. The code then creates a confusion matrix for the given parameters and plots it on a graph. The code also prints out the confusion matrix and the total number of correct predictions for each label. This code can be used to evaluate the performance of a classification model.

## Indian-Sign-Language-Recognition-master/classification/classification.py



This code is used to classify images into digits from 0 to 9. The dataset is divided into train60 and train40 for training and testing respectively. The code contains 4 classification algorithms: Support Vector Machines (SVM), Naive Bayes (NB), K Nearest Neighbours (KNN) and Logistic Regression (LR). The code uses the sklearn library for the classification algorithms and pandas for reading the csv files.

The code first reads the csv files and stores the labels in the variable y and the features in the variable x. It then divides the data into train and test sets. The code then uses the 4 classification algorithms to classify the images. It then calculates the accuracy, precision, F1 score and recall score for each algorithm. Finally, it stores the predicted labels in a csv file.

## Indian-Sign-Language-Recognition-master/classification/saved_cnn.py



This code is a basic implementation of a Convolutional Neural Network (CNN) using TensorFlow. It is used to classify images of handwritten digits. The code reads in the test data, sets up the CNN, and defines the weights and biases for each layer. It then evaluates the test data and outputs the predicted labels in a csv file. Finally, the accuracy and precision of the predictions are calculated.

