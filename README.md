# Social Image Description Platform
This project is part of Udacity MLND program.

The report is available here : [Report.pdf](https://github.com/Nlte/social-image-platform/blob/master/Report.pdf)

## Overview
This project presents a neural network that learns annotating an image with a set tags.

The neural network is also deployed on a photo sharing website where users can upload images.

### Architecture
The neural network is a multilabel classifier is composed of a deep convolution neural network and a multilayer perceptron.
First the image is sent to the CNN which embeds the image into a fix-length vector. Then, the multilayer perceptron predicts the labels that describe the best the image.
<div style="text-align:center">
<img src="https://raw.githubusercontent.com/Nlte/social-image-platform/master/docs/architecture.jpg"/>
</div>
The model uses transfer learning with Inception-v3 as it shows state of the art performances on the ILSVR challenge.
For more information you can check out this [tensorflow-tutorial](https://www.tensorflow.org/versions/r0.9/how_tos/image_retraining/index.html)

This github repo is divided into 2 parts :
- img_platform : contains all the sources for the website.
- ml_core : contains the sources for the classifier.


## Training the neural network
Requirements
- tensorflow (tested on 1.5)
- numpy
- matplotlib
- pandas

### Preprocess the data
This project is based on the MIRFLICKR 25K dataset.

>M. J. Huiskes, M. S. Lew (2008). The MIR Flickr Retrieval Evaluation. ACM International Conference on Multimedia Information Retrieval (MIR'08), Vancouver, Canada

NOTE : The dataset consists of 25000 images, annotations and metadata. It takes arround 3.5 GB on the hard-drive.

First, download the dataset :

```sh
cd ml_core/data/
./download_dataset.sh
```
It will create two directories in `data/`:

```sh
+-- data
|   +-- annotation # annotation text files
|   +-- mirflickr # images
```
Create the `annotations.json` file with :
```sh
python create_json_annotation.py
```
Then, run the processing script :
```sh
python build_tfr_data.py
```
This script converts the annotations.json into tensorflow records files : `train-???-008.tfr` , `test-???-004.tfr` , `val-???-001.tfr` and store them into `output/`.
Each record file consists of proto examples containing the image name and the labels associated with it.

### Train the network
Training the full network end-to-end is computation intensive (one epoch takes arround 4h on a macbook pro with CPU only). Therefore in this project, we'll be only training the classifier that follows the CNN, there will be no fine-tuning of Inception.
We need to extract and save the cnn feature of each image.
To run the caching script :
```sh
cd ..
python cache_bottlenecks.py
```
This script will run each image in the CNN once to extract the image embedding vector. Each vector in stored in the `ml_core/data/bottlenecks` directory as `name-of-the-image.jpg.txt` .
It takes arround 1h30 to process the 25000 images from the dataset.

Once the caching is done, we can train the classifier :

```sh
python train.py
```
This script builds a model according to the hyperparameters set in the class `ModelConfig` in `configuration.py`.
During the training process, the loss values and the mean AUC can be monitored in tensorboard.
```sh
# In a new terminal
tensorboard --logdir=models/model
```
The model is trained for 10 epochs, after that a checkpoint is created in `ml_core/models/model`.

We can now proceed to the evaluation of our newly trained model :
```sh
python evaluate.py --model_str="1hidden-1500"
```
This script evaluates the model on the test dataset. The results are stored in `ml_core/results.csv` under the string passed as argument.

It is also possible to run inference on an image with :
```sh
python inference.py --image="../docs/lake.jpg"
```
Below is an example of prediction
<div style="text-align:center">
<img src="https://raw.githubusercontent.com/Nlte/social-image-platform/master/docs/example_inference.png" width="300" height="300"/>
</div>

### References

- Ali Sharif Razavian, Hossein Azizpour, Josephine Sullivan and Stefan Carlsson. CNN Features off-the-shelf: an Astounding Baseline for Recognition. KTH, 2014. [[link]](https://arxiv.org/abs/1403.6382)
- Min-Ling Zhang and Zhi-Hua Zhou. A Review on Multi-Label Learning Algorithms. IEEE Transactions on Knowledge and Data Engineering, 2014. [[link]](http://cse.seu.edu.cn/people/zhangml/files/TKDE'13.pdf)
- Maxime Oquab, Leon Bottou, Ivan Laptev and Josef Sivic. Learning and Transferring Mid-Level Image Representations using Convolutional Neural Networks. In CVPR, 2014. [[link]](http://www.di.ens.fr/willow/pdfscurrent/oquab14cvpr.pdf)
- Oriol Vinyals, Alexander Toshev, Samy Bengio and Dumitru Erhan. Show and Tell: A Neural Image Caption Generator. In CVPR, 2014. [[link]](https://arxiv.org/abs/1411.4555)
- Mohammad S Sorower. A Literature Survey on Algorithms for Multi-label Learning. Oregon State University, 2010. [[link]](http://people.oregonstate.edu/~sorowerm/pdf/Qual-Multilabel-Shahed-CompleteVersion.pdf)
- Mark J. Huiskes and Michael S. Lew. The MIR Flickr Retrieval Evaluation. ACM International Conference on Multimedia Information Retrieval, 2008. [[link]](http://press.liacs.nl/mirflickr/mirflickr.pdf)
- Antonio Torralba and Alexei A. Efros. Unbiased Look at Dataset Bias. In CVPR, 2011. [[link]](https://people.csail.mit.edu/torralba/publications/datasets_cvpr11.pdf)
- Matthieu Guillaumin, Thomas Mensink, Jakob Verbeek and Cordelia Schmid. TagProp: Discriminative Metric Learning in Nearest Neighbor Models for Image Auto-Annotation. In ICCV, 2009. [[link]](http://class.inrialpes.fr/pub/guillaumin-iccv09b.pdf)
- Minmin Chen, Alice Zheng and Kilian Q. Weinberger. Fast Image Tagging. In JMLR, 2013. [[link]](http://www.jmlr.org/proceedings/papers/v28/chen13j.pdf)
- Mark Everingham, Luc Van Gool, Christopher K. I. Williams, John Winn and Andrew Zisserman. The PASCAL Visual Object Classes (VOC) Challenge. In IJCV, 2010 [[link]](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.167.6629&rep=rep1&type=pdf)
- Nitish Srivastava, Geoffrey Hinton, Alex Krizhevsky, Ilya Sutskever and Ruslan Salakhutdinov. Dropout: A Simple Way to Prevent Neural Networks from Overfitting. In JMLR, 2014. [[link]](https://www.cs.toronto.edu/~hinton/absps/JMLRdropout.pdf)
- Diederik P. Kingma and Jimmy Lei Ba. Adam: a method for stochastic optimization. In ICLR, 2015. [[link]](https://arxiv.org/pdf/1412.6980v8.pdf)
- Fei-Fei Li, Andrej Karpathy, Justin Johnson. Stanford Course CS231n: Convolutional Neural Networks for Visual Recognition.  [[Website]](http://cs231n.stanford.edu)
- Sebastian Ruder. An overview of gradient descent optimization algorithms. [[Website]](http://sebastianruder.com/optimizing)
- Chris Shallue. Show and Tell: A Neural Image Caption Generator. [[GitHub]](https://github.com/cshallue/models/tree/master/im2txt)



## Running the website

<img src="https://raw.githubusercontent.com/Nlte/social-image-platform/master/docs/frontpage.png" />

The website was built using Flask.

It is preferable to create a virtual environment before proceeding to the installation of the website.
```sh
# at the root of the repository
virtualenv -p python3 env
source env/bin/activate
```
To install the requirements
```sh
pip install -r requirements.txt
```
We can then start the two servers:
- `predserver.py` located in ml_core, responsible for the tag prediction
- `webserver.py` located in flask_platform, that runs the website
```sh
# in one terminal run the prediction server
cd ml_core/
python predserver.py # the initialization can take a few seconds
# in another terminal run the webserver
cd flask_platform/
python webserver.py
```

After the initialization of the tensorflow model and the flask server are done. We can navigate to `127.0.0.1:5000` and play with the website.
