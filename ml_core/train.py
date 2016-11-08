import tensorflow as tf

import inputs
import os
from datetime import datetime
from configuration import ModelConfig
from CNNS import CNNSigmoid


FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('log_dir', 'models/model', """logging directory""")

tf.app.flags.DEFINE_integer('num_steps', 10, """Number of batches to run.""")

tf.app.flags.DEFINE_string('train_file_pattern', 'train-???-008.tfr',
                            """file pattern of training tfrecords.""")

tf.app.flags.DEFINE_string('val_file_pattern', 'val-???-001.tfr',
                            """file pattern of training tfrecords.""")


def main(_):

    if not tf.gfile.IsDirectory(FLAGS.log_dir):
        tf.logging.info("Creating output directory: %s" % FLAGS.log_dir)
        tf.gfile.MakeDirs(FLAGS.log_dir)

    config = ModelConfig()

    train_images, train_annotations = inputs.input_pipeline(FLAGS.train_file_pattern,
                                    num_classes=config.num_classes, batch_size=32)

    val_images, val_annotations = inputs.input_pipeline(FLAGS.val_file_pattern,
                                    num_classes=config.num_classes, batch_size=8)

    data = tf.placeholder(tf.float32, [None, 299, 299, 3])
    target = tf.placeholder(tf.float32, [None, config.num_classes])

    model = CNNSigmoid("train", config, data, target)
    model.build()

    merged = tf.merge_all_summaries()
    saver = tf.train.Saver()

    sess = tf.Session()

    sess.run(tf.initialize_all_variables())
    sess.run(tf.initialize_local_variables())
    model.init_fn(sess)

    train_writer = tf.train.SummaryWriter(FLAGS.log_dir + '/train', sess.graph)
    test_writer = tf.train.SummaryWriter(FLAGS.log_dir + '/test')

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    print("%s Start training." % datetime.now())
    for n in xrange(FLAGS.num_steps):

        images, annotations = sess.run([train_images, train_annotations])
        _, loss, summary = sess.run([model.optimize, model.loss, merged],
                                    {data:images, target: annotations})
        train_writer.add_summary(summary, n)
        print("%s - Loss : %f" % (datetime.now(), loss))

        if n%10 == 0:
            images, annotations = sess.run([val_images, val_annotations])
            sess.run(model.metrics_op, {data: images, target: annotations})
            recall, accuracy, precision = sess.run(model.metrics_value)
            print("%s - Recall : %f Accuracy : %f Precision: %f" %
                    (datetime.now(), recall, accuracy, precision))
            summary = sess.run(merged, {data: images, target: annotations})
            test_writer.add_summary(summary, n)

    save_path = saver.save(sess, os.path.join(FLAGS.log_dir, 'model.ckpt'))
    print("Model saved in file: %s" % save_path)

    coord.request_stop()
    coord.join(threads)
    sess.close()

if __name__ == '__main__':
    tf.app.run()