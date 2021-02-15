import json

import pulumi
import pulumi_aws as aws

from iam import eventRuleRole
from states import stateMachine

eventRule = aws.cloudwatch.EventRule(
    resource_name="state-machine",
    is_enabled=False,
    name="state-machine",
    role_arn=eventRuleRole.arn,
    schedule_expression="rate(1 day)",
)

eventTarget = aws.cloudwatch.EventTarget(
    resource_name="state-machine",
    opts=pulumi.ResourceOptions(parent=eventRule),
    arn=stateMachine.arn,
    input=json.dumps(
        {
            "DatabaseQueryString": "CREATE DATABASE IF NOT EXISTS awards_processed;",
            "TableQueryStrings": [
                {
                    "Drop": "DROP TABLE IF EXISTS awards_processed.id;",
                    "Create": (
                        "CREATE TABLE awards_processed.id AS "
                        "SELECT id "
                        "FROM awards.awards;"
                    ),
                },
                {
                    "Drop": "DROP TABLE IF EXISTS awards_processed.num_awards;",
                    "Create": (
                        "CREATE TABLE awards_processed.num_awards AS "
                        "SELECT num_awards "
                        "FROM awards.awards;"
                    ),
                },
            ],
        }
    ),
    role_arn=eventRuleRole.arn,
    rule=eventRule.name,
)
