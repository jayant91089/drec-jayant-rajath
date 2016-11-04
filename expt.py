#!/usr/bin/env python
"""
Some of the following code can be found at:
https://www.kaggle.com/martinthoma/digit-recognizer/minst-tensorflow-py
"""

import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing
from datetime import datetime as dt
import logging
logging.getLogger("tf").setLevel(logging.WARNING)


# Handle Kaggle input data
def dense_to_one_hot(labels_dense, num_classes=10):
    """Convert class labels from scalars to one-hot vectors."""
    num_labels = labels_dense.shape[0]
    index_offset = np.arange(num_labels) * num_classes
    labels_one_hot = np.zeros((num_labels, num_classes))
    labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
    return labels_one_hot


class MnistDataSets(object):
    """
    Convenience class for Training-, Validation- and Testset.

    Parameters
    ----------
    train_path : str
        Path to the train.csv
    test_path : str
        Path to the test.csv
    """
    def __init__(self, train_path, test_path):
        train_df = pd.read_csv(train_path)
        y_train = train_df[['label']]
        x_train = train_df.ix[:, 1:]
        x_train, x_val, y_train, y_val = train_test_split(x_train,
                                                          y_train,
                                                          test_size=0.10,
                                                          random_state=42)
        lb = preprocessing.LabelBinarizer()
        lb.fit([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

        self.train = DataSet(x_train, lb.transform(y_train))
        self.validation = DataSet(x_val, lb.transform(y_val))

        test_images = pd.read_csv(test_path)
        self.test = DataSet(test_images)


class DataSet(object):
    def __init__(self, images, labels=None, fake_data=False):
        if fake_data:
            self._num_examples = 10000
        else:
            if labels is not None:
                assert images.shape[0] == labels.shape[0], (
                    "images.shape: %s labels.shape: %s" % (images.shape,
                                                           labels.shape))
        self._num_examples = images.shape[0]
        images = images.astype(np.float32)
        images = np.multiply(images, 1.0 / 255.0)
        self._images = images
        self._labels = labels
        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def images(self):
        return self._images

    @property
    def labels(self):
        return self._labels

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size):
        """Return the next `batch_size` examples from this data set."""
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._images = self._images[perm]
            self._labels = self._labels[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._images[start:end], self._labels[start:end]
