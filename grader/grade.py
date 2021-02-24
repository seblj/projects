import os, re, wget, json, requests, argparse, sys
import config as c

from datetime import date
today = date.today()

class Canvas:

    def __init__(self):
        self.headers = None
        self.group_users = {}
        self.downloads = {}
        self.group_userjson = []
        self.submissionjson = []
        self.assignment_id = c.ASSIGNMENT
        self.group_id = c.GROUP
        self.course_id = c.COURSE
        self.user_id = ""
        self.download = False
        self.gradeable_users = []
        self.users = None
        self.names = {}

    # Get token from file
    def set_token(self):
        with open(os.path.join(sys.path[0], 'canvas.token'), 'r') as f:
            token = f.readline()
            self.headers = {
                "Authorization" : token.strip()
            }

    # Check arguments added by user
    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--user', '-u', required=False)
        parser.add_argument('--download', '-d', required=False, action='store_true')
        args = parser.parse_args()
        if args.user != None:
            self.user_id = args.user
        self.download = args.download

    # Get id to download submission.
    def name_to_id(self, name):
        for key in self.names:
            if name == self.names[key]:
                return key

    # Get assignment_id based on path if possible. If requirements not met, use id set in config.
    # Requires the naming of assignments to only contain one number in the name, and that being
    # the assignment number. Also requires a path that contains 'a3' for example, which indicates assignment 3.
    def get_assignment(self):

        assignments = requests.get('https://uit.instructure.com/api/v1/courses/' + self.course_id + '/assignments', headers = self.headers)

        assignments_json = assignments.json()

        path = os.getcwd()
        for i in range(len(assignments_json)):
            for c in str(assignments_json[i]["name"]):
                if c.isdigit():
                    a = "a" + str(c)
                    if a in path:
                        self.assignment_id = str(assignments_json[i]["id"])
                

    # Get info about user in specified group and assignments from every single student.
    def get_request(self):

        group_users = requests.get('https://uit.instructure.com/api/v1/groups/' + self.group_id + '/users?per_page=2000', headers = self.headers)


        append_data = []
        submissions = requests.get('https://uit.instructure.com/api/v1/courses/' + self.course_id + '/assignments/' + self.assignment_id + '/submissions?per_page=200000', headers = self.headers)
        self.submissionjson = submissions.json()

        # Get all submissions if spread over more than one page
        while submissions.links['current']['url'] != submissions.links['last']['url']:
            submissions = requests.get(submissions.links['next']['url'], headers = self.headers)
            data = submissions.json()
            append_data += data


        alluser_append = []
        allusers = requests.get('https://uit.instructure.com/api/v1/courses/' + self.course_id + '/users?per_page=200000', headers = self.headers)
        userdata = allusers.json()
        # Get all users if spread over more than one page
        while allusers.links['current']['url'] != allusers.links['last']['url']:
            allusers = requests.get(allusers.links['next']['url'], headers = self.headers)
            data = allusers.json()
            alluser_append += data


        self.users = userdata + alluser_append
        self.submissionjson = self.submissionjson + append_data
        self.group_userjson = group_users.json()


    def parse_json(self):
        # store the id and names of users in dictionary
        for idx, user in enumerate(self.group_userjson):
            self.group_users[self.group_userjson[idx]["name"]] = self.group_userjson[idx]["id"]
            self.group_users[self.group_userjson[idx]["id"]] = self.group_userjson[idx]["name"]

        for idx, user in enumerate(self.users):
            self.names[self.users[idx]["id"]] = self.users[idx]["name"]

        for idx, user in enumerate(self.submissionjson):

            key = self.submissionjson[idx]["user_id"]
            try:
                for attach in self.submissionjson[idx]["attachments"]:
                    if attach["content-type"] != 'application/pdf':
                        self.downloads[key] = (attach["url"], attach["content-type"])

            except KeyError:
                pass


    def print_gradeable_users(self):
        for sub in self.submissionjson:
            if sub["workflow_state"] == "submitted":
                try:
                    userid = sub["user_id"]
                    if userid in self.group_users:
                        print(self.group_users[userid])

                except KeyError:
                    pass


    def download_submissions(self):
        path = os.getcwd()
        os.chdir(path)

        for key in self.group_users:

            if self.user_id:
                key = self.user_id

            try:
                if "rar" in self.downloads[key][1]:
                    ftype = ".rar"
                else:
                    ftype = ".zip"
                fname = "src-" + today.strftime("%d.%m.%y")
            except KeyError:
                if self.user_id:
                    break
                continue

            name = self.names[key].replace(" ", "")
            print(os.path.basename(os.getcwd()))
            print(name)
            if os.path.basename(os.getcwd()) != name:
                if not os.path.isdir(f"{name}"):
                    os.system(f"mkdir {name}")
            if os.path.basename(os.getcwd()) != name:
                os.chdir(path + "/" + name)
            wget.download(self.downloads[key][0], fname + ftype)
            os.chdir(path)
            if self.user_id:
                print("here")
                break
            

if __name__ == '__main__':
    canvas = Canvas()

    canvas.set_token()
    canvas.parse_arguments()
    canvas.get_assignment()
    canvas.get_request()
    canvas.parse_json()
    if not canvas.user_id.isdigit():
        name = canvas.user_id.title()
        canvas.user_id = canvas.name_to_id(name)

    if canvas.download:
        canvas.download_submissions()
    else:
        canvas.print_gradeable_users()
