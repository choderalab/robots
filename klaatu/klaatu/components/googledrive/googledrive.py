"""
Created on 14.08.2014

@author: jan-hendrikprinz
"""

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import uuid


class Distributor(object):
    """
    Class to easily place scripts on the googledrive for the robot.
    """

    folder_list = {
        'evo_worklist': '0BxfZbreCWWAAcVF1ZE9RcDJBdTg',
        'infinite_script': '0BxfZbreCWWAAY09qeHdYeHBjTU0',
        'momentum_process': '0BxfZbreCWWAAdVMtblBiSkFFLWM',
        'hpd300_protocol': '0BxfZbreCWWAAai1oRDc3a2VsNXM',
        'hpd300_report': '0BxfZbreCWWAAQmU1ajFEXzFSN2M',
        'infinite_platedefinition': '0BxfZbreCWWAAYjN5SGpiaDUyZXM',
        'infinite_result': '0BxfZbreCWWAAMnNuNHJ2Tml5NDg',
        'momentum_experiment': '0BxfZbreCWWAAUHpRSTFCLXFuSDQ'
    }

    file_type = {
        'evo_worklist': '.gwl',
        'infinite_script': '.xml',
        'momentum_process': '.mpr',
        'hpd300_protocol': '.hpdd',
        'hpd300_report': '.DATA.xml',
        'infinite_platedefinition': '.pdfx',
        'infinite_result': '.xml',
        'momentum_experiment': '.mex'
    }

    def __init__(self):
        """Initializes a Distributor object and opens the connection to the googledrive momentum@choderalab.org

        Notes
        -----

        Requires pydrive and google python api to be installed. Alsoa clients_secrets.json file needs to be present in the folder.
        """

        # Setup google drive

        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)

    @property
    def supported(self):
        """Returns a list of supported file locations/types

        Returns
        -------
        filetypes : list of string
            A list of strings that contain the supported device locations where files can be place and read.
        """
        return Distributor.file_type.keys()

    def place(self, name, device, s):
        """Create a new file on the google drive in the appropriate folder

        Parameters
        ----------
        name : string
            The file name of the file to be created. An 32bit UUID is added to the end as well as the correct file ending
        device : string
            A string specifing the type and folder to be used. Distributor.supported lists the allowed types
        s : string
            The content of the file to be placed on the googledrive

        Returns
        -------
        full_name : string
            Full filename used to create file including uuid and fileextension
        """

        if device in self.supported:
            u = str(uuid.uuid4()).split("-")[0]
            full_name = name + "-" + u + Distributor.file_type[device]

            file1 = self.drive.CreateFile(
                {'title': full_name, "parents": [{"kind": "drive#fileLink", "id": Distributor.folder_list[device]}]})
            file1.SetContentString(s)
            file1.Upload()

            return full_name

    def ls(self, device):
        if device in self.supported:
            folder = Distributor.folder_list[device]
            file_list = self.drive.ListFile({'q': "'" + folder + "' in parents and trashed=false"}).GetList()

            return file_list
            return {file['id']: file['title'] for file in file_list}
        else:
            return []
            return {}

    def get(self, file_id):
        file_handle = self.drive.CreateFile({'id': file_id})
        content = file_handle.GetContentString()
        return content


if __name__ == '__main__':
    db = Distributor()
    # s = 'Hallo'
    #    print db.place('name', 'momentum_process', s)

    files = db.ls('infinite_result')

    print [f['title'] for f in files]

    s = db.get(files[2]['id'])

    print s

    pass
