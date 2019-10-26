import os
import json

class Metadata:

	METADATA_FILE_NAME = 'metadata.json'

	def __init__(self):
		self.metadata = {}
		if (os.path.isfile(self.METADATA_FILE_NAME)):
			self.metadata = json.load(open(self.METADATA_FILE_NAME))

	def put(self, challenge_id, submission_id):
		self.metadata[str(challenge_id)] = str(submission_id)
		json.dump(self.metadata, open(self.METADATA_FILE_NAME, 'w'))

	def get(self, challenge_id):
		challenge_id_string = str(challenge_id)
		if challenge_id_string not in self.metadata:
			self.metadata[challenge_id_string] = -1
		submission_id_string = self.metadata[challenge_id_string]
		return int(submission_id_string)
