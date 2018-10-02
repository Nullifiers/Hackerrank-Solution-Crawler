import os
import requests
import getpass

class Crawler():
	base_url = 'https://www.hackerrank.com/'
	login_url = base_url + 'auth/login'
	submissions_url = base_url + 'rest/contests/master/submissions/?offset={}&limit={}'
	challenge_url = base_url + 'rest/contests/master/challenges/{}/submissions/{}'
	domain_url = base_url + 'domains/{}/{}'
	problem_url = base_url + 'challenges/{}/problem'

	new_readme_text = '## [{}]({})\n\nProblem Name|Problem Link|Solution Link\n---|---|---'
	problem_readme_text = '{}|[Problem]({})|[Solution](/{}{})'

	base_folder_name = 'Hackerrank'

	# add other exclusive extensions if your data not crawled properly
	special_extensions = {
		'cpp14': 'cpp',
		'haskell': 'hs',
		'java8': 'java',
		'mysql': 'sql',
		'oracle': 'sql',
		'perl': 'pl',
		'python': 'py',
		'python3': 'py',
		'rust': 'rs',
		'text': 'txt',
	}

	def __init__(self):
		self.session = requests.Session()

	def login(self, username, password):
		resp = self.session.get(self.login_url, auth=(username, password))
		self.cookies = self.session.cookies.get_dict()
		self.headers = resp.request.headers

	def get_all_submissions_url(self, offset, limit):
		return self.submissions_url.format(offset, limit)

	def get_submission_url(self, challenge_slug, submission_id):
		return self.challenge_url.format(challenge_slug, submission_id)

	def store_submission(self, file_name, code):
		print(file_name)
		os.makedirs(os.path.dirname(file_name), exist_ok=True)
		with open(file_name, 'w') as text_file:
			print(code, file=text_file)

	def update_readme(self, challenge_name, readme_file_path, challenge_slug, file_name, file_extension):
		problem_url = self.problem_url.format(challenge_slug)
		text = self.problem_readme_text.format(challenge_name, problem_url, file_name, file_extension)
		with open(readme_file_path, 'a') as text_file:
			print(text, file=text_file)

	def create_readme(self, track_name, track_url, file_name):
		if track_name is not None:
			os.makedirs(os.path.dirname(file_name), exist_ok=True)
			text = self.new_readme_text.format(track_name, track_url)
			with open(file_name, 'w') as text_file:
				print(text, file=text_file)

	def get_file_path(self, folder_name, file_name_with_extension):
		return os.path.join(self.base_folder_name, folder_name, file_name_with_extension)

	def get_readme_path(self, folder_name):
		return os.path.join(self.base_folder_name, folder_name, 'README.md')
				
	def get_submissions(self, submissions):
		headers = self.headers
		
		for submission in submissions:
			id = submission['id']
			# challenge_id = submission['challenge_id']
			# contest_id = submission['contest_id']
			# hacker_id = submission['hacker_id']
			status = submission['status']
			# created_at = submission['created_at']
			language = submission['language']
			status_code = submission['status_code']
			# score = submission['score']
			challenge = submission['challenge']
			challenge_name = challenge['name']
			challenge_slug = challenge['slug']
			submission_url = self.get_submission_url(challenge_slug, id)

			if status == 'Accepted' or status_code == 2:
				resp = self.session.get(submission_url, headers=headers)
				data = resp.json()['model']
				code = data['code'].replace('\\n', '\n')
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
					folder_name = os.path.join(parent_folder_name ,track_folder_name)
				
				if language in self.special_extensions:
					file_extension = '.' + self.special_extensions[language]

				if file_extension == '.java':
					file_name = challenge_name.replace(' ','')
				
				file_path = self.get_file_path(folder_name, file_name + file_extension)
				if not os.path.exists(file_path):
					self.store_submission(file_path, code)
					readme_file_path = self.get_readme_path(folder_name)
					if not os.path.exists(readme_file_path):
						self.create_readme(track_folder_name, track_url, readme_file_path)
					self.update_readme(
						challenge_name,
						readme_file_path,
						challenge_slug,
						file_name,
						file_extension,
					)
		print('All Solutions Crawled')

def main():
	offset = 0
	limit  = 10 # you should change this

	username = input('Username: ')
	password = getpass.getpass('Password: ')

	crawler = Crawler()
	crawler.login(username, password)

	limit = input('Enter limit needed to crawl: ')
	all_submissions_url = crawler.get_all_submissions_url(offset, limit)
	
	resp = crawler.session.get(all_submissions_url, headers=crawler.headers)
	data = resp.json()
	models = data['models']
	crawler.get_submissions(models)

if __name__ == "__main__": main()