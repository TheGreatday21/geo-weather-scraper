##this is to define how our image shall be built 

FROM python:3.13

## this is now going to be our base image 

WORKDIR /WEATHER_SCRAPPING_TOOL

##COPY  requirements.txt .
##copying the requirement to the working directory 

RUN pip3 install --upgrade pip

RUN pip install tk requests pandas python-dotenv

##using the no cache dir since we are working with containers
##this is to install the requirements on run

COPY  . .
##this means copy all things from the local directory(WEATHER_SCRAPPING_TOOL) to the current directory (gui_app)

ENV PYTHONPATH=/WEATHER_SCRAPPING_TOOL 
##adding this environment path since i have a complex folder heirarchy in my application to enable docker jump out of gui to parent folder and find src 

##This command shall be executed once the container is run
CMD [ "python", "gui_app/app.py" ]