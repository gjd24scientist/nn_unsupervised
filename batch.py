from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import glob

def _files_and_labels(glob_str):
  files = glob.glob(glob_str)
  length = int(len(files) / 4)
  files.sort()
  cc_left = files[::4]
  cc_right = files[2::4]
  mlo_left = files[1::4]
  mlo_right = files[3::4]
  left_image = cc_left + mlo_left
  right_image = cc_right + mlo_right
  label = map(lambda x: 2 if 'benign' in x else 1 if 'cancer' in x else 0, left_image)
  return left_image, right_image, list(label)

def _process_image_string(istr):
  value = tf.read_file(istr)
  img = tf.image.decode_png(value)
  w_img = tf.image.per_image_whitening(img)
  w_img.set_shape((512, 256, 1))
  return w_img

def _get_data(glob_str):
  l_image_list, r_image_list, label_list = _files_and_labels(glob_str)
  l_images = tf.convert_to_tensor(l_image_list, dtype=tf.string)
  r_images = tf.convert_to_tensor(r_image_list, dtype=tf.string)
  labels = tf.convert_to_tensor(label_list, dtype=tf.int32)

  input_queue = tf.train.slice_input_producer([l_images, r_images, labels])

  l_img = _process_image_string(input_queue[0])
  r_img = _process_image_string(input_queue[1])
  return l_img, r_img, input_queue[2]

def get_batch(glob_str, batch_size):
  l_image, r_image, label = _get_data(glob_str)
  min_after_dequeue = 1000
  capacity = min_after_dequeue + 3 * batch_size
  l_image_batch, r_image_batch, label_batch = tf.train.shuffle_batch(
      [l_image, r_image, label], batch_size=batch_size, capacity=capacity,
       min_after_dequeue=min_after_dequeue)
  return l_image_batch, r_image_batch, label_batch


