# Use an official Node.js image
FROM node:20

# Set the working directory in the container
WORKDIR /app

# Copy only package.json and package-lock.json first for caching layer
COPY package*.json /app/

# Install global Angular CLI and project dependencies
RUN npm install -g @angular/cli \
    && npm install

# Copy the rest of the application files
COPY . /app

# Expose the port the Angular app runs on
EXPOSE 4200

# Run the Angular development server
CMD ["ng", "serve", "--host", "0.0.0.0"]
