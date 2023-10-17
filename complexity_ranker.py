import subprocess
import datetime
import os

def get_git_file_info(report):
    file_stats = []

    # Get the list of files tracked by Git
    files = subprocess.check_output(['git', 'ls-files']).decode('utf-8').split('\n')

    for f in [f for f in files if ".sol" in f]:
        # Get the commit history for the file
        commits = subprocess.check_output(['git', 'log', '--pretty=format:%ai', f]).decode('utf-8').split('\n')

        # Calculate the number of days between the first and most recent commit
        dates = [datetime.datetime.strptime(commit.split()[0], '%Y-%m-%d') for commit in commits]
        days_between = (max(dates) - min(dates)).days

        # Get the number of lines that have been cumulatively deleted for all the commits in the file
        deletions = subprocess.check_output(['git', 'log', '--pretty=tformat:', '--numstat', f]).decode('utf-8').split('\n')
        total_deletions = sum(int(deletion.split()[1]) for deletion in deletions if deletion)
        total_additions = sum(int(deletion.split()[0]) for deletion in deletions if deletion)

        # Get the number of authors that worked on the file
        authors = subprocess.check_output(['git', 'shortlog', '-sne', '--', f]).decode('utf-8').split('\n')
        num_authors = len(authors) - 1  # Subtract 1 to ignore the final empty string

        file_stats.append({
            "name": f,
            "ratio": total_deletions / total_additions if total_additions > 0 else 0.0,
            "adds": total_additions,
            "dels": total_deletions,
            "dr": days_between,
            "authors": num_authors,
        })

    sorted_file_stats = sorted(file_stats, key=lambda x: x["ratio"], reverse=True)

    max_name_len = max([len(f["name"]) for f in sorted_file_stats])

    print(f"File Name{(max_name_len-9)*' '} | Ratio| Adds  | Dels  | DateR | Total Authors")
    print(f"File Name,Ratio,Adds,Deletes,Date Range,Total Authors", file=report)

    for s in sorted_file_stats:
        print(s["name"] + (max_name_len-len(s["name"]))*" " + "   " + "%.3f" % s["ratio"], s["adds"], s["dels"], s["dr"], s["authors"], sep="\t")
        print(s["name"], "%.3f" % s["ratio"], s["adds"], s["dels"], s["dr"], s["authors"], sep=",", file=report)

# Change to the directory
with open("report.txt", "w") as report:
    dir_path = input("Enter Git directory full path:")
    os.chdir(dir_path)
    get_git_file_info(report)