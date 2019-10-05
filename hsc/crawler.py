import os
import requests
import getpass
from hsc.helper import update_progress


class Crawler:
    base_url = 'https://www.hackerrank.com/'
    login_url = base_url + 'auth/login'
    submissions_url = base_url + 'rest/contests/master/submissions/?offset={}&limit={}'
    challenge_url = base_url + 'rest/contests/master/challenges/{}/submissions/{}'
    domain_url = base_url + 'domains/{}/{}'
    problem_url = base_url + 'challenges/{}/problem'

    new_readme_text = '## [{}]({})\n\n|Problem Name|Problem Link|Language|Solution Link|\n---|---|---|---\n'
    readme_headers_len = len(new_readme_text.split('\n'))
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
        self.update_progress = True

    def login(self, username, password):
        resp = self.session.get(self.login_url, auth=(username, password))
        self.cookies = self.session.cookies.get_dict()
        self.headers = resp.request.headers
        self.get_number_of_submissions()
        return self.total_submissions != 0

    def authenticate(self):
        username = input('Hackerrank Username: ')
        password = getpass.getpass('Hackerrank Password: ')
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
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w') as text_file:
            text_file.write(code)

    def update_readme(self, readme_file_path, problem_readme_text):
        header_length = self.readme_headers_len
        with open(readme_file_path, 'r+') as text_file:
            lines = text_file.readlines()
            lines.append(problem_readme_text)
            sorted_lines = lines[:header_length] + sorted(lines[header_length:])
            text_file.seek(0)
            text_file.writelines(sorted_lines)

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

        submission_count = 1
        total_submissions = len(submissions)
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
                    file_name = challenge_name.replace(' ', '')

                file_path = self.get_file_path(folder_name, file_name + file_extension)
                if not os.path.exists(file_path):
                    self.store_submission(file_path, code)
                    readme_file_path = self.get_readme_path(folder_name)
                    if not os.path.exists(readme_file_path):
                        self.create_readme(track_folder_name, track_url, readme_file_path)
                    problem_url = self.problem_url.format(challenge_slug)
                    readme_text = self.problem_readme_text.format(challenge_name, problem_url, language,
                                                                  file_name + file_extension)
                    self.update_readme(
                        readme_file_path,
                        readme_text,
                    )
            if self.update_progress:
                update_progress(submission_count, total_submissions, challenge_name)
            submission_count += 1
        print('All Solutions Crawled')


def main():
    offset = 0
    limit = 10  # you should change this

    crawler = Crawler()

    while not crawler.authenticate():
        print('Auth was unsuccessful')

    limit = input('Enter limit needed to crawl: ')
    all_submissions_url = crawler.get_all_submissions_url(offset, limit)

    resp = crawler.session.get(all_submissions_url, headers=crawler.headers)
    data = resp.json()
    models = data['models']
    crawler.get_submissions(models)


if __name__ == "__main__": 
    main()
