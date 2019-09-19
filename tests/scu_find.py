from gtdicom.connection import gtDicomConnection
from gtdicom.gtdicom import gtDicom

get_studies = True
get_series = True
download_series = False

#addr = 'www.dicomserver.co.uk'
#port = 104

addr = 'www.dicomserver.co.uk'
port = 104

connection = gtDicomConnection(addr, port)
gt_dicom = gtDicom(connection)

if not gt_dicom.echo():
    print('ERROR: Cannot establish a connection to the DICOM node. Please check the hostname and port')
    exit()

# study0 = gt_dicom.get_study('1.2.826.0.1.3680043.9.6384.2.5000023.20190827124526.136.9')
# series1 = gt_dicom.get_serie('1.2.826.0.1.3680043.9.6384.2.5000023.20190827124526.136.11')
# series1.download('C:/Users/martin/Desktop/temp/dicom/PACS')
# series0 = gt_dicom.get_serie('1.2.826.0.1.3680043.9.6384.2.5000023.20190827121233.364.3')
# series0.download('C:/Users/martin/Desktop/temp/dicom/PACS')

patients = gt_dicom.get_patients('M*', modality='MR')

series = gt_dicom.get_series(modality='MR')
for serie in series:
    print(
        f'    SERIES: Name: {serie.SeriesDescription}, Date: {serie.SeriesDate}, Time: {serie.SeriesTime}, Modality: {serie.Modality}, UID: {serie.SeriesInstanceUID}')
    if download_series:
        try:
            serie.download('C:/Users/martin/Desktop/temp/dicom/PACS', extension='.dcm')
        except Exception as e:
            print('Error: ' + str(e))

patients = gt_dicom.get_patients('MR/*')

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
                            try:
                                serie.download('C:/Users/martin/Desktop/temp/dicom/PACS', extension='.dcm')
                            except Exception as e:
                                print('Error: ' + str(e))
    except Exception as e:
        print('ERROR: ' + str(e))

patient0 = gt_dicom.get_patient(patients[0].PatientID)
series = patient0.get_series()
study0 = gt_dicom.get_study(studies[0].StudyInstanceUID)
series0 = gt_dicom.get_serie(series[0].SeriesInstanceUID)
#if download_series:
#    filenames = series0.download('C:/Users/martin/Desktop/temp/dicom/PACS', extension='.dcm')


