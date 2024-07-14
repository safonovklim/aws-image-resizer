#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.app_stack import AwsImageAutoresizerStack

app = cdk.App()
AwsImageAutoresizerStack(app, "AwsImageAutoresizerStack")

app.synth()
