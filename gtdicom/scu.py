import os

from pydicom.dataset import Dataset

from pynetdicom import AE, evt, build_role, StoragePresentationContexts, \
    QueryRetrievePresentationContexts,PYNETDICOM_IMPLEMENTATION_UID, PYNETDICOM_IMPLEMENTATION_VERSION
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, PatientRootQueryRetrieveInformationModelGet, VerificationSOPClass

from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, \
    ExplicitVRBigEndian, DeflatedExplicitVRLittleEndian

from gtdicom.exception import gtDicomException


class Scu:
    @staticmethod
    def c_echo(host, port, calling_aet='GETSCU', called_aet='ANY-SCP'):
        echo = False

        # Initialise the Application Entity
        ae = AE(ae_title=calling_aet)

        # Add a requested presentation context
        ae.add_requested_context(VerificationSOPClass)

        # Associate with peer AE
        assoc = ae.associate(host, port, ae_title=called_aet)

        if assoc.is_established:
            # Use the C-FIND service to send the identifier
            status = assoc.send_c_echo()

            if status:
                echo = True
            else:
                echo = False

            # Release the association
            assoc.release()
        else:
            echo = False

        return echo

    @staticmethod
    def c_find(host, port, ds: Dataset, calling_aet='GETSCU', called_aet='ANY-SCP'):
        identifiers = []

        # Initialise the Application Entity
        ae = AE(ae_title=calling_aet)

        # Add a requested presentation context
        ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

        # Associate with peer AE
        assoc = ae.associate(host, port, ae_title=called_aet)

        if assoc.is_established:
            # Use the C-FIND service to send the identifier
            responses = assoc.send_c_find(ds)

            for (status, identifier) in responses:
                if status:
                    # If the status is 'Pending' then identifier is the C-FIND response
                    if status.Status in (0xFF00, 0xFF01):
                        Scu._copy_attr(ds, identifier)
                        if  not identifier in identifiers:
                            identifiers.append(identifier)
                else:
                    raise gtDicomException('Connection timed out, was aborted or received invalid response')

            # Release the association
            assoc.release()
        else:
            raise gtDicomException('Association rejected, aborted or never connected')

        return identifiers

    @staticmethod
    def c_get(host, port, ds: Dataset, output_directory: os.path = None, overwrite=True, file_extension=None, ae_title='GETSCU', called_aet='ANY-SCP'):
        # Initialise the Application Entity
        ae = AE(ae_title=ae_title)

        for context in QueryRetrievePresentationContexts:
            ae.add_requested_context(context.abstract_syntax)
        for context in StoragePresentationContexts[:115]:
            ae.add_requested_context(context.abstract_syntax)

        # Add SCP/SCU Role Selection Negotiation to the extended negotiation
        # We want to act as a Storage SCP
        ext_neg = []
        for context in StoragePresentationContexts:
            ext_neg.append(build_role(context.abstract_syntax, scp_role=True))

        def _handle_store(event):
            """Handle a C-STORE request."""
            mode_prefixes = {
                'CT Image Storage': 'CT',
                'Enhanced CT Image Storage': 'CTE',
                'MR Image Storage': 'MR',
                'Enhanced MR Image Storage': 'MRE',
                'Positron Emission Tomography Image Storage': 'PT',
                'Enhanced PET Image Storage': 'PTE',
                'RT Image Storage': 'RI',
                'RT Dose Storage': 'RD',
                'RT Plan Storage': 'RP',
                'RT Structure Set Storage': 'RS',
                'Computed Radiography Image Storage': 'CR',
                'Ultrasound Image Storage': 'US',
                'Enhanced Ultrasound Image Storage': 'USE',
                'X-Ray Angiographic Image Storage': 'XA',
                'Enhanced XA Image Storage': 'XAE',
                'Nuclear Medicine Image Storage': 'NM',
                'Secondary Capture Image Storage': 'SC'
            }

            ds = event.dataset

            # Because pydicom uses deferred reads for its decoding, decoding errors
            #   are hidden until encountered by accessing a faulty element
            try:
                sop_class = ds.SOPClassUID
                sop_instance = ds.SOPInstanceUID
            except Exception as exc:
                # Unable to decode dataset
                return 0xC210

            try:
                # Get the elements we need
                mode_prefix = mode_prefixes[sop_class.name]
            except KeyError:
                mode_prefix = 'UN'

            filename = '{0!s}.{1!s}'.format(mode_prefix, sop_instance)
            if file_extension:
                filename += file_extension

            if os.path.exists(filename) and not overwrite:
                raise gtDicomException('The dicom file already exists and overwrite=False --> aborting')

            # Presentation context
            cx = event.context

            ## DICOM File Format - File Meta Information Header
            # If a DICOM dataset is to be stored in the DICOM File Format then the
            # File Meta Information Header is required. At a minimum it requires:
            #   * (0002,0000) FileMetaInformationGroupLength, UL, 4
            #   * (0002,0001) FileMetaInformationVersion, OB, 2
            #   * (0002,0002) MediaStorageSOPClassUID, UI, N
            #   * (0002,0003) MediaStorageSOPInstanceUID, UI, N
            #   * (0002,0010) TransferSyntaxUID, UI, N
            #   * (0002,0012) ImplementationClassUID, UI, N
            # (from the DICOM Standard, Part 10, Section 7.1)
            # Of these, we should update the following as pydicom will take care of
            #   the remainder
            meta = Dataset()
            meta.MediaStorageSOPClassUID = sop_class
            meta.MediaStorageSOPInstanceUID = sop_instance
            meta.ImplementationClassUID = PYNETDICOM_IMPLEMENTATION_UID
            meta.TransferSyntaxUID = cx.transfer_syntax

            # The following is not mandatory, set for convenience
            meta.ImplementationVersionName = PYNETDICOM_IMPLEMENTATION_VERSION

            ds.file_meta = meta
            ds.is_little_endian = cx.transfer_syntax.is_little_endian
            ds.is_implicit_VR = cx.transfer_syntax.is_implicit_VR

            status_ds = Dataset()
            status_ds.Status = 0x0000

            # Try to save to output-directory
            if output_directory is not None:
                filename = os.path.join(output_directory, filename)

            try:
                # We use `write_like_original=False` to ensure that a compliant
                #   File Meta Information Header is written
                ds.save_as(filename, write_like_original=False)
                status_ds.Status = 0x0000  # Success
            except IOError:
                raise gtDicomException('Could not write file to specified directory: ' + format(
                    os.path.dirname(filename)) + '. Directory may not exist or you may not have write permission')
                # Failed - Out of Resources - IOError
                status_ds.Status = 0xA700
            except:
                raise gtDicomException('Could not write file to specified directory: ' + format(
                    os.path.dirname(filename)))
                status_ds.Status = 0xA701

            return status_ds

        handlers = [(evt.EVT_C_STORE, _handle_store)]

        # Request association with remote
        assoc = ae.associate(host,
                             port,
                             ae_title=called_aet,
                             ext_neg=ext_neg,
                             evt_handlers=handlers)

        # Send query
        if assoc.is_established:
            response = assoc.send_c_get(ds)

            for status, identifier in response:
                pass

            assoc.release()
        else:
            raise gtDicomException('Association rejected, aborted or never connected')

    @staticmethod
    def c_store(host, port, dataset: Dataset, calling_aet='GETSCU', called_aet='ANY-SCP'):
        # Set Transfer Syntax options
        transfer_syntax = [ExplicitVRLittleEndian,
                           ImplicitVRLittleEndian,
                           DeflatedExplicitVRLittleEndian,
                           ExplicitVRBigEndian]

        # Initialise the Application Entity
        ae = AE(ae_title=calling_aet)

        for context in StoragePresentationContexts:
            ae.add_requested_context(context.abstract_syntax, transfer_syntax)

        # Associate with peer AE
        assoc = ae.associate(host, port, ae_title=called_aet)

        if assoc.is_established:
            # Use the C-FIND service to send the identifier
            status = assoc.send_c_store(dataset)

            if not status:
                raise gtDicomException('Transfer unsuccessful')

            # Release the association
            assoc.release()
        else:
            raise gtDicomException('Association rejected, aborted or never connected')

    @staticmethod
    def _copy_attr(obj_src, obj_tgt):
        # pass
        for attr, value in obj_src.items():
           if not attr in obj_tgt:
               obj_tgt[attr] = value



