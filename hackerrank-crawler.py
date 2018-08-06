import os
import requests

def get_headers():
	# provide these to start crawling
	# remember_hacker_token = ''
	_hrank_session='ae67b3fec360f0297c458d4552def00c0b1490bf99532fbfba57f0b00765c7b07879f3a1209159ca97d5d660eb439f961325d1de2ef88bb1e0d356ce2f44983a'
	headers = {
		'Cookie': '_hrank_session='+_hrank_session,
	}
	return headers

def get_all_submissions_url(offset, limit):
	offset, limit = str(offset), str(limit)
	base_url = 'https://www.hackerrank.com/rest/contests/master/submissions/'
	url = base_url + '?offset=' + offset + '&limit=' + limit
	return url

def get_submission_url(challenge_slug, submission_id):
	submission_id = str(submission_id)
	base_url = 'https://www.hackerrank.com/rest/contests/master/challenges/'
	url = base_url + challenge_slug + '/submissions/' + submission_id
	return url

def crawl_submissions(submissions):
	headers = get_headers()
	
	# add other exclusive extensions if your data not crawled properly
	special_extensions = {
		'cpp14': 'cpp',
		'haskell': 'hs',
		'java8': 'java',
		'mysql': 'sql',
		'oracle': 'sql',
		'python': 'py',
		'python3': 'py',
		'text': 'txt',
	}
	
	for submission in submissions:
		id = submission['id']
		challenge_id = submission['challenge_id']
		contest_id = submission['contest_id']
		hacker_id = submission['hacker_id']
		status = submission['status']
		kind = submission['kind']
		created_at = submission['created_at']
		language = submission['language']
		in_contest_bounds = submission['in_contest_bounds']
		status_code = submission['status_code']
		score = submission['score']
		challenge = submission['challenge']
		challenge_name = challenge['name']
		challenge_slug = challenge['slug']
		submission_url = get_submission_url(challenge_slug, id)
		if status == 'Accepted' or status_code == 2:
			resp = requests.get(submission_url, headers=headers)
			data = resp.json()['model']
			code = data['code'].replace('\\n', '\n')
			folder_name = 'Others/'
			track = data['track']
			file_extension = '.' + language
			if track:
				track_folder_name = track['name'].strip().replace(' ', '-')
				parent_folder_name = track['track_name'].strip().replace(' ', '-')
				folder_name = parent_folder_name + '/' + track_folder_name + '/'
			if language in special_extensions:
				file_extension = '.' + special_extensions[language]
			file_name = folder_name + challenge_slug + file_extension

			# write only if submission not recorded
			if not os.path.exists(file_name):
				print(file_name)
				os.makedirs(os.path.dirname(file_name), exist_ok=True)
				with open(file_name, 'w') as text_file:
					print(code, file=text_file)
	print('All Solutions Crawled')

if __name__ == "__main__":
	offset = 0
	limit  = 15 # you should change this

	all_submissions_url = get_all_submissions_url(offset, limit)
	headers = get_headers()
	
	resp = requests.get(all_submissions_url, headers=headers)
	data = resp.json()
	models = data['models']
	# print(models)
	crawl_submissions(models)