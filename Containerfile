FROM python:3.8.5-alpine3.12

# Update the packages
RUN apk update

# Install the ansible dependancies
RUN apk add gcc libffi-dev musl-dev openssl-dev sshpass make
# RUN apk add py-crypto python-dev

# Install td4a
RUN pip install td4a==2.0.3

# Clear out extras
RUN rm -rf /var/cache/apk/*

# Start td4a
CMD [ "td4a-server" ]
