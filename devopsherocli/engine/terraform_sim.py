"""In-memory Terraform IaC Simulator for DevOpsHeroCLI."""
from __future__ import annotations

from typing import Dict, List, Set


class TerraformSimulator:
    """Simulates Terraform CLI workflows in memory."""

    def __init__(self):
        self.initialized: bool = False
        self.state_resources: Set[str] = set()
        self.planned_resources: Set[str] = set()
        self.outputs: Dict[str, str] = {}
        self.reset_default_state()

    def reset_default_state(self):
        self.initialized = False
        self.state_resources = {
            "aws_vpc.main",
            "aws_subnet.public_a",
            "aws_security_group.web",
        }
        self.planned_resources = {
            "aws_s3_bucket.app_storage",
            "aws_instance.api_server",
        }
        self.outputs = {
            "vpc_id": "vpc-0987654321fedcba0",
            "web_security_group_id": "sg-0123456789abcdef0",
        }

    def init(self, args: List[str]) -> str:
        self.initialized = True
        return (
            "Initializing the backend...\n"
            "Initializing provider plugins...\n"
            "- Finding hashicorp/aws versions matching \"~> 5.0\"...\n"
            "- Installing hashicorp/aws v5.42.0...\n"
            "- Installed hashicorp/aws v5.42.0 (signed by HashiCorp)\n\n"
            "Terraform has been successfully initialized!\n\n"
            "You may now begin working with Terraform. Try running \"terraform plan\" to see\n"
            "any changes that are required for your infrastructure."
        )

    def validate(self, args: List[str]) -> str:
        return "Success! The configuration is valid."

    def fmt(self, args: List[str]) -> str:
        if "-check" in args:
            return ""
        return "main.tf\nvariables.tf\noutputs.tf"

    def plan(self, args: List[str]) -> str:
        if not self.initialized:
            return "Error: Could not satisfy plugin requirements\nRun 'terraform init' to install required providers."

        return (
            "Terraform used the selected providers to generate the following execution plan.\n"
            "Resource actions are indicated with the following symbols:\n"
            "  + create\n\n"
            "Terraform will perform the following actions:\n\n"
            "  # aws_s3_bucket.app_storage will be created\n"
            "  + resource \"aws_s3_bucket\" \"app_storage\" {\n"
            "      + arn                         = (known after apply)\n"
            "      + bucket                      = \"company-app-production-data\"\n"
            "      + id                          = (known after apply)\n"
            "    }\n\n"
            "  # aws_instance.api_server will be created\n"
            "  + resource \"aws_instance\" \"api_server\" {\n"
            "      + ami                          = \"ami-0c55b159cbfafe1f0\"\n"
            "      + instance_type                 = \"t3.micro\"\n"
            "      + id                           = (known after apply)\n"
            "    }\n\n"
            "Plan: 2 to add, 0 to change, 0 to destroy."
        )

    def apply(self, args: List[str]) -> str:
        if not self.initialized:
            return "Error: Could not satisfy plugin requirements\nRun 'terraform init' to install required providers."

        auto_approve = "-auto-approve" in args
        self.state_resources.update(self.planned_resources)
        self.outputs["s3_bucket_arn"] = "arn:aws:s3:::company-app-production-data"
        self.outputs["api_server_ip"] = "54.210.12.34"

        return (
            "aws_s3_bucket.app_storage: Creating...\n"
            "aws_s3_bucket.app_storage: Creation complete after 2s [id=company-app-production-data]\n"
            "aws_instance.api_server: Creating...\n"
            "aws_instance.api_server: Creation complete after 12s [id=i-01a2b3c4d5e6f7890]\n\n"
            "Apply complete! Resources: 2 added, 0 changed, 0 destroyed.\n\n"
            "Outputs:\n\n"
            "api_server_ip = \"54.210.12.34\"\n"
            "s3_bucket_arn = \"arn:aws:s3:::company-app-production-data\"\n"
            "vpc_id = \"vpc-0987654321fedcba0\""
        )

    def show(self, args: List[str]) -> str:
        lines = ["# Current Terraform State:"]
        for res in sorted(self.state_resources):
            lines.append(f"# {res}:")
            lines.append(f"resource \"{res.split('.')[0]}\" \"{res.split('.')[1]}\" {{")
            lines.append(f"    id = \"{abs(hash(res)) % 1000000000}\"")
            lines.append("}\n")
        return "\n".join(lines).strip()

    def state_cmd(self, args: List[str]) -> str:
        if not args:
            return "usage: terraform state <subcommand> [options] [args]"
        sub = args[0]
        if sub == "list":
            return "\n".join(sorted(self.state_resources))
        elif sub == "show" and len(args) > 1:
            target = args[1]
            if target in self.state_resources:
                parts = target.split(".", 1)
                r_type = parts[0]
                r_name = parts[1] if len(parts) > 1 else "default"
                r_id = abs(hash(target)) % 1000000000
                return (
                    f"# {target}:\n"
                    f'resource "{r_type}" "{r_name}" {{\n'
                    f'    id = "{r_id}"\n'
                    f'}}'
                )
            return f"No instance found for the given address: {target}"
        return f"terraform state: unsupported subcommand {sub}"

    def output_cmd(self, args: List[str]) -> str:
        if not args:
            lines = [f"{k} = \"{v}\"" for k, v in self.outputs.items()]
            return "\n".join(lines)
        target = args[0].strip("\"'")
        if target in self.outputs:
            if "-raw" in args:
                return self.outputs[target]
            return f"\"{self.outputs[target]}\""
        return f"Warning: No output found with name '{target}'"

    def destroy(self, args: List[str]) -> str:
        count = len(self.state_resources)
        self.state_resources.clear()
        self.outputs.clear()
        return f"Destroy complete! Resources: {count} destroyed."

    def execute(self, args: List[str]) -> str:
        if not args:
            return (
                "Usage: terraform [global options] <subcommand> [args]\n\n"
                "Common commands:\n"
                "    init          Prepare your working directory for other commands\n"
                "    validate      Check whether the configuration is valid\n"
                "    plan          Show changes required by the current configuration\n"
                "    apply         Create or update infrastructure\n"
                "    destroy       Destroy previously-created infrastructure\n"
                "    state         Advanced state management\n"
                "    output        Show output values from your root module\n"
                "    fmt           Reformat your configuration in the standard style"
            )

        sub = args[0]
        sub_args = args[1:]

        if sub in ["version", "-v", "--version"]:
            return "Terraform v1.8.2\non linux_amd64\n+ provider registry.terraform.io/hashicorp/aws v5.42.0"
        elif sub == "init":
            return self.init(sub_args)
        elif sub == "validate":
            return self.validate(sub_args)
        elif sub == "fmt":
            return self.fmt(sub_args)
        elif sub == "plan":
            return self.plan(sub_args)
        elif sub == "apply":
            return self.apply(sub_args)
        elif sub == "show":
            return self.show(sub_args)
        elif sub == "state":
            return self.state_cmd(sub_args)
        elif sub == "output":
            return self.output_cmd(sub_args)
        elif sub == "destroy":
            return self.destroy(sub_args)

        return f"Terraform has no command named \"{sub}\"."
