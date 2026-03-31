FROM nginx:alpine

# Copy custom nginx configuration to listen on 8080 and support envsubst
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy all static assets into the Nginx public directory
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

# Expose port 8080 as expected by Cloud Run
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
