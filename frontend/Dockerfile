# Use highly secure & dev-friendly image
FROM node:20-bookworm-slim

# Set work directory
WORKDIR /app

# Copy package files and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy frontend source files
COPY frontend/ ./

# Expose React port
EXPOSE 3000

# Start React development server
CMD ["npm", "start"]
