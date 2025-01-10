FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy application code
COPY app/ /app

# Install dependencies
RUN pip install flask faker requests

# Expose the port
EXPOSE 80

# Start the application
CMD ["python", "app.py"]



# FROM openjdk:8-jdk-alpine
# VOLUME /tmp
# ARG JAVA_OPTS
# ENV JAVA_OPTS=$JAVA_OPTS
# COPY dockerproject.jar dockerproject.jar
# EXPOSE 80
# ENTRYPOINT exec java $JAVA_OPTS -jar dockerproject.jar
# For Spring-Boot project, use the entrypoint below to reduce Tomcat startup time.
#ENTRYPOINT exec java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar dockerproject.jar
