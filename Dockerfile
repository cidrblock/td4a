FROM python:2.7.14-alpine3.6

# Update the packages
RUN apk update

# Install the ansible dependancies
RUN apk add gcc libffi-dev musl-dev openssl-dev sshpass make
# RUN apk add py-crypto python-dev

# Install td4a
RUN pip install td4a==1.7

# Clear out extras
RUN rm -rf /var/cache/apk/*

# Start td4a
CMD [ "td4a-server" ]
