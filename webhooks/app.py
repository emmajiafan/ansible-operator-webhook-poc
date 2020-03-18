import json
import base64

from flask import Flask, request

import kubernetes
from openshift.dynamic import DynamicClient


app = Flask(__name__)


class AdmissionReviewRequest:

    def __init__(self, uid=None,
                 kind=None,
                 resource=None,
                 requestKind=None,
                 requestResource=None,
                 name=None,
                 namespace=None,
                 operation=None,
                 userInfo=None,
                 object_=None,
                 oldObject=None,
                 dryRun=None,
                 options=None):
        self.uid = uid
        self.kind = kind
        self.resource = resource
        self.requestKind = requestKind
        self.requestResource = requestResource
        self.name = name
        self.namespace = namespace
        self.operation = operation
        self.userInfo = userInfo
        self.object_ = object_
        self.oldObject = oldObject
        self.dryRun = dryRun
        self.options = options

        self.allowed = False
        self.status = None
        self.patches = []

    @classmethod
    def from_json(cls, data):
        if isinstance(data, str):
            data = json.loads(data)
        data['object_'] = data['object']
        del data['object']
        return cls(**data)

    def response_json(self):
        return {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": self.uid,
                "allowed": self.allowed,
                "status": self.status,
                "patchType": "JSONPatch" if self.patches else None,
                "patch": base64.b64encode(json.dumps(self.patches)) if self.patches else None
            }
        }


@app.route('/mutating', methods=["POST"])
def mutate():
    review = AdmissionReviewRequest.from_json(request.json['request'])
    client = DynamicClient(kubernetes.config.new_client_from_config())
    v1_secrets = client.resources.get(api_version='v1', kind='Secret')
    v1_secrets.get(namespace=review.namespace)
    review.allowed = True
    return review.response_json()


@app.route('/validating', methods=["POST"])
def validate():
    review = AdmissionReviewRequest.from_json(request.json['request'])
    client = DynamicClient(kubernetes.config.new_client_from_config())
    v1_configmaps = client.resources.get(api_version='v1', kind='ConfigMap')
    v1_configmaps.get(namespace=review.namespace)
    review.allowed = True
    return review.response_json()


if __name__ == '__main__':
    app.run()
