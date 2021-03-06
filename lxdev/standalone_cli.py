import os, argparse
import lxdev

defined_tasks = [
	"check_dirs",
	"rsync_to_container",
	"rsync_from_container",
	"get_remote_working_directory"
]

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("task", type=str, help=f"action to do, out of: {''.join(s + ', ' for s in defined_tasks)}")
	parser.add_argument("remote_hostname", type=str, help="remote_hostname")
	parser.add_argument("if_delete", type=str, help="'delete' or 'keep'? how to handle overwriting files at destination.")

	args = parser.parse_args()

	assert args.task in defined_tasks

	if args.task == "check_dirs":
		print("Hello this is the standalone cli file")
		print(f"This .py's path is: {os.path.dirname(os.path.realpath(__file__))}")
		print(f"User dir is: {os.path.expanduser('~')}")
		print(f"Script called from {os.getcwd()}")

	elif args.task in ["rsync_to_container", "rsync_from_container", "get_remote_working_directory"]:
		assert "home" in os.getcwd(), "this function is defined for folders within a host users home directory only"
		
		lxd_container_name = assert_we_can_extract_lxd_name_from_hostname(args.remote_hostname)

		if args.task in ["rsync_to_container", "rsync_from_container"]:
			if args.if_delete == "delete":
				delete = True
			elif args.if_delete == "keep":
				delete = False
			else:
				assert 0, "Invalid if_delete argument passed, should be 'delete' or 'keep'"

		with  lxdev.RemoteClient(
			host = args.remote_hostname, # e.g. lxd_doc-dev
			lxd_container_name = lxd_container_name,
			local_working_directory = os.getcwd() # the directory where this is called from
			) as ssh_remote_client:

				# print("Connected!")
				if args.task == "rsync_to_container":
					ssh_remote_client.rsync_to_container(delete=delete)
				elif args.task == "rsync_from_container":
					ssh_remote_client.rsync_from_container(delete=delete)
				elif args.task == "get_remote_working_directory":
					print(ssh_remote_client.remote_working_directory, end="") 
					# this 'print' is used to save the result as a variable in some bash scripts, 
					# e.g. remote_dir=$(lxdev get_remote_working_directory lxd_doc-dev keep)
				else:
					assert 0	
	else:
		assert 0, "Invalid task given"


def assert_we_can_extract_lxd_name_from_hostname(hostname):
	lxd_container_name = hostname.replace("lxd_", "") # e.g. lxd_doc-dev -> doc-dev
	result, error = lxdev.run_local_cmd(f"lxc info {lxd_container_name}")
	assert "Error: Not Found" not in result+error, f"Invalid lxd container name inferred of: {lxd_container_name}"
	return lxd_container_name