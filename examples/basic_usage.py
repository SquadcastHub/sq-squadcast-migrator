from pathlib import Path

from squadcastify.terraform.exporter import TerraformExporter
from squadcastify.terraform.models import (
    ServiceMaintainer,
    ServiceTag,
    SquadcastEscalationPolicy,
    SquadcastService,
    SquadcastTeam,
    SquadcastUser,
)


def main():
    # Initialize config manager
    output_dir = Path("terraform_output")
    provider_config = {
        "region": "${var.squadcast_region}",  # Use a variable for region (us or eu)
        "refresh_token": "${var.squadcast_refresh_token}",  # Use a variable for sensitive data
    }

    manager = TerraformExporter(output_dir, provider_config)

    # Create a team - terraform_name will be "engineering_team"
    team = SquadcastTeam(
        display_name="Engineering Team", description="Core engineering team"
    )
    manager.add_resource(team)

    # Create a user - terraform_name will be "jane_smith"
    user = SquadcastUser(
        email="jane.smith@example.com",
        first_name="Jane",
        last_name="Smith",
        role="admin",
        abilities={"manage-teams", "manage-users", "manage-api-tokens"},
    )
    manager.add_resource(user)

    # Create an escalation policy - terraform_name will be "default_escalation_policy"
    escalation_policy = SquadcastEscalationPolicy(
        display_name="Default Escalation Policy",
        team_id=team.terraform_id_reference,  # Reference the team
    )
    manager.add_resource(escalation_policy)

    # Create a service - terraform_name will be "api_service"
    service = SquadcastService(
        display_name="API Service",
        team_id=team.terraform_id_reference,  # Use ID reference
        escalation_policy_id=escalation_policy.terraform_id_reference,  # Use ID reference
        email_prefix="api-alerts",
        description="Main API service monitoring",
        maintainer=ServiceMaintainer(id=user.terraform_id_reference, type="user"),
        tags=[
            ServiceTag(key="environment", value="production"),
            ServiceTag(key="team", value="engineering"),
        ],
        alert_sources=["datadog", "prometheus"],
    )
    manager.add_resource(service)

    # Generate Terraform configuration files
    result = manager.export()

    if result["status"] == "success":
        print(f"Generated Terraform configuration in: {result['output_dir']}")
        print("Resource counts:", result["resource_counts"])
        print("\nGenerated Terraform names:")
        print(f"Team: {team.terraform_name}")
        print(f"User: {user.terraform_name}")
        print(f"Escalation Policy: {escalation_policy.terraform_name}")
        print(f"Service: {service.terraform_name}")
    else:
        print("Error generating configuration:", result["message"])


if __name__ == "__main__":
    main()
