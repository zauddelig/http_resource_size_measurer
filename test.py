#!/usr/bin/env python3
import unittest
import multiprocessing
from measurer import LinksGetter, Resource
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server


class TestLinksGetter(unittest.TestCase):
	main_url = "http://father.test/"

	def get_feed(self, html, url=None):
		if not url:
			url = self.main_url
		parser = LinksGetter(url)
		parser.feed(html)
		return parser

	def test_iframe(self):
		html = "<hmtl><iframe src='http://example.com'></iframe></html>"
		parser = self.get_feed(html)
		self.assertEqual(parser.links, ["http://example.com"])

	def test_css_link(self):
		html = "<hmtl><link rel='stylesheet' href='http://example.com/test.css'></iframe></html>"
		parser = self.get_feed(html, self.main_url+"test/")
		self.assertEqual(parser.links, ["http://example.com/test.css"])

	def test_ignore_most_links(self):
		html = "<hmtl><link href='http://example.com/test.css'></iframe></html>"
		parser = self.get_feed(html, self.main_url+"test/")
		self.assertEqual(parser.links, [])

	def test_image(self):
		html = "<hmtl><img src='http://example.com/test.png'></script></html>"
		parser = self.get_feed(html, self.main_url+"test/")
		self.assertEqual(parser.links, ["http://example.com/test.png"])

	def test_script(self):
		html = "<hmtl><script src='http://example.com/test.js'></script></html>"
		parser = self.get_feed(html, self.main_url+"test/")
		self.assertEqual(parser.links, ["http://example.com/test.js"])

	def test_relative_link(self):
		html = "<hmtl><link rel='stylesheet' href='/test.css'></link></html>"
		parser = self.get_feed(html, self.main_url+"test/")
		self.assertEqual(parser.links, [self.main_url+"test.css"])

	def test_absolute_link(self):
		html = "<hmtl><link rel='stylesheet' href='/test.css'></link></html>"
		parser = self.get_feed(html, self.main_url+"test/")
		self.assertEqual(parser.links, [self.main_url+"test.css"])

	def test_net_link(self):
		html = "<hmtl><link rel='stylesheet' href='//example.com/test.css'></link></html>"
		parser = self.get_feed(html, "https://father.test/test/")
		self.assertEqual(parser.links, ["https://example.com/test.css"])

	def test_dotted_relative_link(self):
		html = "<hmtl><link rel='stylesheet' href='../example/test.css'></link></html>"
		parser = self.get_feed(html, "https://father.test/test/")

	def test_dotted_absolute_link(self):
		html = "<hmtl><link rel='stylesheet' href='/example/../test.css'></link></html>"
		parser = self.get_feed(html, "https://father.test/test/")
		self.assertEqual(parser.links, ["https://father.test/test.css"])

class TestResource(unittest.TestCase):
	"""
		We it test using unlikely to change resources
	"""

	def test_simple(self):
		"""
		Note we assume that this page size is very unlikelly to change
		:return:
		"""
		resource = Resource("http://example.com/")
		self.assertEqual(resource.size, 1270)

	def test_non_html(self):
		resource = Resource("http://www.ietf.org/rfc/rfc1808.txt")
		# had to give a rather big delta here, I was not able to assess the precise size of the page
		self.assertAlmostEqual(resource.size, 34130, delta=1000)
		resource = Resource("http://www.governo.it/Governo/Costituzione/CostituzioneRepubblicaItaliana.pdf")
		self.assertAlmostEqual(resource.size, 188249)





if __name__=="__main__":
	unittest.main()
