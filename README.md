# Social Image Description Platform
## Overview 
This project presents a neural network that learns annotating an image with a set tags.
// photos + annot
The neural network is also deployed on a photo sharing website where users can upload images.

### Architecture
The neural network is a multilabel classifier is composed of a deep convolution neural network and a multilayer perceptron.
First the image is sent to the CNN which embeds the image into a fix-length vector. Then, the multilayer perceptron predicts the 
labels that describe the best the image.
// shcema architecture
The model uses transfer learning with Inception-v3 as it shows state of the art performances on the ILSVR challenge.
https://arxiv.org/abs/1512.00567
For more information you can check out this [tensorflow-tutorial](https://www.tensorflow.org/versions/r0.9/how_tos/image_retraining/index.html)

This github repo is divided into 2 parts : img_platform and ml_core. 
img_platform contains all the sources for the website.
ml_core contains the sources for the classifier, it can be run independently of the website.

## Running the neural network
Requirements
* tensorflow (tested on 0.11)
* numpy

### Preprocess the data
This project is based on the MIRFLICKR 25K dataset and can be downloaded from this http://press.liacs.nl/mirflickr/
M. J. Huiskes, M. S. Lew (2008). The MIR Flickr Retrieval Evaluation. ACM International Conference on Multimedia Information Retrieval (MIR'08), Vancouver, Canada
To run the dataset processing script :
cd ml_core/mirflickrdata/

python build_tfr_data.py --image_dir=path/to/image/dir --annot_dir=path/to/annotation/dir --output_dir=mirflickrdata/output


This script process the raw dataset into tensorflow records files : train-???-008.tfr, test-???-004.tfr, val-???-001.tfr
The record file contains proto examples containing the image name, the jpeg string of the image and the labels encoded as a binary vector.

### Train the network
Training the full network end-to-end is computation intensive (one epoch takes arround 4h on a macbook pro without GPU).
Therefore in this project we only train the classifier that follows the CNN, there will be no fine-tuning of Inception.
First, run the caching script : 

python cache_bottlenecks.py --image_dir=mirflickrdata/images/ --output_dir=mirflickrdata/output/

This script will run each image in the CNN once to extract the image embedding vector. Each vector in stored in the output directory as name-of-the-image.jpg.txt . It takes arround 1h30 to process the 25000 images.
Once the caching is done, we can train the classifier

python train.py --tfr_dir=mirflickrdata/ --model_dir=models/model

and evaluate it

python evaluate.py --tfr_dir=mirflickrdata/ --model_dir=models/model



## Running the website
Requires Node.js

cd img_platform/
pip install -r requirements.txt
npm install -g bower
npm install
bower install
python manage.py migrate
python manage.py runserver

