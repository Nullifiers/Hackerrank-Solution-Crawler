import os
import json
import requests
import getpass
import configargparse
from progress.bar import ChargingBar


class CustomProgress(ChargingBar):
	message = 'Downloading Solutions'
	suffix = '%(percent)d%% [%(index)d/%(max)d]'


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


class Crawler:
	base_url = 'https://www.hackerrank.com/'
	login_url = base_url + 'auth/login'
	submissions_url = base_url + 'rest/contests/master/submissions/?offset={}&limit={}'
	challenge_url = base_url + 'rest/contests/master/challenges/{}/submissions/{}'
	domain_url = base_url + 'domains/{}/{}'
	problem_url = base_url + 'challenges/{}/problem'

	new_readme_text = '## [{}]({})\n\n|Problem Name|Problem Link|Language|Solution Link|\n---|---|---|---\n'
	readme_headers_len = len(new_readme_text.split('\n')) - 1
	problem_readme_text = '|{}|[Problem]({})|{}|[Solution](./{})|\n'

	base_folder_name = 'Hackerrank'

	# make a separate folder for different languages e.g Hackerrank/Regex/Introduction/python3/matching.py
	make_language_folder = False
	# prepend language in file extension e.g Hackerrank/Regex/Introduction/matching.python3.py
	prepend_language_in_extension = False

	# file extensions
	file_extensions = {
		'ada': 'ada',
		'bash': 'sh',
		'c': 'c',
		'clojure': 'clj',
		'coffeescript': 'coffee',
		'cpp': 'cpp',
		'cpp14': 'cpp',
		'csharp': 'cs',
		'd': 'd',
		'db2': 'sql',
		'elixir': 'ex',
		'erlang': 'erl',
		'fortran': 'for',
		'fsharp': 'fs',
		'go': 'go',
		'groovy': 'groovy',
		'haskell': 'hs',
		'java': 'java',
		'java8': 'java',
		'javascript': 'js',
		'julia': 'jl',
		'kotlin': 'kt',
		'lolcode': 'lol',
		'lua': 'lua',
		'mysql': 'sql',
		'objectivec': 'm',
		'ocaml': 'ml',
		'octave': 'oct',
		'oracle': 'sql',
		'pascal': 'pas',
		'perl': 'pl',
		'php': 'php',
		'pypy': 'py',
		'pypy3': 'py',
		'python': 'py',
		'python3': 'py',
		'racket': 'rkt',
		'r': 'r',
		'ruby': 'rb',
		'rust': 'rs',
		'sbcl': 'lisp',
		'scala': 'scala',
		'swift': 'swift',
		'smalltalk': 'st',
		'tcl': 'tcl',
		'tsql': 'sql',
		'visualbasic': 'vbs',
		'whitespace': 'hs',
	}

	def __init__(self):
		self.session = requests.Session()
		self.total_submissions = 0
		self.options = {}

	def login(self, username, password):
		resp = self.session.get(self.login_url, auth=(username, password))
		self.cookies = self.session.cookies.get_dict()
		self.headers = resp.request.headers
		self.get_number_of_submissions()
		return self.total_submissions != 0

	def parse_script(self):
		p = configargparse.ArgParser(default_config_files=['./user.yaml'])
		p.add('-c', '--config', is_config_file=True, help='config file path')
		p.add('-l', '--limit', help='limit to no. of solutions to be crawled')
		p.add('-o', '--offset', help='crawl solutions starting from this number')
		p.add('-u', '--username', help='hackerrank account username')
		p.add('-p', '--password', help='hackerrank account password')

		self.options = p.parse_args()

	def authenticate(self):
		username = self.options.username or input('Hackerrank Username: ')
		password = self.options.password or getpass.getpass('Hackerrank Password: ')
		return self.login(username, password)

	def get_number_of_submissions(self):
		if not self.total_submissions:
			all_submissions_url = self.get_all_submissions_url(0, 0)
			resp = self.session.get(all_submissions_url, headers=self.headers)
			self.total_submissions = resp.json()['total']
		return self.total_submissions

	def get_all_submissions_url(self, offset, limit):
		return self.submissions_url.format(offset, limit)

	def get_submission_url(self, challenge_slug, submission_id):
		return self.challenge_url.format(challenge_slug, submission_id)

	def store_submission(self, file_name, code):
		if not os.path.exists(file_name):
			os.makedirs(os.path.dirname(file_name), exist_ok=True)
		with open(file_name, 'w') as text_file:
			text_file.write(code)

	def update_readme(self, readme_file_path, problem_readme_text):
		header_length = self.readme_headers_len
		with open(readme_file_path, 'r+') as text_file:
			lines = text_file.readlines()
			lines.append(problem_readme_text)
			sortedlines = lines[:header_length] + sorted(lines[header_length:])
			text_file.seek(0)
			text_file.writelines(sortedlines)

	def create_readme(self, track_name, track_url, file_name):
		if track_name is not None:
			os.makedirs(os.path.dirname(file_name), exist_ok=True)
			text = self.new_readme_text.format(track_name, track_url)
			with open(file_name, 'w') as text_file:
				text_file.write(text)

	def get_file_path(self, folder_name, file_name_with_extension):
		return os.path.join(self.base_folder_name, folder_name, file_name_with_extension)

	def get_readme_path(self, folder_name):
		return os.path.join(self.base_folder_name, folder_name, 'README.md')

	def get_submissions(self, submissions):
		headers = self.headers

		progress = CustomProgress('Downloading Solutions', max=len(submissions))
		metadata = Metadata()

		for submission in submissions:
			submission_id = submission['id']
			challenge_id = submission['challenge_id']
			status = submission['status']
			language = submission['language']
			status_code = submission['status_code']
			challenge = submission['challenge']
			challenge_name = challenge['name']
			challenge_slug = challenge['slug']

			if submission_id > metadata.get(challenge_id) and (status == 'Accepted' or status_code == 2):
				metadata.put(challenge_id, submission_id)

				submission_url = self.get_submission_url(challenge_slug, submission_id)
				resp = self.session.get(submission_url, headers=headers)
				data = resp.json()['model']
				code = data['code']
				track = data['track']

				folder_name = 'Others'
				file_extension = '.' + language
				file_name = challenge_slug
				track_folder_name = 'Others'
				track_url = ''

				if track:
					track_folder_name = track['name'].strip().replace(' ', '')
					track_url = self.domain_url.format(track['track_slug'], track['slug'])
					parent_folder_name = track['track_name'].strip().replace(' ', '')
					folder_name = os.path.join(parent_folder_name, track_folder_name)

				if self.make_language_folder:
					folder_name = os.path.join(folder_name, language)

				if language in self.file_extensions:
					if not self.prepend_language_in_extension:
						file_extension = ''
					file_extension += '.{}'.format(self.file_extensions[language])

				if file_extension.endswith('.java'):
					file_name = challenge_name.replace(' ','')

				file_path = self.get_file_path(folder_name, file_name + file_extension)
				self.store_submission(file_path, code)
				readme_file_path = self.get_readme_path(folder_name)
				if not os.path.exists(readme_file_path):
					self.create_readme(track_folder_name, track_url, readme_file_path)
				problem_url = self.problem_url.format(challenge_slug)
				readme_text = self.problem_readme_text.format(challenge_name, problem_url, language, file_name + file_extension)
				self.update_readme(
					readme_file_path,
					readme_text,
				)
			progress.next()
		progress.finish()
		print('All Solutions Crawled')

def main():

	crawler = Crawler()
	crawler.parse_script()
	if not crawler.authenticate():
		print('Auth was unsuccessful. Exiting the program')
		exit(1)

	limit = crawler.options.limit or crawler.total_submissions
	offset = crawler.options.offset or 0
	print('Start crawling {} solutions starting from {}'.format(limit, offset))
	all_submissions_url = crawler.get_all_submissions_url(offset, limit)

	resp = crawler.session.get(all_submissions_url, headers=crawler.headers)
	data = resp.json()
	models = data['models']
	crawler.get_submissions(models)

if __name__ == "__main__":
	main()
