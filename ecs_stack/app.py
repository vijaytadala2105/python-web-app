#!/usr/bin/env python3
import os

import aws_cdk as cdk

from ecs_stack.ecs_stack_stack import EcsStackStack


app = cdk.App()
EcsStackStack(app, "EcsStackStack",
          env=cdk.Environment(account='880729935461', region='us-east-1')    
     )

app.synth()
