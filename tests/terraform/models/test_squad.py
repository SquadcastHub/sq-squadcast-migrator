"""Tests for the Squad Terraform model."""

import unittest
from squadcastify.terraform.models import SquadcastSquad, SquadMember

class TestSquadcastSquad(unittest.TestCase):
    """Test cases for SquadcastSquad model."""
    
    def test_squad_to_hcl_with_members(self):
        """Test HCL generation for a squad with members."""
        squad = SquadcastSquad(
            terraform_name="test_squad_with_members",
            name="Test Squad With Members",
            team_id="${squadcast_team.test_team.id}",
            members=[
                SquadMember(user_id="${squadcast_user.user1.id}"),
                SquadMember(user_id="${squadcast_user.user2.id}")
            ]
        )
        
        expected_hcl = (
            'resource "squadcast_squad" "test_squad_with_members" {\n'
            '  name = "Test Squad With Members"\n'
            '  team_id = "${squadcast_team.test_team.id}"\n'
            '  members {\n'
            '    user_id = "${squadcast_user.user1.id}"\n'
            '  }\n'
            '  members {\n'
            '    user_id = "${squadcast_user.user2.id}"\n'
            '  }\n'
            '}'
        )
        
        self.assertEqual(squad.to_hcl(), expected_hcl)
    
    def test_auto_terraform_name(self):
        """Test auto-generation of terraform_name."""
        squad = SquadcastSquad(
            name="Auto Name Squad",
            team_id="team123"
        )
        
        # Check that terraform_name was auto-generated
        self.assertIsNotNone(squad.terraform_name)
        self.assertTrue(squad.terraform_name.startswith("auto_name_squad"))
    
    def test_terraform_resource_type(self):
        """Test the terraform_resource_type property."""
        squad = SquadcastSquad(
            terraform_name="test_squad",
            name="Test Squad",
            team_id="${squadcast_team.test_team.id}"
        )
        
        self.assertEqual(squad.terraform_resource_type, "squadcast_squad")


if __name__ == "__main__":
    unittest.main()
