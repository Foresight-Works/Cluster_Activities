import boto3
import zipfile
import os
import shutil

my_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
'''
test download
s3.Bucket(my_bucket).download_file('treatments/T201008CHEM_SUBS.CSV', './T201008CHEM_SUBS.CSV')
'''
source_files=open ('./files_lists/sources.txt').read().split ('\n')
print ('The number of source files:',len (source_files))
for source_file in source_files:
    print ('source file:',source_file)

    # Download and unzip the source file (Month/Year data)
    zip_file_save_path='./downloaded_file/{fn}'.format(fn=source_file)
    s3.Bucket(my_bucket).download_file('sources/{fn}'.format(fn=source_file),zip_file_save_path)
    archive = zipfile.ZipFile(zip_file_save_path,'r')
    archive.extractall('./downloaded_file/')
    archive.close()
    # or: archive = ZipFile('data1.zip', 'r')
    files = os.listdir('./downloaded_file/')
    print ('files downloaded:',files)

    # Rename and upload the downloaded files
    for file in files:
        newname=('_').join(file.split(' '))
        print ('file:{f} | new name: {n}'.format (f=file,n=newname))
        os.rename('./downloaded_file/{on}'.format(on=file),'./downloaded_file/{nn}'.format(nn=newname))

    file_types=["ADDR","CHEM","PDPI"]
    directories=['./practices','./treatments','./prescriptions']
    directories=['/practices','/treatments','/prescriptions']
    directories=['practices','treatments','prescriptions']
    files = os.listdir('./downloaded_file/')
    for file in files:
        file_path='./downloaded_file/{nn}'.format(nn=file)
        s3_client = boto3.client('s3')
        for index, file_type in enumerate (file_types):
            directory=directories[index]
            save_path='{d}/{f}'.format (d=directory,f=file)
            if file_type in file:
                print ('{ft} in {f}'.format (f=file, ft=file_type))
                s3_client.upload_file(file_path,my_bucket,save_path)
                print ('Saved {f} to {d} as {sp}'.format (f=file,d=directory,sp=save_path))

        os.remove(file_path)

    os.system('rm -rf ~/.local/share/Trash/*')
