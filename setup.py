#!/usr/bin/env python

from setuptools import setup

setup(
      name='RefWeb',
      version='1.0',
      description='Refweb',
      author=['Rickert Mulder'],
      author_email=['circlingthesun@gmail.com'],
      url='http://www.circlngthesun.co.za',
      packages=['refweb'],
      install_requires=[
        'pdfminer'
	#'pySide',
        #'python-dateutil',
        #'flask',
        #'python-ntlm',
      ],
)
