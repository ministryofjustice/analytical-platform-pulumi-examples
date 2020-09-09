import pulumi

import pulumi_aws as aws

from iam import eventRuleRole
from states import stateMachine

eventRule = aws.cloudwatch.EventRule(
    resource_name="state-machine",
    is_enabled=False,
    name="state-machine",
    role_arn=eventRuleRole.arn,
    schedule_expression="rate(5 minutes)",
)

eventTarget = aws.cloudwatch.EventTarget(
    resource_name="state-machine",
    opts=pulumi.ResourceOptions(parent=eventRule),
    arn=stateMachine.arn,
    role_arn=eventRuleRole.arn,
    rule=eventRule.name,
)
