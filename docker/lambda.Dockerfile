# node builder image
FROM node:20-slim as builder 

# always good practice to upgrade our package manager index and upgrade all packages
RUN apt-get update && apt-get upgrade -y

# yarn is already installed in the node image, so no need to install it

# set the working directory to be /app (create it since it doesn't exist)
WORKDIR /app

# copy all our local files (this will be ran from the context provided when running docker build)
COPY . .

# install our dependencies 
RUN yarn install
# build the production react application
RUN yarn build

# create a new stage for our lambda runtime image
FROM public.ecr.aws/lambda/python:3.11

# copy in our requirements
COPY requirements.txt .

# ensure we don't have any old pip versions/security issues
RUN pip install -U pip setuptools
RUN pip install -r requirements.txt

# Copy the api directory to /var/task
COPY ./api ${LAMBDA_TASK_ROOT}/api

# copy the build directory from the builder stage
COPY --from=builder /app/build ${LAMBDA_TASK_ROOT}/build

# Use the full module path
CMD ["api.main.handler"]
