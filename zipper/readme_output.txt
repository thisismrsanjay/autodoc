## Indian-Sign-Language-Recognition-master/Image Preprocessing/image_processing.py



This code is used to detect and segment skin from an image. It takes an image path as an argument, reads the image, converts it to HSV format, applies a series of erosions and dilations to the mask using an elliptical kernel, blurs the mask to help remove noise, and then applies the mask to the frame. It also converts the image from HSV to BGR format, and then to gray format, and applies a Gaussian blur to highlight the main object. Finally, it applies a threshold to the image and returns the thresholded image.

## Indian-Sign-Language-Recognition-master/Image Preprocessing/preprocessing.py


This code is intended to create two csv files, train60.csv and train40.csv, which contain the label and flattened pixel values of images from the folder "train". The code uses the function "func" from the module "image_processing" to convert the images to black and white and flatten them. The csv files are written using the module "csv" with the fieldnames being "pixel0" to "pixel9215". For each subfolder of "train", the code writes 60% of the images to train60.csv and 40% of the images to train40.csv.

## Indian-Sign-Language-Recognition-master/Image Preprocessing/surf_image_processing.py



This code is used to detect and compute the features of an image. It is composed of two functions: func and func2. 

The func function takes a path to an image as an argument, converts the image to HSV, creates a skin mask, applies a median blur to the mask, computes the edges of the image using Canny, and then computes the SURF features of the image. 

The func2 function takes a path to an image as an argument, converts the image to HSV, creates a skin mask, applies a median blur to the mask, computes the edges of the image using Canny, and then computes the ORB features of the image. 

The code uses the following libraries: numpy, cv2, and matplotlib.pyplot.

## Indian-Sign-Language-Recognition-master/Visualization/visualize_submissions.py



This code is used to plot a confusion matrix for a given set of true labels and predicted labels. It imports pandas, numpy, matplotlib, and sklearn libraries. The function plot_confusion_matrix() takes in the confusion matrix, class names, and other parameters such as title, cmap, and normalize. It prints and plots the confusion matrix and returns a visual representation of the matrix.

## Indian-Sign-Language-Recognition-master/classification/classification.py


This code is used to run four different machine learning algorithms (Support Vector Machine (SVM), Naive Bayes (NB), K Nearest Neighbors (KNN) and Logistic Regression (LR)) on the data set. It imports the necessary packages and libraries, reads the csv files and assigns labels to the data. It then defines a function to calculate the accuracy of the algorithms, and four functions to run each of the algorithms. It then calls each of the four functions to run the algorithms.

## Indian-Sign-Language-Recognition-master/classification/saved_cnn.py



This code is an implementation of convolutional neural network (CNN) using TensorFlow and Python. It is used to predict the labels of images from the MNIST dataset. The code reads in test images and labels from the "test.csv" file and uses the trained variables from the "trained_variables2.ckpt" file. It then builds the TensorFlow graph with the weights and biases of the trained variables. It then evaluates the predictions of the labels of the test images and saves them in the "submission_cnn111.csv" file. Finally, it prints the accuracy score and precision score of the predictions.

