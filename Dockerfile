# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV BOT_TOKEN=${BOT_TOKEN}
ENV CHAT_ID=${CHAT_ID}

# Command to run the bot
CMD ["python", "bin_reminder_bot_listener.py"]
