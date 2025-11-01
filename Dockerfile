FROM public.ecr.aws/lambda/python:3.11

# Install dependencies into the Lambda task root so they are on PYTHONPATH
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application code into the Lambda task root
COPY . ${LAMBDA_TASK_ROOT}

# Set the handler (module.function)
CMD ["lambda_handler.handler"]
