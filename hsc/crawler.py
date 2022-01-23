import os
import requests
import getpass
import configargparse
from .progress_bar import CustomProgress
from .metadata import Metadata
from .constants import extensions


class Crawler:
	base_url = 'https://www.hackerrank.com/'
	user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.63'
	login_url = base_url + 'rest/auth/login'
	submissions_url = base_url + 'rest/contests/master/submissions/?offset={}&limit={}'
	challenge_url = base_url + 'rest/contests/master/challenges/{}/submissions/{}'
	domain_url = base_url + 'domains/{}'
	subdomain_url = base_url + 'domains/{}/{}'
	problem_url = base_url + 'challenges/{}/problem'

	subdomain_readme_text = '## [{}]({})\n\n|Problem Name|Problem Link|Language|Solution Link|\n---|---|---|---\n'
	domain_readme_text = '## [{}]({})\n\n|Subdomain|Problem Name|Problem Link|Language|Solution Link|\n---|---|---|---|---\n'
	root_readme_text = '## [Hackerrank]({})\n\n|Domain|Subdomain|Problem Name|Problem Link|Language|Solution Link|\n---|---|---|---|---|---\n'
	readme_headers_len = len(subdomain_readme_text.split('\n')) - 1

	subdomain_readme_row = '|{}|[Problem]({})|{}|[Solution]({})|\n'
	domain_readme_row = '|{}|{}|[Problem]({})|{}|[Solution]({})|\n'
	root_readme_row = '|{}|{}|{}|[Problem]({})|{}|[Solution]({})|\n'

	base_folder_name = 'Hackerrank'

	# make a separate folder for different languages e.g Hackerrank/Regex/Introduction/python3/matching.py
	make_language_folder = False
	# prepend language in file extension e.g Hackerrank/Regex/Introduction/matching.python3.py
	prepend_language_in_extension = False

	file_extensions = extensions

	def __init__(self):
		self.session = requests.Session()
		self.total_submissions = 0
		self.options = {}

	def login(self, username, password):
		resp = self.session.post(self.login_url, auth=(username, password), headers={'user-agent': self.user_agent})
		data = resp.json()
		if data['status']:
			self.cookies = self.session.cookies.get_dict()
			self.headers = resp.request.headers
			self.get_number_of_submissions()
		return data['status']

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

	def update_readme(self, readme_file_path, readme_text):
		header_length = self.readme_headers_len
		with open(readme_file_path, 'r+') as text_file:
			lines = text_file.readlines()
			lines.append(readme_text)
			sortedlines = lines[:header_length] + sorted(lines[header_length:])
			text_file.seek(0)
			text_file.writelines(sortedlines)

	def write(self, file_name, text):
		os.makedirs(os.path.dirname(file_name), exist_ok=True)
		with open(file_name, 'w') as text_file:
			text_file.write(text)


	def create_readmes(self, domain_name, subdomain_name, domain_url, subdomain_url,
				subdomain_readme_path, domain_readme_path, root_readme_path):
		"""
		Method to check if readme files already exist. If readme files doesn't exist, then create them and add headers.
		"""
		if not os.path.exists(subdomain_readme_path):
			text = self.subdomain_readme_text.format(subdomain_name, subdomain_url)
			self.write(subdomain_readme_path, text)

		if not os.path.exists(domain_readme_path):
			text = self.domain_readme_text.format(domain_name, domain_url)
			self.write(domain_readme_path, text)

		if not os.path.exists(root_readme_path):
			text = self.root_readme_text.format(self.base_url)
			self.write(root_readme_path, text)


	def update_readmes(self, domain_name, subdomain_name, domain_url, subdomain_url,
				challenge_name, challenge_slug, language, file_name_with_extension):
		"""
		Method to add a new row corresponding to a new solution in the readme files
		"""
		subdomain_readme_path = os.path.join(self.base_folder_name, domain_name, subdomain_name, 'README.md')
		if self.make_language_folder:
			subdomain_readme_path = os.path.join(self.base_folder_name, domain_name, subdomain_name, language, 'README.md')
		domain_readme_path = os.path.join(self.base_folder_name, domain_name, 'README.md')
		root_readme_path = os.path.join(self.base_folder_name, 'README.md')

		self.create_readmes(domain_name, subdomain_name, domain_url, subdomain_url,
				subdomain_readme_path, domain_readme_path, root_readme_path)

		problem_url = self.problem_url.format(challenge_slug)

		file_path_relative_to_subdomain = './' + file_name_with_extension
		file_path_relative_to_domain = '{}/{}'.format(subdomain_name, file_name_with_extension)
		file_path_relative_to_root = '{}/{}/{}'.format(domain_name, subdomain_name, file_name_with_extension)
		subdomain_readme_text = self.subdomain_readme_row.format(challenge_name, problem_url, language, file_path_relative_to_subdomain)
		domain_readme_text = self.domain_readme_row.format(subdomain_name, challenge_name, problem_url, language, file_path_relative_to_domain)
		root_readme_text = self.root_readme_row.format(domain_name, subdomain_name, challenge_name, problem_url, language, file_path_relative_to_root)
		self.update_readme(
			subdomain_readme_path,
			subdomain_readme_text,
		)
		self.update_readme(
			domain_readme_path,
			domain_readme_text,
		)
		self.update_readme(
			root_readme_path,
			root_readme_text,
		)


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

				# Default should be empty
				file_extension = ''
				file_name = challenge_slug

				domain_name = 'Others'
				subdomain_name = 'Miscellaneous'

				domain_slug = ''
				subdomain_slug = ''

				if track:
					domain_name = track['track_name'].strip().replace(' ', '')
					subdomain_name = track['name'].strip().replace(' ', '')
					domain_slug = track['track_slug']
					subdomain_slug = track['slug']

				domain_url = self.domain_url.format(domain_slug)
				subdomain_url = self.subdomain_url.format(domain_slug, subdomain_slug)

				if language in self.file_extensions:
					if self.prepend_language_in_extension:
						file_extension += '.{}'.format(language)
					file_extension += '.{}'.format(self.file_extensions[language])

				if file_extension.endswith('.java'):
					file_name = challenge_name.replace(' ','')

				file_name_with_extension = file_name + file_extension
				file_path = os.path.join(self.base_folder_name, domain_name, subdomain_name, file_name_with_extension)
				if self.make_language_folder:
					file_path = os.path.join(self.base_folder_name, domain_name, subdomain_name, language, file_name_with_extension)
				self.store_submission(file_path, code)

				self.update_readmes(domain_name, subdomain_name, domain_url, subdomain_url,
						challenge_name, challenge_slug, language, file_name_with_extension)

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
