from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tensorflow as tf

import inputs
import cnn
import image_processing

tf.logging.set_verbosity(tf.logging.INFO)


class CNNSigmoid(object):

    def __init__(self, mode, config, images=None, annotations=None):

        # config
        self.mode = mode
        self.config = config
        # inputs
        self.images = images
        self.annotations = annotations
        # vocabulary
        self.vocabulary = self.config.vocabulary
        # inception
        self.bottleneck_tensor = None
        # sigmoid
        self.loss = None
        self.logits = None
        self.prediction = None
        self.optimize = None
        # evaluation
        self.metrics_op = None
        self.metrics_value = None


    def build_inputs():
        image_feed = tf.placeholder(tf.string, shape=[])
        annotation_feed = tf.placeholder(tf.int64, shape=[None])
        images = tf.expand_dims(self.process_image(image_feed), 0)
        input_seqs = tf.expand_dims(input_feed, 0)
        self.images = images
        self.input_seqs = input_seqs


    def build_inception(self):
        cnn.maybe_download_and_extract(self.config.inception_dir)
        inception_output = cnn.inception_v3(self.images, trainable=False)
        self.inception_variables = tf.get_collection(
            tf.GraphKeys.VARIABLES, scope="InceptionV3")
        self.bottleneck_tensor = inception_output


    def build_sigmoid(self):
        output_dim = self.config.num_classes
        bottleneck_dim = self.config.bottleneck_dim
        with tf.name_scope('sigmoid_layer'):
            W = tf.Variable(
                tf.random_normal([bottleneck_dim, output_dim],
                stddev=0.35),
                name='sigmoid_weights'
                )
            b = tf.Variable(tf.zeros([output_dim]), name='sigmoid_biases')
            # logits
            logits = tf.matmul(self.bottleneck_tensor, W) + b
            # compute the activations
            sigmoid_tensor = tf.nn.sigmoid(logits, name='sigmoid_tensor')
            # label is true if sigmoid activation > 0.5
            prediction = tf.round(sigmoid_tensor, name='prediction_tensor')
            cross_entropy = tf.reduce_mean(
                tf.nn.sigmoid_cross_entropy_with_logits(logits, self.annotations)
            )
            tf.scalar_summary('cross_entropy', cross_entropy)
            train_step = tf.train.AdamOptimizer(self.config.learning_rate).minimize(cross_entropy)
        self.loss = cross_entropy
        self.prediction = prediction
        self.optimize = train_step


    def build_evaluation(self):
        with tf.name_scope('metrics'):
            recall, recall_op = tf.contrib.metrics.streaming_recall(
                                self.prediction, self.annotations, name='recall')
            accuracy, accuracy_op = tf.contrib.metrics.streaming_accuracy(
                                self.prediction, self.annotations, name='accuracy')
            precision, precision_op = tf.contrib.metrics.streaming_precision(
                                self.prediction, self.annotations, name='precision')
            tf.scalar_summary('recall', recall)
            tf.scalar_summary('accuracy', accuracy)
            tf.scalar_summary('precision', precision)
        self.metrics_op = [recall_op, accuracy_op, precision_op]
        self.metrics_value = [recall, accuracy, precision]


    def init_fn(self, sess):
        saver = tf.train.Saver(self.inception_variables)
        tf.logging.info("Restoring Inception variables from checkpoint file %s",
            self.config.inception_checkpoint)
        saver.restore(sess, self.config.inception_checkpoint)


    def setup_global_step(self):
        global_step = tf.Variable(0, name='global_step', trainable=False)
        self.global_step = global_step


    def build(self):
        """Build the layers of the model."""

        if self.mode == "inference":
            self.build_inputs()

        self.build_inception()
        self.build_sigmoid()
        self.build_evaluation()
        self.setup_global_step()
        tf.logging.info("Model sucessfully built.")


    def restore(self, sess):
        """Restore variables from the checkpoint file in configuration.py"""

        saver = tf.train.Saver()
        tf.logging.info("Restoring model variables from checkpoint file %s",
            self.config.model_checkpoint)
        saver.restore(sess, self.config.model_checkpoint)
        tf.logging.info("Model restored.")
