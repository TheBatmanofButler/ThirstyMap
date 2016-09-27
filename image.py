import os
import urllib2
import json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from PIL import Image
from StringIO import StringIO
import requests

class WaterSourceClassifier:

	def __init__(self, img_directory="images", use_local_images = False):
		
		self.img_directory = img_directory
		self.geo_data = {}
		self.map_tensors = []
		self.filepaths = []
		self.images = []
		self.labels = []


		self.access_token = "pk.eyJ1IjoiZ2FuZXNocmF2aWNoYW5kcmFuIiwiYSI6ImNpczUxMTBqNTBhNDUyb2xrcGwzdGQ5YzcifQ.QoSUWMk-EZJoPTn-K8OreA"

		if use_local_images:
			self.geo_data = self.load_obj("image_metadata")

			for key in self.geo_data:
				source = self.geo_data[key]
				self.labels.append(source["label"])

				img_path = os.path.join(self.img_directory, source["name"] + ".png")
				self.filepaths.append(img_path)

				self.image_obj = Image.open(img_path) #Can be many different formats.
				self.image_list = np.array(self.image_obj).tolist()
				self.images.append(self.image_list)

		else:

			if not os.path.exists(self.img_directory):
			    os.makedirs(self.img_directory)

			self.get_water_sources()

			for key in self.geo_data:
				source = self.geo_data[key]
				self.make_tensor(source)

		self.classify()

	def read_images_from_disk(self, input_queue):
		"""Consumes a single filename and label as a ' '-delimited string.
		Args:
		  filename_and_label_tensor: A scalar string tensor.
		Returns:
		  Two tensors: the decoded image, and the string label.
		"""
		label = input_queue[1]
		file_contents = tf.read_file(input_queue[0])
		print dir(file_contents), "123"
		example = tf.image.decode_png(file_contents, channels=3)
		return example, label

	def save_obj(self, obj, name):
		np.save(os.path.join(self.img_directory, name + ".npy"), obj)

	def load_obj(self, name):
		return np.load(os.path.join(self.img_directory, name + ".npy")).item();

	def make_tensor(self, source, zoom=17):
		url = "https://api.mapbox.com/v4/mapbox.satellite/%s,%s,%s/1000x1000.png32?access_token=%s" % (source["lon"], source["lat"], zoom, self.access_token)
		
		res = urllib2.urlopen(url)
		stream = res.read()
		
		img_path = os.path.join(self.img_directory, source["name"] + ".png")

		img_file = open(img_path,'w')
		img_file.write(stream)
		img_file.close()

		self.load_tensor(img_path)

	def load_tensor(self, img_path):

		tensor = tf.image.decode_png(img_path)
		self.map_tensors.append(tensor)
		self.labels.append([1]);

	def get_water_sources(self, stateCd="NY"):
		url = "http://waterservices.usgs.gov/nwis/iv/?format=json&stateCd=%s" %(stateCd)
		res = urllib2.urlopen(url)

		# list of water sources
		data = json.loads(res.read())["value"]["timeSeries"]

		stopper = 0

		for source in data:
			if stopper < 100:
				sourceInfo = source["sourceInfo"]
				siteCode = sourceInfo["siteCode"][0]["value"]
				sourceGeoInfo = sourceInfo["geoLocation"]["geogLocation"]

				self.geo_data[siteCode] = {
					"name": sourceInfo["siteName"].replace (" ", "_"),
					"lat": sourceGeoInfo["latitude"],
					"lon": sourceGeoInfo["longitude"],
					"label": 1
				}

				self.make_tensor(self.geo_data[siteCode])

				stopper += 1

		self.save_obj(self.geo_data, "image_metadata")

	def classify(self):

		print "Starting classify()..."

		x = tf.placeholder(tf.float32)
		W = tf.Variable(tf.zeros([1000, 1000]))
		b = tf.Variable(tf.zeros([1]))
		y = tf.nn.softmax(tf.matmul(x, W) + b)

		y_ = tf.placeholder(tf.float32)
		cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
		train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
		init = tf.initialize_all_variables()
		sess = tf.Session()
		sess.run(init)

		# training_labels = [1] * len(self.images[0])

		new_list = []

		for row in self.images[0]:
			new_list.extend(row)

		print new_list

		# training_set = self.image[:len(self.tf_images)/2]
		# training_labels = self.tf_labels[:len(self.tf_labels)/2]

		# self.wtf = training_set[0]

		# test_set = self.tf_images[len(self.tf_images)/2:]
		# test_labels = self.tf_labels[len(self.tf_labels)/2:]

		# sess.run(train_step, feed_dict={x: np.array(self.images[0]), y_: training_labels[0]})
		# print y._shape, y_._shape, 
		# correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
		# accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
		# print(sess.run(accuracy, feed_dict={x: np.array(self.images[1]), y_: training_labels[1]}))

