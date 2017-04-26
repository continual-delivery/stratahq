FROM jenkins
# Install tools we need for different things
USER root
RUN apt-get update && apt-get install -y netcat-traditional
USER jenkins
COPY plugins.txt /usr/share/jenkins/ref/

RUN /usr/local/bin/plugins.sh /usr/share/jenkins/ref/plugins.txt