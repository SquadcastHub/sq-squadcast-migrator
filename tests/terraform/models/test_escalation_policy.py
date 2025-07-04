"""Tests for the EscalationPolicy Terraform model."""

import unittest
from squadcastify.terraform.models import (
    SquadcastEscalationPolicy,
    Rule,
    Target,
    Repeat,
    RoundRobin,
    Rotation,
    EntityOwner
)

class TestSquadcastEscalationPolicy(unittest.TestCase):
    """Test cases for SquadcastEscalationPolicy model."""
    
    def test_escalation_policy_to_hcl_basic(self):
        """Test basic HCL generation for an escalation policy with simple rule."""
        escalation_policy = SquadcastEscalationPolicy(
            terraform_name="simple_policy",
            name="Simple Escalation Policy",
            team_id="${squadcast_team.test_team.id}",
            entity_owner=EntityOwner(
                id="${squadcast_user.owner.id}",
                type="user"
            ),
            rules=[
                Rule(
                    delay_minutes=5,
                    targets=[
                        Target(
                            id="${squadcast_user.user1.id}",
                            type="user"
                        )
                    ]
                )
            ]
        )
        
        expected_hcl = (
            'resource "squadcast_escalation_policy" "simple_policy" {\n'
            '  name = "Simple Escalation Policy"\n'
            '  team_id = "${squadcast_team.test_team.id}"\n'
            '  rules {\n'
            '    delay_minutes = 5\n'
            '    targets {\n'
            '      id = "${squadcast_user.user1.id}"\n'
            '      type = "user"\n'
            '    }\n'
            '  }\n'
            '  entity_owner {\n'
            '    id = "${squadcast_user.owner.id}"\n'
            '    type = "user"\n'
            '  }\n'
            '}'
        )
        
        self.assertEqual(escalation_policy.to_hcl(), expected_hcl)
    
    def test_escalation_policy_to_hcl_complex(self):
        """Test HCL generation for an escalation policy with complex rules."""
        escalation_policy = SquadcastEscalationPolicy(
            terraform_name="complex_policy",
            name="Complex Escalation Policy",
            team_id="${squadcast_team.test_team.id}",
            description="A complex policy with multiple rules",
            entity_owner=EntityOwner(
                id="${squadcast_user.owner.id}",
                type="user"
            ),
            rules=[
                Rule(
                    delay_minutes=5,
                    targets=[
                        Target(
                            id="${squadcast_user.user1.id}",
                            type="user"
                        )
                    ],
                    notification_channels=["Email", "SMS"]
                ),
                Rule(
                    delay_minutes=15,
                    targets=[
                        Target(
                            id="${squadcast_squad.squad1.id}",
                            type="squad"
                        ),
                        Target(
                            id="${squadcast_schedule_v2.schedule1.id}",
                            type="schedulev2"
                        )
                    ],
                    repeat=Repeat(
                        times=3,
                        delay_minutes=10
                    ),
                    round_robin=RoundRobin(
                        enabled=True,
                    )
                )
            ],
            repeat=Repeat(
                times=2,
                delay_minutes=30
            )
        )
        
        # The exact expected HCL is quite complex, so we'll check for key elements
        hcl = escalation_policy.to_hcl()
        
        # Check for basic fields
        self.assertIn('resource "squadcast_escalation_policy" "complex_policy" {', hcl)
        self.assertIn('  name = "Complex Escalation Policy"', hcl)
        self.assertIn('  team_id = "${squadcast_team.test_team.id}"', hcl)
        self.assertIn('  description = "A complex policy with multiple rules"', hcl)
        
        # Check for first rule
        self.assertIn('  rules {', hcl)
        self.assertIn('    delay_minutes = 5', hcl)
        self.assertIn('    targets {', hcl)
        self.assertIn('      id = "${squadcast_user.user1.id}"', hcl)
        self.assertIn('      type = "user"', hcl)
        self.assertIn('    notification_channels = ["Email", "SMS"]', hcl)
        
        # Check for second rule with more complex structures
        self.assertIn('    delay_minutes = 15', hcl)
        self.assertIn('    targets {', hcl)
        self.assertIn('      id = "${squadcast_squad.squad1.id}"', hcl)
        self.assertIn('      type = "squad"', hcl)
        self.assertIn('    targets {', hcl)
        self.assertIn('      id = "${squadcast_schedule_v2.schedule1.id}"', hcl)
        self.assertIn('      type = "schedulev2"', hcl)
        
        # Check for repeat config
        self.assertIn('    repeat {', hcl)
        self.assertIn('      times = 3', hcl)
        self.assertIn('      delay_minutes = 10', hcl)
        
        # Check for round robin
        self.assertIn('    round_robin {', hcl)
        self.assertIn('      enabled = true', hcl)
        
        # Check for global repeat
        self.assertIn('  repeat {', hcl)
        self.assertIn('    times = 2', hcl)
        self.assertIn('    delay_minutes = 30', hcl)
        
        # Check for entity owner
        self.assertIn('  entity_owner {', hcl)
        self.assertIn('    id = "${squadcast_user.owner.id}"', hcl)
        self.assertIn('    type = "user"', hcl)
    
    def test_auto_terraform_name(self):
        """Test auto-generation of terraform_name."""
        policy = SquadcastEscalationPolicy(
            name="Auto Name Policy",
            team_id="team123",
            entity_owner=EntityOwner(id="user1", type="user"),
            rules=[Rule(delay_minutes=5, targets=[Target(id="user1", type="user")])]
        )
        
        # Check that terraform_name was auto-generated
        self.assertIsNotNone(policy.terraform_name)
        self.assertTrue(policy.terraform_name.startswith("auto_name_policy"))
    
    def test_terraform_resource_type(self):
        """Test the terraform_resource_type property."""
        policy = SquadcastEscalationPolicy(
            terraform_name="test_policy",
            name="Test Policy",
            team_id="team123",
            entity_owner=EntityOwner(id="user1", type="user"),
            rules=[Rule(delay_minutes=5, targets=[Target(id="user1", type="user")])]
        )
        
        self.assertEqual(policy.terraform_resource_type, "squadcast_escalation_policy")


if __name__ == "__main__":
    unittest.main()
