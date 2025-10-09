import aws_cdk as core
import aws_cdk.assertions as assertions

from ecs_stack.ecs_stack_stack import EcsStackStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ecs_stack/ecs_stack_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EcsStackStack(app, "ecs-stack")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
