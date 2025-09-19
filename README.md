How to run:
1. instal depedencies in requirements.txt
   pip install -r requirements.txt
2. execute : python main.py
3. dont forget to create .env file to configure key
4. if using docker, create the image
   docker build -t document-analyst .
5. run the image
   docker run -it --rm -p 8000:8000 document-analyst
