import os
import tarfile
import json




class Operations:
    def __init__(self):
        self.container_num = 0
        self.tar_name = None
        self.mount_points = None

    def mount_item(self, item, path, access, dir_path):
        path_list = path.split('/')
        path_list.pop(0)

        for directory in path_list:
            if not os.path.isdir(dir_path + '/' + directory):
                os.mkdir(dir_path + '/' + directory)

    def launch_instance(self, file_name):
        self.container_num += 1
        dir_name = 'containers/container' + str(self.container_num)
        os.mkdir(dir_name)



        # Read the needed tar_file name and mount points
        with open(file_name) as json_file:
            config_data = json.load(json_file)
            self.tar_name = config_data['base_image']
            self.mount_points = config_data['mounts']

        # Extract the base image
        # tar_path = 'base_images/' + self.tar_name
        # tar_file = tarfile.open(tar_path)
        # tar_file.extractall(dir_path)
        # tar_file.close()

        # Parse the required mount points
        # for mount in self.mount_points:
        #     mount_list = mount.split('')
        #     mount_item = mount_list[0]
        #     mount_path = mount_list[1]
        #     mount_access = mount_list[2]
        #     self.mount_item(self, mount_item, mount_path, mount_access, dir_path)

        return dir_name


def launch_instance(name):
    return None