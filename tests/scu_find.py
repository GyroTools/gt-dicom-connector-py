from gtdicom.connection import gtDicomConnection
from gtdicom.gtdicom import gtDicom

get_studies = True
get_series = True
download_series = True

#addr = 'www.dicomserver.co.uk'
#port = 104

addr = 'www.dicomserver.co.uk'
port = 104

connection = gtDicomConnection(addr, port)
gt_dicom = gtDicom(connection)

if not gt_dicom.echo():
    print('ERROR: Cannot establish a connection to the DICOM node. Please check the hostname and port')
    exit()

patients = gt_dicom.get_patients('Martin*')

for patient in patients:
    try:
        print(f'PATIENT: {patient.PatientName}')

        if get_studies:
            studies = patient.get_studies()
            for study in studies:
                print(f'  STUDY: Name: {study.StudyDescription}, Date: {study.StudyDate}, Time: {study.StudyTime}, UID: {study.StudyInstanceUID}')

                if get_series:
                    series = study.get_series()
                    for serie in series:
                        print(f'    SERIES: Name: {serie.SeriesDescription}, Date: {serie.SeriesDate}, Time: {serie.SeriesTime}, Modality: {serie.Modality}, UID: {serie.SeriesInstanceUID}')
                        if download_series:
                            serie.download('C:/Users/martin/Desktop/temp/dicom/PACS', extension='.dcm')
    except Exception as e:
        print('ERROR: ' + str(e))


