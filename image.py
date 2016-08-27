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
		self.labels = []
		self.access_token = "pk.eyJ1IjoiZ2FuZXNocmF2aWNoYW5kcmFuIiwiYSI6ImNpczUxMTBqNTBhNDUyb2xrcGwzdGQ5YzcifQ.QoSUWMk-EZJoPTn-K8OreA"

		if use_local_images:
			self.geo_data = self.load_obj("image_metadata")
			print type(self.geo_data)

			for key in self.geo_data:
				source = self.geo_data[key]
				img_path = os.path.join(self.img_directory, source["name"] + ".png")
				self.load_tensor(img_path)
		else:

			if not os.path.exists(self.img_directory):
			    os.makedirs(self.img_directory)

			self.get_water_sources()

			for key in self.geo_data:
				source = self.geo_data[key]
				self.make_tensor(source)

		self.classify()

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

		print img_path
		tensor = tf.image.decode_png(img_path)
		print tensor
		tensor2 = tf.image.decode_png("/Users/ganeshravichandran/Dropbox/Code/thirsty/images/HUDSON_RIVER_AT_SOUTH_DOCK_AT_WEST_POINT_NY.png")
		print tensor2
		self.map_tensors.append(tensor)
		self.labels.append([1]);

	def get_water_sources(self, stateCd="NY"):
		url = "http://waterservices.usgs.gov/nwis/iv/?format=json&stateCd=%s" %(stateCd)
		res = urllib2.urlopen(url)

		# list of water sources
		data = json.loads(res.read())["value"]["timeSeries"]

		for source in data:
			sourceInfo = source["sourceInfo"]
			siteCode = sourceInfo["siteCode"][0]["value"]
			sourceGeoInfo = sourceInfo["geoLocation"]["geogLocation"]

			self.geo_data[siteCode] = {
				"name": sourceInfo["siteName"].replace (" ", "_"),
				"lat": sourceGeoInfo["latitude"],
				"lon": sourceGeoInfo["longitude"]
			}

		self.save_obj(self.geo_data, "image_metadata")

	def classify(self):

		print "Starting classify()..."

		x = tf.placeholder(tf.float32, [None, 1000000])
		W = tf.Variable(tf.zeros([1000000, 2]))
		b = tf.Variable(tf.zeros([2]))
		y = tf.nn.softmax(tf.matmul(x, W) + b)

		y_ = tf.placeholder(tf.float32, [None, 2])
		cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
		train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
		init = tf.initialize_all_variables()
		sess = tf.Session()
		sess.run(init)

		training_set = self.map_tensors[:len(self.map_tensors)/2]
		training_labels = self.labels[:len(self.labels)/2]

		print training_set

		test_set = self.map_tensors[len(self.map_tensors)/2:]
		test_labels = self.labels[len(self.labels)/2:]

		sess.run(train_step, feed_dict={x: training_set, y_: training_labels})

		correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
		accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
		print(sess.run(accuracy, feed_dict={x: test_set, y_: test_labels}))

