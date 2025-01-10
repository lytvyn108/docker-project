# Base image
FROM nginx:alpine

# Copy website files to the container
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80


# FROM openjdk:8-jdk-alpine
# VOLUME /tmp
# ARG JAVA_OPTS
# ENV JAVA_OPTS=$JAVA_OPTS
# COPY dockerproject.jar dockerproject.jar
# EXPOSE 80
# ENTRYPOINT exec java $JAVA_OPTS -jar dockerproject.jar
# For Spring-Boot project, use the entrypoint below to reduce Tomcat startup time.
#ENTRYPOINT exec java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar dockerproject.jar
