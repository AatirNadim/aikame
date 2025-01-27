import os

'''
	Constants for the project.
	They can be set as environment variables.
'''

parent_path = os.environ.get("parent_path", "./data")

chunk_size = os.environ.get("chunk_size", 256)