# Use the official Nginx image as the base image
FROM nginx:latest

# Remove the default Nginx configuration file
RUN rm /etc/nginx/nginx.conf

# Copy the development nginx.conf file (you can change this based on your needs)
COPY ./dev/nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for HTTP
EXPOSE 80

# Command to start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
