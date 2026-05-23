from somecommon import get_original_git_show, generate_commit_messages

import subprocess


def get_latest_commit_id():
    cmd = ["git", "--no-pager", "rev-parse", "HEAD"]
    commit_id = subprocess.check_output(cmd).decode("utf-8").strip()
    return commit_id


full_id = get_latest_commit_id()
newmsg = generate_commit_messages(get_original_git_show(full_id))


def amend_last_commit_message(new_message):
    print(new_message)
    subprocess.run(["git", "commit", "--amend", "-m", new_message], check=True)


amend_last_commit_message(newmsg)
