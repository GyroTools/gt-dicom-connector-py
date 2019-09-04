import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from gtdicom.connection import gtDicomConnection
from gtdicom.models.patient import Patient
from gtdicom.scu import Scu
from gtdicom.utils import to_path_array, get_filelist_from_path_array, is_dicom_file


class gtDicom:
    def __init__(self, connection: gtDicomConnection):
        self.connection = connection

    def echo(self):
        return Scu.c_echo(self.connection.host, self.connection.port, self.connection.calling_aet,
                                 self.connection.called_aet)

    def get_patients(self, search_string='*'):
        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Patient.attributes:
            ds.__setattr__(attr, '')

        ds.PatientName = search_string
        ds.QueryRetrieveLevel = 'PATIENT'

        identifiers = Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
        patients = []
        for identifier in identifiers:
            patient = Patient()
            patient.create(identifier, self.connection)
            patients.append(patient)

        return patients

    def store(self, files):
        files = to_path_array(files)
        if not files:
            return None

        files = get_filelist_from_path_array(files)

        for file in files:
            if is_dicom_file(file):
                try:
                    f = open(file, 'rb')
                    ds = dcmread(f, force=True)
                    f.close()
                    Scu.c_store(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
                except IOError:
                    pass



