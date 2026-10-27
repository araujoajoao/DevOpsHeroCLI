"""In-memory AWS CLI Simulator for DevOpsHeroCLI."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class S3Bucket:
    name: str
    creation_date: str = "2026-01-15T12:00:00.000Z"
    objects: List[str] = field(default_factory=list)


@dataclass
class EC2Instance:
    instance_id: str
    instance_type: str
    state: str
    public_ip: str
    private_ip: str
    tags: Dict[str, str] = field(default_factory=dict)


class AwsSimulator:
    """Simulates AWS CLI operations in memory."""

    def __init__(self):
        self.account_id: str = "123456789012"
        self.region: str = "us-east-1"
        self.caller_arn: str = "arn:aws:iam::123456789012:user/devops-hero"
        self.buckets: Dict[str, S3Bucket] = {}
        self.instances: Dict[str, EC2Instance] = {}
        self.iam_users: Set[str] = set()
        self.lambda_functions: List[str] = []
        self.reset_default_state()

    def reset_default_state(self):
        self.account_id = "123456789012"
        self.region = "us-east-1"
        self.buckets = {
            "company-app-artifacts": S3Bucket("company-app-artifacts", objects=["v1.0.0.tar.gz", "v1.1.0.tar.gz"]),
            "company-audit-logs": S3Bucket("company-audit-logs", objects=["2026-10-access.log"]),
        }
        self.instances = {
            "i-0a1b2c3d4e5f67890": EC2Instance(
                instance_id="i-0a1b2c3d4e5f67890",
                instance_type="t3.medium",
                state="running",
                public_ip="54.210.89.12",
                private_ip="10.0.1.45",
                tags={"Name": "web-prod-01", "Environment": "production"},
            ),
            "i-0f9e8d7c6b5a43210": EC2Instance(
                instance_id="i-0f9e8d7c6b5a43210",
                instance_type="t3.small",
                state="stopped",
                public_ip="",
                private_ip="10.0.1.78",
                tags={"Name": "batch-worker-staging", "Environment": "staging"},
            ),
        }
        self.iam_users = {"devops-hero", "ci-deployer", "audit-reader"}
        self.lambda_functions = ["image-resizer-prod", "webhook-processor"]

    def s3_cmd(self, args: List[str]) -> str:
        if not args:
            return "usage: aws s3 <Command> [<Arg> ...]"

        sub = args[0]
        sub_args = args[1:]

        if sub == "ls":
            if not sub_args or sub_args[0] == "":
                lines = []
                for b_name, b in self.buckets.items():
                    lines.append(f"{b.creation_date[:10]} 12:00:00 {b_name}")
                return "\n".join(lines)

            target = sub_args[0].replace("s3://", "").rstrip("/")
            if target in self.buckets:
                b = self.buckets[target]
                lines = []
                for obj in b.objects:
                    lines.append(f"2026-10-27 10:00:00      142857 {obj}")
                return "\n".join(lines) if lines else ""
            return "fatal error: An error occurred (NoSuchBucket) when calling the ListObjectsV2 operation: The specified bucket does not exist"

        elif sub == "mb":
            if not sub_args:
                return "usage: aws s3 mb <S3Uri>"
            b_name = sub_args[0].replace("s3://", "").strip()
            self.buckets[b_name] = S3Bucket(name=b_name, objects=[])
            return f"make_bucket: s3://{b_name}"

        elif sub == "cp":
            if len(sub_args) < 2:
                return "usage: aws s3 cp <LocalPath> <S3Uri> or <S3Uri> <LocalPath>"
            src, dest = sub_args[0], sub_args[1]
            if dest.startswith("s3://"):
                b_name = dest.replace("s3://", "").split("/")[0]
                filename = src.split("/")[-1]
                if b_name in self.buckets:
                    self.buckets[b_name].objects.append(filename)
                return f"upload: {src} to {dest}"
            return f"download: {src} to {dest}"

        elif sub == "rm":
            if not sub_args:
                return "usage: aws s3 rm <S3Uri>"
            target = sub_args[0].replace("s3://", "")
            parts = target.split("/", 1)
            b_name = parts[0]
            if len(parts) > 1 and b_name in self.buckets:
                obj_name = parts[1]
                if obj_name in self.buckets[b_name].objects:
                    self.buckets[b_name].objects.remove(obj_name)
                    return f"delete: s3://{target}"
            return f"delete: s3://{target}"

        return f"aws s3: unknown subcommand '{sub}'"

    def ec2_cmd(self, args: List[str]) -> str:
        if not args:
            return "usage: aws ec2 <Command> [<Arg> ...]"

        sub = args[0]
        if sub in ["describe-instances", "describe_instances"]:
            reservations = []
            for inst in self.instances.values():
                reservations.append({
                    "Instances": [{
                        "InstanceId": inst.instance_id,
                        "InstanceType": inst.instance_type,
                        "State": {"Name": inst.state},
                        "PublicIpAddress": inst.public_ip,
                        "PrivateIpAddress": inst.private_ip,
                        "Tags": [{"Key": k, "Value": v} for k, v in inst.tags.items()],
                    }]
                })
            return json.dumps({"Reservations": reservations}, indent=2)

        elif sub == "start-instances":
            inst_ids = [a for a in args[1:] if a.startswith("i-")]
            for i_id in inst_ids:
                if i_id in self.instances:
                    self.instances[i_id].state = "running"
                    self.instances[i_id].public_ip = "54.210.99.88"
            return json.dumps({"StartingInstances": [{"InstanceId": i, "CurrentState": {"Name": "running"}} for i in inst_ids]}, indent=2)

        elif sub == "stop-instances":
            inst_ids = [a for a in args[1:] if a.startswith("i-")]
            for i_id in inst_ids:
                if i_id in self.instances:
                    self.instances[i_id].state = "stopped"
                    self.instances[i_id].public_ip = ""
            return json.dumps({"StoppingInstances": [{"InstanceId": i, "CurrentState": {"Name": "stopped"}} for i in inst_ids]}, indent=2)

        elif sub == "describe-vpcs":
            return json.dumps({
                "Vpcs": [{
                    "VpcId": "vpc-0123456789abcdef0",
                    "CidrBlock": "10.0.0.0/16",
                    "State": "available",
                    "IsDefault": True
                }]
            }, indent=2)

        return f"aws ec2: unknown subcommand '{sub}'"

    def iam_cmd(self, args: List[str]) -> str:
        if not args:
            return "usage: aws iam <Command> [<Arg> ...]"

        sub = args[0]
        if sub == "list-users":
            users = [{"UserName": u, "UserId": f"AIDA{abs(hash(u))%10000000000:010d}", "Arn": f"arn:aws:iam::{self.account_id}:user/{u}"} for u in sorted(self.iam_users)]
            return json.dumps({"Users": users}, indent=2)

        elif sub == "create-user":
            username = ""
            if "--user-name" in args:
                username = args[args.index("--user-name") + 1]
            elif len(args) > 1 and not args[1].startswith("-"):
                username = args[1]

            if username:
                self.iam_users.add(username)
                return json.dumps({
                    "User": {
                        "UserName": username,
                        "UserId": f"AIDA{abs(hash(username))%10000000000:010d}",
                        "Arn": f"arn:aws:iam::{self.account_id}:user/{username}",
                    }
                }, indent=2)
            return "error: --user-name required"

        elif sub == "attach-user-policy":
            return ""

        elif sub == "list-roles":
            return json.dumps({
                "Roles": [
                    {"RoleName": "ecsTaskExecutionRole", "Arn": f"arn:aws:iam::{self.account_id}:role/ecsTaskExecutionRole"},
                    {"RoleName": "lambda-s3-execution-role", "Arn": f"arn:aws:iam::{self.account_id}:role/lambda-s3-execution-role"},
                ]
            }, indent=2)

        return f"aws iam: unknown subcommand '{sub}'"

    def sts_cmd(self, args: List[str]) -> str:
        if args and args[0] in ["get-caller-identity", "get_caller_identity"]:
            return json.dumps({
                "UserId": "AIDAI3V7DEVOPSEXAMPLE",
                "Account": self.account_id,
                "Arn": self.caller_arn
            }, indent=2)
        return "usage: aws sts get-caller-identity"

    def lambda_cmd(self, args: List[str]) -> str:
        if args and args[0] == "list-functions":
            return json.dumps({
                "Functions": [
                    {"FunctionName": f, "Runtime": "python3.11", "Handler": "handler.lambda_handler", "MemorySize": 256}
                    for f in self.lambda_functions
                ]
            }, indent=2)
        return "usage: aws lambda list-functions"

    def configure_cmd(self, args: List[str]) -> str:
        if args and args[0] == "list":
            return (
                f"      Name                    Value             Type    Location\n"
                f"      ----                    -----             ----    --------\n"
                f"   profile                <not set>             None    None\n"
                f"access_key     ****************A1B2      config-file    ~/.aws/config\n"
                f"secret_key     ****************X8Y9      config-file    ~/.aws/config\n"
                f"    region                {self.region}      config-file    ~/.aws/config"
            )
        return "AWS CLI configured with mock profile 'default'."

    def execute(self, args: List[str]) -> str:
        if not args:
            return (
                "usage: aws [options] <command> <subcommand> [parameters]\n"
                "To see help text, you can run:\n"
                "  aws help\n"
                "  aws <command> help\n"
                "  aws <command> <subcommand> help"
            )

        if args[0] == "--version":
            return "aws-cli/2.15.22 Python/3.11.8 Linux/6.8.0-generic exe/x86_64"

        service = args[0]
        service_args = args[1:]

        if service == "s3":
            return self.s3_cmd(service_args)
        elif service == "ec2":
            return self.ec2_cmd(service_args)
        elif service == "iam":
            return self.iam_cmd(service_args)
        elif service == "sts":
            return self.sts_cmd(service_args)
        elif service == "lambda":
            return self.lambda_cmd(service_args)
        elif service == "configure":
            return self.configure_cmd(service_args)

        return "aws: error: argument command: Invalid choice, valid choices are: s3 | ec2 | iam | sts | lambda | configure"
