import os
import tarfile
import json
import shutil
import time
from multiprocessing import Process, Queue


class Operations:
    def __init__(self):
        self.container_num = 0
        self.config_data = None
        self.tar_name = None
        self.mount_points = None
        self.mounts = {}
        self.pids = {}

    def mount_item(self, item, path, access, dir_name):
        path_list = path.split('/')
        path_list.pop(0)

        # create mount path
        path = "launched_images/" + dir_name + "/basefs" + path
        if not os.path.exists(path):
            command = "sudo mkdir -p " + path
            os.system(command)
            # os.makedirs(path)

        # Extract the tar file
        dir_path = 'containers/' + dir_name
        tar_path = 'mountables/' + item
        tar_file = tarfile.open(tar_path)
        tar_file.extractall(dir_path)
        tar_file.close()

        dir_path = dir_path + "/" + item.split(".")[0]

        # set access
        access_command = None
        if access == "READWRITE":
            access_command = "-o rw "
        else:
            access_command = "-o ro "

        # mount the corresponding folder
        command = "sudo mount --bind "+ access_command + dir_path + " " + path
        os.system(command)

        # store umount commands
        umount_command = "sudo umount " + path
        if dir_name not in self.mounts:
            self.mounts[dir_name] = []
        self.mounts[dir_name].append(umount_command)

    def chroot(self, dir_name):
        # get startup command
        env_command = self.config_data["startup_env"].replace(";", " ")

        # mount proc
        base_path = 'launched_images/' + dir_name + '/basefs'
        command = 'sudo mount -t proc proc ' + base_path + '/proc'
        os.system(command)

        # start the server
        # first command can pass test3, while the second one can pass test4
        # command = "sudo chroot " + base_path + ' /bin/bash -c "' + env_command + ' webserver/tiny.sh"'
        command = "sudo unshare -p -f --mount-proc=" + base_path + "/proc chroot " + base_path + ' /bin/bash -c "' + env_command + ' webserver/tiny.sh"'

        # start a new process to support the server
        try:
            q = Queue()
            x = Process(target=run_server, args=(command,q,))
            x.start()
            self.pids[dir_name] = q.get()
        except KeyboardInterrupt:
            pass
        except:
            print("Error: unable to start thread")

    def launch_instance(self, file_name):																																																										
        # self.container_num += 1

        # Read the needed tar_file name and mount points
        with open(file_name) as json_file:
            self.config_data = json.load(json_file)
            self.tar_name = self.config_data['base_image']
            self.mount_points = self.config_data['mounts']

        dir_name_part1 = self.config_data['name']
        dir_name_part2 = self.config_data['major']
        dir_name_part3 = self.config_data['minor']
        dir_name = dir_name_part1 + '-' + dir_name_part2 + '-' + dir_name_part3

        dir_path = 'containers/' + dir_name
        os.mkdir(dir_path)

        # extract base image if not exist
        img_path = "launched_images/" + dir_name
        if not os.path.exists(img_path):
            os.makedirs(img_path)
            tar_path = 'base_images/basefs.tar.gz'
            tar_file = tarfile.open(tar_path)
            tar_file.extractall(img_path)
            tar_file.close()

        # Parse the required mount points
        for mount in self.mount_points:
            mount_list = mount.split(' ')
            mount_item = mount_list[0]
            mount_path = mount_list[1]
            mount_access = mount_list[2]
            self.mount_item(mount_item, mount_path, mount_access, dir_name)

        # do chroot
        self.chroot(dir_name)

        return dir_name

    def destroy_instance(self, dir_name):
        file_name = dir_name + '.cfg'
        # self.container_num -= 1

        # kill server process
        pid = self.pids[dir_name]
        command = "sudo kill " + str(pid)
        os.system(command)
        del self.pids[dir_name]

        # umount proc
        base_path = 'launched_images/' + dir_name + '/basefs'
        command = "sudo umount " + base_path + '/proc'
        os.system(command)

        # umount mounted folders
        for umount_command in reversed(self.mounts[dir_name]):
            os.system(umount_command)
        del self.mounts[dir_name]

        # delete container folder
        shutil.rmtree('containers/' + dir_name)

def run_server(command, q):
    q.put(os.getpid())
    os.system(command)
