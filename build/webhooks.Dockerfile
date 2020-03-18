FROM python:3

RUN pip install flask pyopenssl openshift pdbpp

ENV HOME=/app \
    KUBECONFIG=/app/.kube/config

WORKDIR /app

COPY webhooks /app

ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--cert", "tls/tls.crt", "--key", "tls/tls.key"]
