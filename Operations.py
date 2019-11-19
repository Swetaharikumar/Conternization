import os
import tarfile
import json
import shutil
import threading


class Operations:
    def __init__(self):
        self.container_num = 0
        self.config_data = None
        self.tar_name = None
        self.mount_points = None
        self.path = "base_images/basefs"
        self.mounts = {}
        self.kills = {}

    def mount_item(self, item, path, access, dir_name):
        path_list = path.split('/')
        path_list.pop(0)

        path = "launched_images/" + dir_name + "/basefs" + path
        # print("path: "+path)
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

        access_command = None
        if access == "READWRITE":
            access_command = "-o rw "
        else:
            access_command = "-o ro "

        command = "sudo mount --bind "+ access_command + dir_path + " " + path
        # print(command)
        os.system(command)
        umount_command = "sudo umount " + path
        if dir_name not in self.mounts:
            self.mounts[dir_name] = []

        self.mounts[dir_name].append(umount_command)

    def chroot(self, dir_name):
        startup_env = self.config_data["startup_env"]
        port = startup_env.split("=")[1].split(";")[0]
        command = 'sudo PORT=' + port + ' chroot launched_images/' + dir_name +'/basefs webserver/tiny.sh'
        kill_command = 'sudo chroot launched_images/' + dir_name +'/basefs webserver/cgi-bin/pkill.sh'
        self.kills[dir_name] = kill_command
        try:
            x = threading.Thread(target=run_server, args=(command,))
            x.start()
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

        img_path = "launched_images/" + dir_name
        if not os.path.exists(img_path):
            os.makedirs(img_path)
            tar_path = 'base_images/basefs.tar.gz'
            tar_file = tarfile.open(tar_path)
            print(img_path)
            tar_file.extractall(img_path)
            tar_file.close()

        # Parse the required mount points
        for mount in self.mount_points:
            mount_list = mount.split(' ')
            mount_item = mount_list[0]
            mount_path = mount_list[1]
            mount_access = mount_list[2]
            self.mount_item(mount_item, mount_path, mount_access, dir_name)

        self.chroot(dir_name)

        return dir_name

    def destroy_instance(self, dir_name):
        file_name = dir_name + '.cfg'
        # self.container_num -= 1
        kill_command = self.kills[dir_name]
        print(kill_command)
        os.system(kill_command)
        del self.kills[dir_name]
        for umount_command in reversed(self.mounts[dir_name]):
            os.system(umount_command)
        del self.mounts[dir_name]

        shutil.rmtree('containers/' + dir_name)

def run_server(command):
    os.system(command)
