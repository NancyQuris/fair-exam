# Pre-requisites
 - Python 3.8.6 or above
 - Packages: cryptography, pyftpdlib, numpy, ftplib, cv2

# Project Structure
 - **ftp_server.py:** server for uploading and downloading of exam papers.
 - **exam_server.py**: server for streaming and netstat data. 
 - **instructor_client.py**: client to be run by the instructor to upload exam papers and start exams.
 - **student_client.py**: client to be run the student, to download exam papers.
 - **settings.py:** configurations for the servers.

# How to Run the Programs
Each single client/server can be run by:
```bash
python file_name.py
```
The ftp_server will be always running, and the rest programs are run on demand. The detailed flow demo will be shown in our presentation.
